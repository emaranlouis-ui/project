# Cahier de charge fonctionnel

## Projet

Development of a Restaurant Management Web Application.

- Framework: Django avec Python 3.x.
- SGBD: MySQL obligatoire.
- Architecture: MVT Django.
- Base de depart: schema MySQL existant du restaurant.

## Objectif general

Developper une application web complete de gestion de restaurant basee sur Django et connectee a une base MySQL existante.

## Objectifs specifiques

- Implementer les modeles Django correspondant au schema SQL existant.
- Configurer MySQL comme SGBD principal.
- Developper une interface d'administration personnalisee.
- Concevoir des interfaces ergonomiques.
- Implementer les regles metier.
- Generer des rapports financiers dynamiques.
- Assurer la securite des donnees.

## Modules fonctionnels

### Gestion des utilisateurs

Roles attendus:

- Administrateur.
- Directeur.
- Chef cuisinier.
- Cuisinier.
- Serveur.
- Gestionnaire de stock.

Fonctions attendues:

- Authentification securisee.
- Gestion des roles.
- Permissions specifiques.

### Gestion des produits

- Creation, modification et suppression.
- Association recette-ingredient.
- Quantites requises.
- Temps de cuisson.
- Chef responsable.
- Catalogue des plats.
- Categorisation.
- Prix dynamique.

### Gestion des commandes et revenus

- Commandes sur place.
- Commandes en livraison.
- Calcul automatique du montant.
- Generation de factures.

### Gestion des stocks

- Mise a jour automatique apres commande.
- Alertes de seuil critique.
- Historique des variations.

### Gestion RH

- Fiches employes.
- Affectations.
- Calcul de la paie.

### Tableau de bord

- Chiffre d'affaires mensuel.
- Nombre de commandes.
- Produits les plus vendus.
- Depenses d'approvisionnement.

## Exigences non fonctionnelles

- Interface ergonomique.
- Protection CSRF active.
- Protection contre les injections SQL via ORM Django.
- Performance optimisee.
- Logging des actions critiques.

## Livrables attendus

- Code source complet.
- Base MySQL configuree.
- Rapport technique de 25 a 35 pages.
- Manuel utilisateur.
- Presentation orale avec demonstration.

