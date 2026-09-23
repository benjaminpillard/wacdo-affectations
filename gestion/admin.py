
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Affectation, Collaborateur, Fonction, Restaurant

@admin.register(Collaborateur)
class CollaborateurAdmin(UserAdmin):
    model = Collaborateur

    list_display = (
        "email",
        "first_name",
        "last_name",
        "administrateur",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("last_name","first_name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Informations personnelles",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_premiere_embauche",
                )
            },
        ),
        (
            "Autorisations",
            {
                "fields": (
                    "administrateur",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates importantes",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "date_premiere_embauche",
                    "password1",
                    "password2",
                    "administrateur",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "adresse",
        "code_postal",
        "ville",
    )

    search_fields = (
        "nom",
        "code_postal",
        "ville",
    )


@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ("intitule_poste",)
    search_fields = ("intitule_poste",)


@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = (
        "collaborateur",
        "restaurant",
        "poste",
        "debut",
        "fin",
    )

    list_filter = (
        "poste",
        "restaurant",
        "debut",
        "fin",
    )

    search_fields = (
        "collaborateur__first_name",
        "collaborateur__last_name",
        "restaurant__nom",
        "restaurant__ville",
        "poste__intitule_poste",
    )


