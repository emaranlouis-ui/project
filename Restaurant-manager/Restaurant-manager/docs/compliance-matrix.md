# Matrice de couverture du cahier de charge

| Exigence | Etat | Implementation actuelle |
| --- | --- | --- |
| Django Python 3.x | Initialise | `manage.py`, `restaurant_manager/`, `restaurant/` |
| MySQL obligatoire | Initialise | `restaurant_manager/settings.py`, variables `.env.example` |
| ORM aligne sur le SQL | Initialise | `restaurant/models.py` |
| Authentification securisee | Partiel | Auth Django, `login_required`, admin |
| Gestion des roles | Partiel | Commande `python manage.py init_roles` |
| Permissions specifiques | Partiel | Groupes Django par role |
| Admin personnalisee | Partiel | `restaurant/admin.py` |
| Interface ergonomique | Partiel | Templates dashboard et modules |
| Produits et recettes | Partiel | Vue `/produits/`, modeles `Produit`, `CompositionProduit`, `Ingredient` |
| Commandes | Partiel | Vue `/commandes/`, modeles `Commande`, `LigneCommande` |
| Calcul automatique montant | Partiel | Service `recompute_order_total` |
| Factures | Partiel | Vue `/finances/`, modele `Facture` |
| Stock et seuils critiques | Partiel | Vue `/stock/`, service `low_stock_items` |
| Historique stock | Modele pret | Modele `VariationStock` |
| RH | Partiel | Vue `/rh/`, modeles `Employe`, `Poste`, `Affectation` |
| Paie | A faire | Service de paie mensuelle a ajouter |
| Dashboard financier | Partiel | Vue `/dashboard/`, services mensuels |
| CSRF | Initialise | Middleware Django active |
| Anti SQL injection | Initialise | Requetes ORM |
| Logging actions critiques | Initialise | Configuration `LOGGING` |
| Documentation technique | Partiel | `README.md`, `docs/schema-analysis.md`, ce document |

## Priorites restantes

1. Ajouter des formulaires metier pour creer les commandes et lignes de commandes hors admin.
2. Brancher la mise a jour automatique du stock apres validation d'une commande.
3. Ajouter la generation de facture liee a une commande.
4. Ajouter le calcul de paie mensuelle par employe.
5. Ajouter des tests Django sur les services critiques.
6. Rediger le rapport technique complet et le manuel utilisateur.

