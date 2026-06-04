from django.contrib import admin

from .models import (
    ActionMarketing,
    Approvisionnement,
    Client,
    Commande,
    Deplacement,
    Employe,
    Equipement,
    Facture,
    Fournisseur,
    Ingredient,
    Livraison,
    Maintenance,
    Poste,
    Produit,
    Reservation,
    RestaurantTable,
    Stock,
    VariationStock,
    Vehicule,
)


admin.site.site_header = "Restaurant POS Manager"
admin.site.site_title = "Restaurant POS"
admin.site.index_title = "Administration du restaurant"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id_client", "nom", "prenom", "tel", "email", "type_de_client")
    search_fields = ("nom", "prenom", "tel", "email")
    list_filter = ("type_de_client",)


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ("id_table", "numero_table", "capacite", "commentaire")
    search_fields = ("numero_table", "commentaire")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id_reservation", "client", "table", "date", "heure", "statut")
    list_filter = ("statut", "date")
    search_fields = ("client__nom", "client__prenom", "table__numero_table")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id_ingredient", "nom", "unite_de_mesure", "type_ingredient")
    list_filter = ("type_ingredient", "unite_de_mesure")
    search_fields = ("nom",)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "quantite_actuelle", "seuil_alerte")
    search_fields = ("ingredient__nom",)


@admin.register(VariationStock)
class VariationStockAdmin(admin.ModelAdmin):
    list_display = ("id_variation", "ingredient", "date", "type_variation", "quantite")
    list_filter = ("type_variation", "date")
    search_fields = ("ingredient__nom",)


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ("id_employe", "nom", "prenom", "tel", "salaire", "date_embauche")
    search_fields = ("nom", "prenom", "tel")
    list_filter = ("date_embauche",)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("id_produit", "nom", "description", "duree_cuisson", "nombre_personnes", "createur")
    search_fields = ("nom", "description", "createur__nom", "createur__prenom")
    list_filter = ("description",)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("id_fournisseur", "nom", "tel", "adresse")
    search_fields = ("nom", "tel", "adresse")


@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ("id_poste", "libelle_poste")
    search_fields = ("libelle_poste",)


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ("id_vehicule", "immatriculation", "marque", "modele")
    search_fields = ("immatriculation", "marque", "modele")


@admin.register(Deplacement)
class DeplacementAdmin(admin.ModelAdmin):
    list_display = ("id_deplacement", "chauffeur", "vehicule", "date_depart", "destination", "distance_totale")
    list_filter = ("date_depart",)
    search_fields = ("destination", "chauffeur__nom", "vehicule__immatriculation")


@admin.register(Approvisionnement)
class ApprovisionnementAdmin(admin.ModelAdmin):
    list_display = (
        "id_approvisionnement",
        "ingredient",
        "fournisseur",
        "deplacement",
        "date",
        "quantite",
        "prix_unitaire",
    )
    list_filter = ("date", "fournisseur")
    search_fields = ("ingredient__nom", "fournisseur__nom")


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ("id_equipement", "nom", "etat", "date_achat")
    list_filter = ("etat", "date_achat")
    search_fields = ("nom",)


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("id_maintenance", "technicien", "equipement", "date", "type_maintenance")
    list_filter = ("type_maintenance", "date")
    search_fields = ("technicien__nom", "equipement__nom", "commentaire")


@admin.register(ActionMarketing)
class ActionMarketingAdmin(admin.ModelAdmin):
    list_display = ("id_action", "type_action", "responsable", "date_debut", "date_fin", "budget")
    list_filter = ("type_action", "date_debut")
    search_fields = ("type_action", "description", "responsable__nom")


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id_commande", "client", "date", "type_commande", "montant_total", "mode_de_paiement")
    list_filter = ("type_commande", "mode_de_paiement", "date")
    search_fields = ("client__nom", "client__prenom", "mode_de_paiement")


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ("id_livraison", "commande", "deplacement")
    search_fields = ("=commande__id_commande", "deplacement__destination")


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("id_facture", "date", "montant", "type_facture")
    list_filter = ("type_facture", "date")
    search_fields = ("type_facture",)
