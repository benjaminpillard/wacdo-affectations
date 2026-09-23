from django import forms

from .models import Affectation, Collaborateur, Fonction, Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["nom", "adresse", "code_postal", "ville"]

    def clean_code_postal(self):
        code_postal = self.cleaned_data["code_postal"]
        if not code_postal.isdigit() or len(code_postal) != 5:
            raise forms.ValidationError("Le code postal doit contenir 5 chiffres.")
        return code_postal


class RestaurantRechercheForm(forms.Form):
    nom = forms.CharField(required=False)
    code_postal = forms.CharField(required=False)
    ville = forms.CharField(required=False)


class AffectationFiltreForm(forms.Form):
    poste = forms.ModelChoiceField(
        queryset=Fonction.objects.order_by("intitule_poste"),
        required=False,
        empty_label="Tous les postes",
    )
    debut = forms.DateField(
        label="Début à partir du",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class AffectationForm(forms.ModelForm):
    collaborateur = forms.ModelChoiceField(
        queryset=Collaborateur.objects.order_by("last_name", "first_name")
    )

    class Meta:
        model = Affectation
        fields = ["collaborateur", "poste", "debut", "fin"]
        widgets = {
            "debut": forms.DateInput(attrs={"type": "date"}),
            "fin": forms.DateInput(attrs={"type": "date"}),
        }


class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ["intitule_poste"]


class CollaborateurForm(forms.ModelForm):
    mot_de_passe = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    mot_de_passe_confirmation = forms.CharField(
        label="Confirmation du mot de passe", widget=forms.PasswordInput
    )

    class Meta:
        model = Collaborateur
        fields = [
            "first_name",
            "last_name",
            "email",
            "date_premiere_embauche",
            "administrateur",
        ]
        labels = {"first_name": "Prénom", "last_name": "Nom"}
        widgets = {
            "date_premiere_embauche": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Collaborateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Un collaborateur utilise déjà cet email.")
        return email

    def clean(self):
        donnees = super().clean()
        if donnees.get("mot_de_passe") != donnees.get("mot_de_passe_confirmation"):
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return donnees

    def save(self, commit=True):
        collaborateur = Collaborateur.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["mot_de_passe"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            date_premiere_embauche=self.cleaned_data["date_premiere_embauche"],
            administrateur=self.cleaned_data["administrateur"],
        )
        return collaborateur


class CollaborateurRechercheForm(forms.Form):
    nom = forms.CharField(required=False, label="Nom")
    prenom = forms.CharField(required=False, label="Prénom")
    email = forms.CharField(required=False)


class ChangementPosteForm(forms.Form):
    fin_poste_actuel = forms.DateField(
        label="Date de fin du poste actuel",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    nouveau_restaurant = forms.ModelChoiceField(
        label="Nouveau restaurant", queryset=Restaurant.objects.order_by("nom")
    )
    nouveau_poste = forms.ModelChoiceField(
        label="Nouveau poste", queryset=Fonction.objects.order_by("intitule_poste")
    )
    nouveau_debut = forms.DateField(
        label="Date de début du nouveau poste",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean(self):
        donnees = super().clean()
        fin = donnees.get("fin_poste_actuel")
        debut = donnees.get("nouveau_debut")
        if fin and debut and debut < fin:
            raise forms.ValidationError(
                "Le nouveau poste ne peut pas commencer avant la fin du poste actuel."
            )
        return donnees


class AffectationRechercheForm(forms.Form):
    poste = forms.ModelChoiceField(
        queryset=Fonction.objects.order_by("intitule_poste"),
        required=False,
        empty_label="Tous les postes",
    )
    debut = forms.DateField(
        label="Début à partir du",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    fin = forms.DateField(
        label="Fin jusqu'au",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    ville = forms.CharField(required=False)