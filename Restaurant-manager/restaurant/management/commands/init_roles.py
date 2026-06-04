from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


ROLE_RULES = {
    "Administrateur": {
        "models": "__all__",
        "actions": ("add", "change", "delete", "view"),
    },
    "Directeur": {
        "models": "__all__",
        "actions": ("change", "view"),
    },
    "Chef Cuisinier": {
        "models": ("produit", "ingredient", "compositionproduit", "stock", "variationstock"),
        "actions": ("add", "change", "view"),
    },
    "Cuisinier": {
        "models": ("produit", "ingredient", "compositionproduit", "stock"),
        "actions": ("view",),
    },
    "Serveur": {
        "models": ("client", "restauranttable", "reservation", "commande", "lignecommande", "facture"),
        "actions": ("add", "change", "view"),
    },
    "Gestionnaire Stock": {
        "models": (
            "ingredient",
            "stock",
            "variationstock",
            "fournisseur",
            "approvisionnement",
        ),
        "actions": ("add", "change", "view"),
    },
}


class Command(BaseCommand):
    help = "Create default groups and permissions for the restaurant project."

    def handle(self, *args, **options):
        restaurant_models = list(apps.get_app_config("restaurant").get_models())
        model_by_name = {model._meta.model_name: model for model in restaurant_models}

        for role, rule in ROLE_RULES.items():
            group, _ = Group.objects.get_or_create(name=role)
            models = restaurant_models
            if rule["models"] != "__all__":
                models = [model_by_name[name] for name in rule["models"] if name in model_by_name]

            permissions = []
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                codenames = [f"{action}_{model._meta.model_name}" for action in rule["actions"]]
                permissions.extend(
                    Permission.objects.filter(content_type=content_type, codename__in=codenames)
                )

            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"{role}: {len(permissions)} permissions"))

