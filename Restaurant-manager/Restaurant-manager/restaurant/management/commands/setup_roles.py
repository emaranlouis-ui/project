from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from restaurant.models import Commande, Stock, Produit, Employe

class Command(BaseCommand):
    help = "Initialise les groupes et permissions par défaut du restaurant."

    def handle(self, *args, **options):
        # 1. Obtenir les content types
        commande_ct = ContentType.objects.get_for_model(Commande)
        stock_ct = ContentType.objects.get_for_model(Stock)
        produit_ct = ContentType.objects.get_for_model(Produit)
        employe_ct = ContentType.objects.get_for_model(Employe)

        # 2. Récupérer ou créer les permissions spécifiques
        try:
            view_cuisine_perm = Permission.objects.get(codename='view_cuisine', content_type=commande_ct)
            change_statut_cuisine_perm = Permission.objects.get(codename='change_statut_cuisine', content_type=commande_ct)
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR("Les permissions view_cuisine ou change_statut_cuisine n'existent pas. Assurez-vous d'avoir fait les migrations."))
            return

        # 3. Définir les groupes et leurs permissions
        roles_permissions = {
            "Chef cuisinier": [
                'view_cuisine', 'change_statut_cuisine', 
                'view_produit', 'change_produit', 'add_produit', 'delete_produit',
                'view_stock'
            ],
            "Cuisinier": [
                'view_cuisine', 'change_statut_cuisine',
                'view_produit'
            ],
            "Serveur": [
                'view_commande', 'add_commande', 'change_commande',
                'view_produit'
            ],
            "Gestionnaire de stock": [
                'view_stock', 'add_stock', 'change_stock', 'delete_stock',
                'view_produit'
            ],
            "Directeur": [
                'view_commande', 'view_stock', 'view_produit', 'view_employe', 'view_facture'
            ],
            "Administrateur": [] # L'administrateur sera souvent superuser
        }

        # 4. Créer les groupes et assigner
        for role_name, perms in roles_permissions.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe '{role_name}' créé."))
            
            # Assigner les permissions
            for perm_codename in perms:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Permission '{perm_codename}' non trouvée, ignorée pour {role_name}."))
            
            self.stdout.write(self.style.SUCCESS(f"Permissions mises à jour pour '{role_name}'."))
            
        self.stdout.write(self.style.SUCCESS("Initialisation des rôles terminée avec succès."))
