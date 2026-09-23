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