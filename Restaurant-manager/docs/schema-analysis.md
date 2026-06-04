# Analyse initiale du schema restaurant

## Sources trouvees

- SQL: `Base_Restaurant.sql/Base_Restaurant.sql`
- Sujet: `GTEL_Project-Restaurant_Software_python&Soft-2025-2026S2pdf.pdf`

## Contraintes principales du sujet

- Framework: Django.
- Base de donnees: MySQL obligatoire.
- Utilisation de l'ORM Django.
- Modules attendus: utilisateurs et roles, recettes/produits, commandes, stock, RH, livraisons, finances, tableau de bord.
- Indicateurs attendus: chiffre d'affaires mensuel, nombre de commandes, produits les plus vendus, depenses d'approvisionnement.

## Tables SQL detectees

Le schema contient 23 tables:

- `Client`
- `Table`
- `Reservation`
- `Ingredient`
- `Employe`
- `Produit`
- `Stock`
- `Variation_Stock`
- `Composition_Produit`
- `Fournisseur`
- `Poste`
- `Affectation`
- `Supervision`
- `Vehicule`
- `Deplacement`
- `Approvisionnement`
- `Equipement`
- `Maintenance`
- `Action_Marketing`
- `Commande`
- `Ligne_Commande`
- `Livraison`
- `Facture`

## Choix d'initialisation Django

- Le projet Django s'appelle `restaurant_manager`.
- L'application metier s'appelle `restaurant`.
- Les modeles utilisent `db_table` et `db_column` pour conserver la compatibilite avec les noms SQL existants.
- La configuration pointe par defaut vers MySQL et la base `Restaurant`.
- `RESTAURANT_MODELS_MANAGED=False` par defaut pour eviter que Django modifie une base MySQL deja creee par le script SQL.

## Points techniques a surveiller

- Les tables `Composition_Produit`, `Affectation`, `Supervision` et `Ligne_Commande` utilisent des cles primaires composites.
- Django 5.2 supporte `CompositePrimaryKey`, mais les modeles avec cle primaire composite ne sont pas encore enregistrables dans l'admin Django standard.
- Ces modeles sont donc presents dans l'ORM pour les requetes et les services, mais ils ne sont pas enregistres directement dans `restaurant/admin.py`.
- Le script SQL contient des donnees accentuees. Le projet ne modifie pas ces donnees afin de garder le SQL source intact.
