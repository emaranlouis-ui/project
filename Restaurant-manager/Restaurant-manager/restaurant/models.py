from django.conf import settings
from django.db import models


SCHEMA_MANAGED = getattr(settings, "RESTAURANT_MODELS_MANAGED", False)


class Client(models.Model):
    id_client = models.IntegerField(db_column="id_Client", primary_key=True)
    nom = models.CharField(db_column="Nom", max_length=20, blank=True, null=True)
    prenom = models.CharField(db_column="Prenom", max_length=20, blank=True, null=True)
    tel = models.CharField(db_column="Tel", max_length=15, blank=True, null=True)
    email = models.EmailField(db_column="Email", max_length=45, blank=True, null=True)
    type_de_client = models.CharField(
        db_column="Type_de_Client", max_length=20, blank=True, null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Client"
        ordering = ("nom", "prenom")

    def __str__(self) -> str:
        full_name = " ".join(part for part in [self.prenom, self.nom] if part)
        return full_name or f"Client #{self.pk}"


class RestaurantTable(models.Model):
    id_table = models.IntegerField(db_column="id_Table", primary_key=True)
    numero_table = models.CharField(db_column="Numero_Table", max_length=3, blank=True, null=True)
    capacite = models.IntegerField(db_column="Capacite", blank=True, null=True)
    commentaire = models.TextField(db_column="Commentaire", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Table"
        ordering = ("numero_table",)
        verbose_name = "Table"
        verbose_name_plural = "Tables"

    def __str__(self) -> str:
        return self.numero_table or f"Table #{self.pk}"


class Reservation(models.Model):
    id_reservation = models.IntegerField(db_column="id_Reservation", primary_key=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_column="id_Client",
        related_name="reservations",
        blank=True,
        null=True,
    )
    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        db_column="id_Table",
        related_name="reservations",
        blank=True,
        null=True,
    )
    date = models.DateField(db_column="Date", blank=True, null=True)
    heure = models.TimeField(db_column="Heure", blank=True, null=True)
    statut = models.CharField(db_column="Statut", max_length=45, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Reservation"
        ordering = ("-date", "-heure")

    def __str__(self) -> str:
        return f"Reservation #{self.pk}"


class Ingredient(models.Model):
    id_ingredient = models.IntegerField(db_column="id_Ingredient", primary_key=True)
    nom = models.CharField(db_column="Nom", max_length=45, blank=True, null=True)
    unite_de_mesure = models.CharField(
        db_column="Unite_de_Mesure", max_length=45, blank=True, null=True
    )
    type_ingredient = models.CharField(db_column="Type", max_length=30, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Ingredient"
        ordering = ("nom",)

    def __str__(self) -> str:
        return self.nom or f"Ingredient #{self.pk}"


class Employe(models.Model):
    id_employe = models.IntegerField(db_column="id_Employe", primary_key=True)
    nom = models.CharField(db_column="Nom", max_length=20, blank=True, null=True)
    prenom = models.CharField(db_column="Prenom", max_length=20, blank=True, null=True)
    tel = models.CharField(db_column="Tel", max_length=15, blank=True, null=True)
    salaire = models.IntegerField(db_column="Salaire", blank=True, null=True)
    date_embauche = models.DateField(db_column="Date_Embauche", blank=True, null=True)
    image = models.ImageField(upload_to="employes/", null=True, blank=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Employe"
        ordering = ("nom", "prenom")

    def __str__(self) -> str:
        full_name = " ".join(part for part in [self.prenom, self.nom] if part)
        return full_name or f"Employe #{self.pk}"


class Produit(models.Model):
    id_produit = models.IntegerField(db_column="id_Produit", primary_key=True)
    createur = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Createur",
        related_name="produits_crees",
        blank=True,
        null=True,
    )
    nom = models.CharField(db_column="Nom", max_length=30, blank=True, null=True)
    description = models.CharField(db_column="Description", max_length=45, blank=True, null=True)
    duree_cuisson = models.CharField(
        db_column="Duree_Cuisson", max_length=20, blank=True, null=True
    )
    nombre_personnes = models.IntegerField(db_column="Nombre_Personnes", blank=True, null=True)
    prix = models.IntegerField(db_column="Prix", default=2500)
    image = models.ImageField(upload_to="produits/", null=True, blank=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Produit"
        ordering = ("nom",)

    def __str__(self) -> str:
        return self.nom or f"Produit #{self.pk}"


class Stock(models.Model):
    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.PROTECT,
        db_column="id_Ingredient",
        primary_key=True,
        related_name="stock",
    )
    quantite_actuelle = models.DecimalField(
        db_column="Quantite_Actuelle", max_digits=10, decimal_places=2, blank=True, null=True
    )
    seuil_alerte = models.DecimalField(
        db_column="Seuil_Alerte", max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Stock"
        ordering = ("ingredient__nom",)

    def __str__(self) -> str:
        return f"{self.ingredient} - {self.quantite_actuelle or 0}"


class VariationStock(models.Model):
    id_variation = models.IntegerField(db_column="id_Variation", primary_key=True)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        db_column="id_Ingredient",
        related_name="variations_stock",
        blank=True,
        null=True,
    )
    date = models.DateField(db_column="Date", blank=True, null=True)
    type_variation = models.CharField(db_column="Type", max_length=10, blank=True, null=True)
    quantite = models.DecimalField(
        db_column="Quantite", max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Variation_Stock"
        ordering = ("-date", "-id_variation")

    def __str__(self) -> str:
        return f"{self.type_variation or 'Variation'} - {self.ingredient}"


class CompositionProduit(models.Model):
    pk = models.CompositePrimaryKey("produit_id", "ingredient_id")
    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        db_column="id_Produit",
        related_name="compositions",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        db_column="id_Ingredient",
        related_name="compositions",
    )
    quantite_utilisee = models.DecimalField(
        db_column="Quantite_Utilisee", max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Composition_Produit"
        ordering = ("produit__nom", "ingredient__nom")

    def __str__(self) -> str:
        return f"{self.produit} / {self.ingredient}"


class Fournisseur(models.Model):
    id_fournisseur = models.IntegerField(db_column="id_Fournisseur", primary_key=True)
    nom = models.CharField(db_column="Nom", max_length=45, blank=True, null=True)
    tel = models.CharField(db_column="Tel", max_length=15, blank=True, null=True)
    adresse = models.CharField(db_column="Adresse", max_length=45, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Fournisseur"
        ordering = ("nom",)

    def __str__(self) -> str:
        return self.nom or f"Fournisseur #{self.pk}"


class Poste(models.Model):
    id_poste = models.IntegerField(db_column="id_Poste", primary_key=True)
    libelle_poste = models.CharField(db_column="Libelle_Poste", max_length=45, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Poste"
        ordering = ("libelle_poste",)

    def __str__(self) -> str:
        return self.libelle_poste or f"Poste #{self.pk}"


class Affectation(models.Model):
    pk = models.CompositePrimaryKey("employe_id", "poste_id")
    employe = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Employe",
        related_name="affectations",
    )
    poste = models.ForeignKey(
        Poste,
        on_delete=models.PROTECT,
        db_column="id_Poste",
        related_name="affectations",
    )
    date_debut = models.DateField(db_column="Date_debut", blank=True, null=True)
    date_fin = models.DateField(db_column="Date_fin", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Affectation"
        ordering = ("-date_debut",)

    def __str__(self) -> str:
        return f"{self.employe} - {self.poste}"


class Supervision(models.Model):
    pk = models.CompositePrimaryKey("superviseur_id", "employe_id")
    superviseur = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Superviseur",
        related_name="supervisions_donnees",
    )
    employe = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Employe",
        related_name="supervisions_recues",
    )
    date_debut = models.DateField(db_column="Date_debut", blank=True, null=True)
    date_fin = models.DateField(db_column="Date_fin", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Supervision"
        ordering = ("-date_debut",)

    def __str__(self) -> str:
        return f"{self.superviseur} -> {self.employe}"


class Vehicule(models.Model):
    id_vehicule = models.IntegerField(db_column="id_Vehicule", primary_key=True)
    immatriculation = models.CharField(db_column="Immatriculation", max_length=15, blank=True, null=True)
    modele = models.CharField(db_column="Modele", max_length=20, blank=True, null=True)
    marque = models.CharField(db_column="Marque", max_length=20, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Vehicule"
        ordering = ("immatriculation",)

    def __str__(self) -> str:
        return self.immatriculation or f"Vehicule #{self.pk}"


class Deplacement(models.Model):
    id_deplacement = models.IntegerField(db_column="id_Deplacement", primary_key=True)
    chauffeur = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Chauffeur",
        related_name="deplacements",
        blank=True,
        null=True,
    )
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.PROTECT,
        db_column="id_Vehicule",
        related_name="deplacements",
        blank=True,
        null=True,
    )
    date_depart = models.DateTimeField(db_column="Date_depart", blank=True, null=True)
    destination = models.TextField(db_column="Destination", blank=True, null=True)
    distance_totale = models.DecimalField(
        db_column="Distance_totale", max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Deplacement"
        ordering = ("-date_depart",)

    def __str__(self) -> str:
        return f"{self.destination or 'Deplacement'} - {self.date_depart or self.pk}"


class Approvisionnement(models.Model):
    id_approvisionnement = models.IntegerField(db_column="id_Approvisionnement", primary_key=True)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        db_column="id_Ingredient",
        related_name="approvisionnements",
        blank=True,
        null=True,
    )
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.PROTECT,
        db_column="id_Fournisseur",
        related_name="approvisionnements",
        blank=True,
        null=True,
    )
    deplacement = models.ForeignKey(
        Deplacement,
        on_delete=models.PROTECT,
        db_column="id_Deplacement",
        related_name="approvisionnements",
        blank=True,
        null=True,
    )
    date = models.DateField(db_column="Date", blank=True, null=True)
    quantite = models.DecimalField(
        db_column="Quantite", max_digits=10, decimal_places=2, blank=True, null=True
    )
    prix_unitaire = models.IntegerField(db_column="Prix_Unitaire", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Approvisionnement"
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.ingredient} - {self.fournisseur}"


class Equipement(models.Model):
    id_equipement = models.IntegerField(db_column="id_Equipement", primary_key=True)
    nom = models.CharField(db_column="Nom", max_length=45, blank=True, null=True)
    etat = models.CharField(db_column="Etat", max_length=45, blank=True, null=True)
    date_achat = models.DateField(db_column="Date_Achat", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Equipement"
        ordering = ("nom",)

    def __str__(self) -> str:
        return self.nom or f"Equipement #{self.pk}"


class Maintenance(models.Model):
    id_maintenance = models.IntegerField(db_column="id_Maintenance", primary_key=True)
    technicien = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Technicien",
        related_name="maintenances",
        blank=True,
        null=True,
    )
    equipement = models.ForeignKey(
        Equipement,
        on_delete=models.PROTECT,
        db_column="id_Equipement",
        related_name="maintenances",
        blank=True,
        null=True,
    )
    date = models.DateField(db_column="Date", blank=True, null=True)
    type_maintenance = models.CharField(db_column="Type", max_length=45, blank=True, null=True)
    commentaire = models.TextField(db_column="Commentaire", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Maintenance"
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.type_maintenance or 'Maintenance'} - {self.equipement}"


class ActionMarketing(models.Model):
    id_action = models.IntegerField(db_column="id_Action", primary_key=True)
    responsable = models.ForeignKey(
        Employe,
        on_delete=models.PROTECT,
        db_column="id_Responsable",
        related_name="actions_marketing",
        blank=True,
        null=True,
    )
    type_action = models.CharField(db_column="Type_Action", max_length=20, blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    date_debut = models.DateField(db_column="Date_debut", blank=True, null=True)
    date_fin = models.DateField(db_column="Date_fin", blank=True, null=True)
    budget = models.IntegerField(db_column="Budget", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Action_Marketing"
        ordering = ("-date_debut",)

    def __str__(self) -> str:
        return f"{self.type_action or 'Action'} - {self.date_debut or self.pk}"


class Commande(models.Model):
    id_commande = models.IntegerField(db_column="id_Commande", primary_key=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_column="id_Client",
        related_name="commandes",
        blank=True,
        null=True,
    )
    date = models.DateTimeField(db_column="Date", blank=True, null=True)
    type_commande = models.CharField(db_column="Type", max_length=30, blank=True, null=True)
    montant_total = models.IntegerField(db_column="Montant_Total", blank=True, null=True)
    mode_de_paiement = models.CharField(
        db_column="Mode_de_Paiement", max_length=45, blank=True, null=True
    )
    statut_cuisine = models.CharField(
        db_column="Statut_Cuisine", 
        max_length=20, 
        choices=[("En attente", "En attente"), ("En cours", "En cours"), ("Prête", "Prête")],
        default="En attente",
        blank=True, 
        null=True
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Commande"
        ordering = ("-date",)
        permissions = [
            ("view_cuisine", "Peut voir l'écran cuisine"),
            ("change_statut_cuisine", "Peut changer le statut des commandes en cuisine"),
        ]

    def __str__(self) -> str:
        return f"Commande #{self.pk}"


class LigneCommande(models.Model):
    pk = models.CompositePrimaryKey("commande_id", "produit_id")
    commande = models.ForeignKey(
        Commande,
        on_delete=models.PROTECT,
        db_column="id_Commande",
        related_name="lignes",
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        db_column="id_Produit",
        related_name="lignes_commande",
    )
    quantite = models.DecimalField(
        db_column="Quantite", max_digits=10, decimal_places=2, blank=True, null=True
    )
    prix_unitaire = models.IntegerField(db_column="Prix_Unitaire", blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Ligne_Commande"
        ordering = ("commande_id", "produit__nom")

    def __str__(self) -> str:
        return f"{self.commande} - {self.produit}"


class Livraison(models.Model):
    id_livraison = models.IntegerField(db_column="id_Livraison", primary_key=True)
    commande = models.OneToOneField(
        Commande,
        on_delete=models.PROTECT,
        db_column="id_Commande",
        related_name="livraison",
        blank=True,
        null=True,
    )
    deplacement = models.ForeignKey(
        Deplacement,
        on_delete=models.PROTECT,
        db_column="id_Deplacement",
        related_name="livraisons",
        blank=True,
        null=True,
    )

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Livraison"
        ordering = ("id_livraison",)

    def __str__(self) -> str:
        return f"Livraison #{self.pk}"


class Facture(models.Model):
    id_facture = models.IntegerField(db_column="id_Facture", primary_key=True)
    date = models.DateField(db_column="Date", blank=True, null=True)
    montant = models.IntegerField(db_column="Montant", blank=True, null=True)
    type_facture = models.CharField(db_column="Type", max_length=45, blank=True, null=True)

    class Meta:
        managed = SCHEMA_MANAGED
        db_table = "Facture"
        ordering = ("-date", "-id_facture")

    def __str__(self) -> str:
        return f"{self.type_facture or 'Facture'} #{self.pk}"

