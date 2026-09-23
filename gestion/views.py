from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (
    AffectationFiltreForm,
    AffectationForm,
    ChangementPosteForm,
    CollaborateurForm,
    CollaborateurRechercheForm,
    FonctionForm,
    RestaurantForm,
    RestaurantRechercheForm,
    AffectationRechercheForm
)
from .mixins import AdministrateurRequisMixin
from .models import Affectation, Collaborateur, Fonction, Restaurant


@login_required
def accueil(request):
    return render(request, "gestion/accueil.html")


class RestaurantListView(AdministrateurRequisMixin, ListView):
    model = Restaurant
    template_name = "gestion/restaurant_liste.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        restaurants = Restaurant.objects.order_by("nom")
        self.formulaire = RestaurantRechercheForm(self.request.GET)
        if self.formulaire.is_valid():
            donnees = self.formulaire.cleaned_data
            if donnees["nom"]:
                restaurants = restaurants.filter(nom__icontains=donnees["nom"])
            if donnees["code_postal"]:
                restaurants = restaurants.filter(
                    code_postal__startswith=donnees["code_postal"]
                )
            if donnees["ville"]:
                restaurants = restaurants.filter(ville__icontains=donnees["ville"])
        return restaurants

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["formulaire"] = self.formulaire
        return contexte


