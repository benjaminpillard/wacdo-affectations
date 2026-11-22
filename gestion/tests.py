from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Affectation, Collaborateur, Fonction, Restaurant


def creer_administrateur():
    return Collaborateur.objects.create_user(
        email="admin@wacdo.test",
        password="MotDePasseTest123",
        first_name="Ada",
        last_name="Ministrateur",
        date_premiere_embauche=date(2020, 1, 1),
        administrateur=True,
    )


def creer_utilisateur_standard():
    return Collaborateur.objects.create_user(
        email="standard@wacdo.test",
        password="MotDePasseTest123",
        first_name="Stan",
        last_name="Dard",
        date_premiere_embauche=date(2021, 1, 1),
        administrateur=False,
    )


class ModeleAffectationTests(TestCase):
    """Tests fonctionnels sur les règles métier du modèle Affectation."""

    def setUp(self):
        self.collaborateur = creer_administrateur()
        self.restaurant = Restaurant.objects.create(
            nom="Wacdo Test", adresse="1 rue du Test", code_postal="75001", ville="Paris"
        )
        self.fonction = Fonction.objects.create(intitule_poste="Équipier polyvalent")

    def test_affectation_sans_date_de_fin_est_valide(self):
        affectation = Affectation(
            collaborateur=self.collaborateur,
            restaurant=self.restaurant,
            poste=self.fonction,
            debut=date.today(),
            fin=None,
        )
        affectation.full_clean()
        affectation.save()
        self.assertIsNone(affectation.fin)

    def test_date_fin_anterieure_a_debut_est_refusee(self):
        affectation = Affectation(
            collaborateur=self.collaborateur,
            restaurant=self.restaurant,
            poste=self.fonction,
            debut=date.today(),
            fin=date.today() - timedelta(days=1),
        )
        with self.assertRaises(Exception):
            affectation.full_clean()


