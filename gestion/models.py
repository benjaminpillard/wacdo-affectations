from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models


class CollaborateurManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")

        email = self.normalize_email(email)

        collaborateur = self.model(
            email=email,
            **extra_fields,
        )

        collaborateur.set_password(password)
        collaborateur.save(using=self._db)

        return collaborateur

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("administrateur", True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class Collaborateur(AbstractUser):
    username = None
    first_name = models.CharField("prénom", max_length=150)
    last_name = models.CharField("nom", max_length=150)

    email = models.EmailField(unique=True)
    date_premiere_embauche = models.DateField()
    administrateur = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "date_premiere_embauche",
    ]

    objects = CollaborateurManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    
class Restaurant(models.Model):
    nom = models.CharField(max_length=150)
    adresse = models.CharField(max_length=250)
    code_postal = models.CharField(max_length=5)
    ville = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.nom}-{self.ville}"

class Fonction(models.Model):
    intitule_poste = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.intitule_poste

class Affectation(models.Model):
    collaborateur = models.ForeignKey(
        Collaborateur,
        on_delete = models.PROTECT,
        related_name="affectations",
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete= models.PROTECT,
        related_name="affectations",
    )
    poste = models.ForeignKey(
        Fonction,
        on_delete= models.PROTECT,
        related_name= "affectations",
    )
    debut = models.DateField()
    fin = models.DateField(blank=True, null=True)

    def clean(self):    
        if self.debut and self.fin and self.fin < self.debut:
            raise ValidationError(
                {"fin":"La date de fin ne paut pas précéder la date de début."}
            )

    def __str__(self) -> str:
        return (
            f"{self.collaborateur} -"
            f"{self.restaurant} -"
            f"{self.poste}"
        )
    
