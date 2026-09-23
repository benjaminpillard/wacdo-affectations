from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="gestion/connexion.html",
            redirect_authenticated_user=True,
        ),
        name="connexion",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="deconnexion"),
    path("restaurants/", views.RestaurantListView.as_view(), name="restaurant_liste"),
    path("restaurants/creer/", views.RestaurantCreateView.as_view(), name="restaurant_creer"),
    path("restaurants/<int:pk>/", views.RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("restaurants/<int:pk>/modifier/", views.RestaurantUpdateView.as_view(), name="restaurant_modifier"),
    path("restaurants/<int:pk>/affecter/", views.RestaurantAffecterView.as_view(), name="restaurant_affecter"),
    path("fonctions/", views.FonctionListView.as_view(), name="fonction_liste"),
    path("fonctions/creer/", views.FonctionCreateView.as_view(), name="fonction_creer"),
    path("fonctions/<int:pk>/modifier/", views.FonctionUpdateView.as_view(), name="fonction_modifier"),
    path("collaborateurs/", views.CollaborateurListView.as_view(), name="collaborateur_liste"),
    path("collaborateurs/creer/", views.CollaborateurCreateView.as_view(), name="collaborateur_creer"),
    path("collaborateurs/non-affectes/", views.CollaborateurNonAffectesView.as_view(), name="collaborateur_non_affectes"),
    path("collaborateurs/<int:pk>/", views.CollaborateurDetailView.as_view(), name="collaborateur_detail"),
    path("affectations/<int:pk>/changer-poste/", views.AffectationChangerPosteView.as_view(), name="affectation_changer_poste"),
    path("affectations/", views.AffectationRechercheView.as_view(), name="affectation_recherche"),
]