class RestaurantCreateView(AdministrateurRequisMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "gestion/restaurant_form.html"
    success_url = reverse_lazy("restaurant_liste")

    def form_valid(self, form):
        messages.success(self.request, "Le restaurant a été créé.")
        return super().form_valid(form)

class RestaurantDetailView(AdministrateurRequisMixin, DetailView):
    model = Restaurant
    template_name = "gestion/restaurant_detail.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        affectations = self.object.affectations.select_related("collaborateur", "poste")

        # Collaborateurs actuellement en poste : affectations sans date de fin
        en_poste = affectations.filter(fin__isnull=True).order_by(
            "collaborateur__last_name", "collaborateur__first_name"
        )

        formulaire = AffectationFiltreForm(self.request.GET)
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            if donnees["poste"]:
                en_poste = en_poste.filter(poste=donnees["poste"])
            if donnees["debut"]:
                en_poste = en_poste.filter(debut__gte=donnees["debut"])

        contexte["formulaire"] = formulaire
        contexte["en_poste"] = en_poste
        contexte["historique"] = affectations.order_by("-debut")
        return contexte


class RestaurantUpdateView(AdministrateurRequisMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "gestion/restaurant_form.html"

    def get_success_url(self):
        return reverse("restaurant_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Le restaurant a été modifié.")
        return super().form_valid(form)

class RestaurantAffecterView(AdministrateurRequisMixin, CreateView):
    model = Affectation
    form_class = AffectationForm
    template_name = "gestion/restaurant_affecter.html"

    def dispatch(self, request, *args, **kwargs):
        self.restaurant = get_object_or_404(Restaurant, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.restaurant = self.restaurant
        messages.success(self.request, "Le collaborateur a été affecté.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["restaurant"] = self.restaurant
        return contexte

    def get_success_url(self):
        return reverse("restaurant_detail", kwargs={"pk": self.restaurant.pk})

class FonctionListView(AdministrateurRequisMixin, ListView):
    model = Fonction
    template_name = "gestion/fonction_liste.html"
    context_object_name = "fonctions"
    queryset = Fonction.objects.order_by("intitule_poste")


class FonctionCreateView(AdministrateurRequisMixin, CreateView):
    model = Fonction
    form_class = FonctionForm
    template_name = "gestion/fonction_form.html"
    success_url = reverse_lazy("fonction_liste")

    def form_valid(self, form):
        messages.success(self.request, "La fonction a été créée.")
        return super().form_valid(form)


class FonctionUpdateView(AdministrateurRequisMixin, UpdateView):
    model = Fonction
    form_class = FonctionForm
    template_name = "gestion/fonction_form.html"
    success_url = reverse_lazy("fonction_liste")

    def form_valid(self, form):
        messages.success(self.request, "La fonction a été modifiée.")
        return super().form_valid(form)

class CollaborateurListView(AdministrateurRequisMixin, ListView):
    model = Collaborateur
    template_name = "gestion/collaborateur_liste.html"
    context_object_name = "collaborateurs"

    def get_queryset(self):
        collaborateurs = Collaborateur.objects.order_by("last_name", "first_name")
        self.formulaire = CollaborateurRechercheForm(self.request.GET)
        if self.formulaire.is_valid():
            donnees = self.formulaire.cleaned_data
            if donnees["nom"]:
                collaborateurs = collaborateurs.filter(last_name__icontains=donnees["nom"])
            if donnees["prenom"]:
                collaborateurs = collaborateurs.filter(first_name__icontains=donnees["prenom"])
            if donnees["email"]:
                collaborateurs = collaborateurs.filter(email__icontains=donnees["email"])
        return collaborateurs

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["formulaire"] = self.formulaire
        return contexte


class CollaborateurCreateView(AdministrateurRequisMixin, CreateView):
    model = Collaborateur
    form_class = CollaborateurForm
    template_name = "gestion/collaborateur_form.html"
    success_url = reverse_lazy("collaborateur_liste")

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Le collaborateur a été créé.")
        return super(CreateView, self).form_valid(form)


class CollaborateurNonAffectesView(AdministrateurRequisMixin, ListView):
    template_name = "gestion/collaborateur_non_affectes.html"
    context_object_name = "collaborateurs"

    def get_queryset(self):
        return Collaborateur.objects.exclude(
            affectations__fin__isnull=True
        ).order_by("last_name", "first_name")

class CollaborateurDetailView(AdministrateurRequisMixin, DetailView):
    model = Collaborateur
    template_name = "gestion/collaborateur_detail.html"
    context_object_name = "collaborateur"

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        affectations = self.object.affectations.select_related("restaurant", "poste")

        en_poste = affectations.filter(fin__isnull=True).order_by("restaurant__nom")

        formulaire = AffectationFiltreForm(self.request.GET)
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            if donnees["poste"]:
                en_poste = en_poste.filter(poste=donnees["poste"])
            if donnees["debut"]:
                en_poste = en_poste.filter(debut__gte=donnees["debut"])

        contexte["formulaire"] = formulaire
        contexte["en_poste"] = en_poste
        contexte["historique"] = affectations.order_by("-debut")
        return contexte


class AffectationChangerPosteView(AdministrateurRequisMixin, View):
    def get(self, request, pk):
        affectation = get_object_or_404(Affectation, pk=pk, fin__isnull=True)
        formulaire = ChangementPosteForm()
        return render(
            request,
            "gestion/changement_poste.html",
            {"affectation": affectation, "formulaire": formulaire},
        )

    def post(self, request, pk):
        affectation = get_object_or_404(Affectation, pk=pk, fin__isnull=True)
        formulaire = ChangementPosteForm(request.POST)
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data

            affectation.fin = donnees["fin_poste_actuel"]
            affectation.full_clean()
            affectation.save()

            nouvelle_affectation = Affectation(
                collaborateur=affectation.collaborateur,
                restaurant=donnees["nouveau_restaurant"],
                poste=donnees["nouveau_poste"],
                debut=donnees["nouveau_debut"],
            )
            nouvelle_affectation.full_clean()
            nouvelle_affectation.save()

            messages.success(request, "Le collaborateur a été affecté à son nouveau poste.")
            return redirect("collaborateur_detail", pk=affectation.collaborateur.pk)

        return render(
            request,
            "gestion/changement_poste.html",
            {"affectation": affectation, "formulaire": formulaire},
        )

class AffectationRechercheView(AdministrateurRequisMixin, ListView):
    model = Affectation
    template_name = "gestion/affectation_recherche.html"
    context_object_name = "affectations"

    def get_queryset(self):
        affectations = Affectation.objects.select_related(
            "collaborateur", "restaurant", "poste"
        ).order_by("-debut")

        self.formulaire = AffectationRechercheForm(self.request.GET)
        if self.formulaire.is_valid():
            donnees = self.formulaire.cleaned_data
            if donnees["poste"]:
                affectations = affectations.filter(poste=donnees["poste"])
            if donnees["debut"]:
                affectations = affectations.filter(debut__gte=donnees["debut"])
            if donnees["fin"]:
                affectations = affectations.filter(fin__lte=donnees["fin"])
            if donnees["ville"]:
                affectations = affectations.filter(restaurant__ville__icontains=donnees["ville"])
        return affectations

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["formulaire"] = self.formulaire
        return contexte