class RestaurantVueTests(TestCase):
    """Tests fonctionnels et de sécurité sur la gestion des restaurants."""

    def setUp(self):
        self.administrateur = creer_administrateur()
        self.standard = creer_utilisateur_standard()

    def test_creation_restaurant_avec_code_postal_invalide_est_refusee(self):
        self.client.force_login(self.administrateur)
        reponse = self.client.post(
            reverse("restaurant_creer"),
            {
                "nom": "Wacdo Test",
                "adresse": "1 rue du Test",
                "code_postal": "750",
                "ville": "Paris",
            },
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(Restaurant.objects.count(), 0)

    def test_creation_restaurant_valide(self):
        self.client.force_login(self.administrateur)
        reponse = self.client.post(
            reverse("restaurant_creer"),
            {
                "nom": "Wacdo Test",
                "adresse": "1 rue du Test",
                "code_postal": "75001",
                "ville": "Paris",
            },
        )
        self.assertRedirects(reponse, reverse("restaurant_liste"))
        self.assertEqual(Restaurant.objects.count(), 1)

    def test_utilisateur_non_administrateur_ne_peut_pas_acceder_a_la_liste(self):
        self.client.force_login(self.standard)
        reponse = self.client.get(reverse("restaurant_liste"))
        self.assertEqual(reponse.status_code, 403)

    def test_utilisateur_non_connecte_est_redirige_vers_la_connexion(self):
        reponse = self.client.get(reverse("restaurant_liste"))
        self.assertRedirects(reponse, f"{reverse('connexion')}?next={reverse('restaurant_liste')}")


class InterfaceTests(TestCase):
    """Tests d'interface : les pages principales s'affichent avec le bon gabarit."""

    def setUp(self):
        self.administrateur = creer_administrateur()
        self.client.force_login(self.administrateur)

    def test_page_accueil_affiche_le_menu(self):
        reponse = self.client.get(reverse("accueil"))
        self.assertEqual(reponse.status_code, 200)
        self.assertTemplateUsed(reponse, "gestion/accueil.html")
        self.assertContains(reponse, "Menu principal")

    def test_page_connexion_affiche_un_formulaire(self):
        self.client.logout()
        reponse = self.client.get(reverse("connexion"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "<form")

class CollaborateurVueTests(TestCase):
    """Tests fonctionnels et de sécurité sur la gestion des collaborateurs."""

    def setUp(self):
        self.administrateur = creer_administrateur()
        self.client.force_login(self.administrateur)

    def donnees(self, **surcharges):
        donnees = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@wacdo.test",
            "date_premiere_embauche": "2024-03-01",
            "mot_de_passe": "",
            "mot_de_passe_confirmation": "",
        }
        donnees.update(surcharges)
        return donnees

    def test_collaborateur_standard_sans_mot_de_passe(self):
        reponse = self.client.post(reverse("collaborateur_creer"), self.donnees())
        self.assertRedirects(reponse, reverse("collaborateur_liste"))
        collaborateur = Collaborateur.objects.get(email="jean.dupont@wacdo.test")
        self.assertFalse(collaborateur.has_usable_password())

    def test_administrateur_sans_mot_de_passe_est_refuse(self):
        reponse = self.client.post(
            reverse("collaborateur_creer"), self.donnees(administrateur="on")
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(Collaborateur.objects.filter(email="jean.dupont@wacdo.test").exists())

    def test_mot_de_passe_administrateur_est_hache(self):
        self.client.post(
            reverse("collaborateur_creer"),
            self.donnees(
                administrateur="on",
                mot_de_passe="Wacdo-Secret-2026",
                mot_de_passe_confirmation="Wacdo-Secret-2026",
            ),
        )
        collaborateur = Collaborateur.objects.get(email="jean.dupont@wacdo.test")
        self.assertTrue(collaborateur.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(collaborateur.check_password("Wacdo-Secret-2026"))

    def test_email_invalide_est_refuse(self):
        reponse = self.client.post(
            reverse("collaborateur_creer"), self.donnees(email="pas-un-email")
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(Collaborateur.objects.count(), 1)

    def test_liste_des_non_affectes(self):
        restaurant = Restaurant.objects.create(
            nom="Wacdo", adresse="1 rue", code_postal="69001", ville="Lyon"
        )
        fonction = Fonction.objects.create(intitule_poste="Manager")
        Affectation.objects.create(
            collaborateur=self.administrateur,
            restaurant=restaurant,
            poste=fonction,
            debut=date(2024, 1, 1),
        )
        libre = creer_utilisateur_standard()
        reponse = self.client.get(reverse("collaborateur_non_affectes"))
        self.assertIn(libre, reponse.context["collaborateurs"])
        self.assertNotIn(self.administrateur, reponse.context["collaborateurs"])


class ChangementPosteTests(TestCase):
    def setUp(self):
        self.administrateur = creer_administrateur()
        self.client.force_login(self.administrateur)
        self.restaurant = Restaurant.objects.create(
            nom="Wacdo", adresse="1 rue", code_postal="69001", ville="Lyon"
        )
        self.equipier = Fonction.objects.create(intitule_poste="Équipier polyvalent")
        self.manager = Fonction.objects.create(intitule_poste="Manager")
        self.affectation = Affectation.objects.create(
            collaborateur=self.administrateur,
            restaurant=self.restaurant,
            poste=self.equipier,
            debut=date(2024, 1, 1),
        )
        self.url = reverse("affectation_changer_poste", args=[self.affectation.pk])

    def poster(self, fin, debut):
        return self.client.post(
            self.url,
            {
                "fin_poste_actuel": fin,
                "nouveau_restaurant": self.restaurant.pk,
                "nouveau_poste": self.manager.pk,
                "nouveau_debut": debut,
            },
        )

    def test_changement_de_poste_cloture_et_cree(self):
        reponse = self.poster("2025-06-30", "2025-07-01")
        self.assertRedirects(
            reponse, reverse("collaborateur_detail", args=[self.administrateur.pk])
        )
        self.affectation.refresh_from_db()
        self.assertEqual(self.affectation.fin, date(2025, 6, 30))
        self.assertTrue(
            Affectation.objects.filter(poste=self.manager, fin__isnull=True).exists()
        )

    def test_fin_avant_debut_du_poste_actuel_affiche_une_erreur(self):
        reponse = self.poster("2023-12-31", "2024-01-01")
        self.assertEqual(reponse.status_code, 200)
        self.affectation.refresh_from_db()
        self.assertIsNone(self.affectation.fin)
        self.assertEqual(Affectation.objects.count(), 1)


class RechercheAffectationTests(TestCase):
    def setUp(self):
        self.administrateur = creer_administrateur()
        self.client.force_login(self.administrateur)
        fonction = Fonction.objects.create(intitule_poste="Manager")
        lyon = Restaurant.objects.create(nom="A", adresse="1", code_postal="69001", ville="Lyon")
        paris = Restaurant.objects.create(nom="B", adresse="2", code_postal="75001", ville="Paris")
        for restaurant in (lyon, paris):
            Affectation.objects.create(
                collaborateur=self.administrateur,
                restaurant=restaurant,
                poste=fonction,
                debut=date(2024, 1, 1),
            )

    def test_recherche_par_ville(self):
        reponse = self.client.get(reverse("affectation_recherche"), {"ville": "lyon"})
        villes = [a.restaurant.ville for a in reponse.context["affectations"]]
        self.assertEqual(villes, ["Lyon"])

    def test_utilisateur_standard_ne_voit_pas_le_menu_de_gestion(self):
        self.client.force_login(creer_utilisateur_standard())
        reponse = self.client.get(reverse("accueil"))
        self.assertNotContains(reponse, reverse("affectation_recherche"))
        self.assertEqual(self.client.get(reverse("affectation_recherche")).status_code, 403)
