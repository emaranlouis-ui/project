import json

from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Count, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Commande, Client, Employe, Facture, LigneCommande, Produit, RestaurantTable, Stock
from .services import (
    best_selling_products,
    low_stock_items,
    monthly_order_count,
    monthly_supply_expenses,
    monthly_turnover,
)


def _get_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _get_month(value: str | None, default: int) -> int:
    return min(max(_get_int(value, default), 1), 12)


@login_required
def dashboard(request):
    from django.db.models import Sum
    today = timezone.localdate()
    year = _get_int(request.GET.get("year"), today.year)
    month = _get_month(request.GET.get("month"), today.month)

    # --- Chart 1: CA des 6 derniers mois ---
    ca_labels = []
    ca_values = []
    MONTHS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    for i in range(5, -1, -1):
        ref = today.replace(day=1)
        # subtract i months
        m = ref.month - i
        y = ref.year
        while m <= 0:
            m += 12
            y -= 1
        total = Commande.objects.filter(date__year=y, date__month=m).aggregate(s=Sum("montant_total"))["s"] or 0
        ca_labels.append(f"{MONTHS_FR[m-1]} {y}")
        ca_values.append(int(total))

    # --- Chart 2: Commandes par type (doughnut) ---
    type_data = (
        Commande.objects
        .filter(date__year=year, date__month=month)
        .values("type_commande")
        .annotate(count=Count("id_commande"))
    )
    type_labels = [d["type_commande"] or "Non défini" for d in type_data]
    type_values = [d["count"] for d in type_data]

    # --- Chart 3: Ventes journalières du mois courant (bar) ---
    import calendar
    nb_days = calendar.monthrange(year, month)[1]
    daily_labels = [str(d) for d in range(1, nb_days + 1)]
    daily_values = []
    daily_qs = (
        Commande.objects
        .filter(date__year=year, date__month=month)
        .values("date__day")
        .annotate(total=Sum("montant_total"))
    )
    daily_map = {d["date__day"]: int(d["total"] or 0) for d in daily_qs}
    for d in range(1, nb_days + 1):
        daily_values.append(daily_map.get(d, 0))

    context = {
        "current_month": timezone.datetime(year, month, 1).date(),
        "monthly_turnover": monthly_turnover(year, month),
        "monthly_order_count": monthly_order_count(year, month),
        "monthly_supply_expenses": monthly_supply_expenses(year, month),
        "best_selling_products": best_selling_products(),
        "low_stock_items": low_stock_items(),
        # Chart data (JSON-safe)
        "chart_ca_labels": json.dumps(ca_labels),
        "chart_ca_values": json.dumps(ca_values),
        "chart_type_labels": json.dumps(type_labels),
        "chart_type_values": json.dumps(type_values),
        "chart_daily_labels": json.dumps(daily_labels),
        "chart_daily_values": json.dumps(daily_values),
        "chart_top_labels": json.dumps([p.nom for p in best_selling_products()]),
        "chart_top_values": json.dumps([int(p.total_quantite or 0) for p in best_selling_products()]),
    }
    return render(request, "restaurant/dashboard.html", context)


@login_required
def products(request):
    from .models import Ingredient
    context = {
        "products": Produit.objects.select_related("createur").prefetch_related(
            "compositions__ingredient"
        ),
        "ingredients": Ingredient.objects.all(),
    }
    return render(request, "restaurant/products.html", context)


@login_required
def product_crud(request):
    if request.method == "POST" and request.user.is_superuser:
        action = request.POST.get("action")
        try:
            if action == "add":
                nom = request.POST.get("nom")
                desc = request.POST.get("description")
                duree = request.POST.get("duree_cuisson")
                pers = request.POST.get("nombre_personnes")
                prix = request.POST.get("prix", 2500)
                image = request.FILES.get("image")
                
                max_id = Produit.objects.aggregate(max_id=Max("id_produit"))["max_id"] or 0
                createur = Employe.objects.first()
                
                Produit.objects.create(
                    id_produit=max_id + 1,
                    nom=nom,
                    description=desc,
                    duree_cuisson=duree,
                    nombre_personnes=int(pers) if pers else None,
                    prix=int(prix),
                    image=image,
                    createur=createur
                )
            elif action == "edit":
                pid = request.POST.get("product_id")
                produit = Produit.objects.get(id_produit=pid)
                produit.nom = request.POST.get("nom")
                produit.description = request.POST.get("description")
                produit.duree_cuisson = request.POST.get("duree_cuisson")
                pers = request.POST.get("nombre_personnes")
                produit.nombre_personnes = int(pers) if pers else None
                prix = request.POST.get("prix")
                if prix:
                    produit.prix = int(prix)
                image = request.FILES.get("image")
                if image:
                    produit.image = image
                produit.save()
            elif action == "delete":
                pid = request.POST.get("product_id")
                Produit.objects.filter(id_produit=pid).delete()
            elif action == "add_ingredient":
                from .models import CompositionProduit, Ingredient
                pid = request.POST.get("product_id")
                ing_id = request.POST.get("ingredient_id")
                qty = request.POST.get("quantite_utilisee")
                produit = Produit.objects.get(id_produit=pid)
                ingredient = Ingredient.objects.get(id_ingredient=ing_id)
                CompositionProduit.objects.create(
                    produit=produit,
                    ingredient=ingredient,
                    quantite_utilisee=float(qty)
                )
            elif action == "remove_ingredient":
                from .models import CompositionProduit
                pid = request.POST.get("product_id")
                ing_id = request.POST.get("ingredient_id")
                CompositionProduit.objects.filter(produit_id=pid, ingredient_id=ing_id).delete()
        except Exception as e:
            pass
            
    return redirect("restaurant:products")

@login_required
def orders(request):
    context = {
        "orders": Commande.objects.select_related("client").prefetch_related(
            "lignes__produit"
        )[:100]
    }
    return render(request, "restaurant/orders.html", context)


@login_required
def inventory(request):
    from .models import VariationStock, Fournisseur, Approvisionnement
    context = {
        "stocks": Stock.objects.select_related("ingredient"),
        "low_stock_items": low_stock_items(limit=50),
        "variations": VariationStock.objects.select_related("ingredient").order_by("-date", "-id_variation")[:50],
        "fournisseurs": Fournisseur.objects.all(),
        "approvisionnements": Approvisionnement.objects.select_related("ingredient", "fournisseur").order_by("-date")[:50],
    }
    return render(request, "restaurant/inventory_redesign.html", context)


@login_required
def inventory_crud(request):
    from .models import Fournisseur, Approvisionnement, Stock, VariationStock, Ingredient
    from django.db.models import Max
    if request.method == "POST" and request.user.has_perm("restaurant.change_stock"):
        action = request.POST.get("action")
        try:
            if action == "add_fournisseur":
                nom = request.POST.get("nom")
                tel = request.POST.get("tel")
                adresse = request.POST.get("adresse")
                max_id = Fournisseur.objects.aggregate(max_id=Max("id_fournisseur"))["max_id"] or 0
                Fournisseur.objects.create(id_fournisseur=max_id + 1, nom=nom, tel=tel, adresse=adresse)
            
            elif action == "add_approvisionnement":
                ing_id = request.POST.get("ingredient_id")
                fournisseur_id = request.POST.get("fournisseur_id")
                quantite = float(request.POST.get("quantite", 0))
                prix = int(request.POST.get("prix", 0))
                
                ingredient = Ingredient.objects.get(pk=ing_id)
                fournisseur = Fournisseur.objects.get(pk=fournisseur_id)
                
                max_app_id = Approvisionnement.objects.aggregate(max_id=Max("id_approvisionnement"))["max_id"] or 0
                Approvisionnement.objects.create(
                    id_approvisionnement=max_app_id + 1,
                    ingredient=ingredient,
                    fournisseur=fournisseur,
                    date=timezone.now().date(),
                    quantite=quantite,
                    prix_unitaire=prix
                )
                
                # Update stock
                stock, created = Stock.objects.get_or_create(ingredient=ingredient, defaults={"quantite_actuelle": 0, "seuil_alerte": 0})
                if stock.quantite_actuelle is None: stock.quantite_actuelle = 0
                stock.quantite_actuelle += quantite
                stock.save()
                
                # Create VariationStock
                max_var_id = VariationStock.objects.aggregate(max_id=Max("id_variation"))["max_id"] or 0
                VariationStock.objects.create(
                    id_variation=max_var_id + 1,
                    ingredient=ingredient,
                    date=timezone.now().date(),
                    type_variation="Entrée",
                    quantite=quantite
                )
        except Exception as e:
            pass # Simple error ignoring for demo
    return redirect("restaurant:inventory")


@login_required
def employees(request):
    from .models import Poste
    from django.contrib.auth.models import User, Group
    context = {
        "employees": Employe.objects.prefetch_related("affectations__poste", "supervisions_recues__superviseur"),
        "postes": Poste.objects.all(),
        "users": User.objects.prefetch_related("groups"),
        "groups": Group.objects.all().order_by("name"),
    }
    return render(request, "restaurant/employees.html", context)


@login_required
def employee_crud(request):
    if request.method == "POST" and request.user.is_superuser:
        action = request.POST.get("action")
        try:
            if action == "add":
                nom = request.POST.get("nom")
                prenom = request.POST.get("prenom")
                tel = request.POST.get("tel")
                salaire = request.POST.get("salaire")
                image = request.FILES.get("image")
                
                max_id = Employe.objects.aggregate(max_id=Max("id_employe"))["max_id"] or 0
                
                Employe.objects.create(
                    id_employe=max_id + 1,
                    nom=nom,
                    prenom=prenom,
                    tel=tel,
                    salaire=float(salaire) if salaire else 0,
                    image=image
                )
            elif action == "edit":
                eid = request.POST.get("employee_id")
                employe = Employe.objects.get(id_employe=eid)
                employe.nom = request.POST.get("nom")
                employe.prenom = request.POST.get("prenom")
                employe.tel = request.POST.get("tel")
                salaire = request.POST.get("salaire")
                employe.salaire = float(salaire) if salaire else 0
                image = request.FILES.get("image")
                if image:
                    employe.image = image
                employe.save()
            elif action == "delete":
                eid = request.POST.get("employee_id")
                Employe.objects.filter(id_employe=eid).delete()
            elif action == "affecter_poste":
                from .models import Poste, Affectation
                eid = request.POST.get("employee_id")
                pid = request.POST.get("poste_id")
                employe = Employe.objects.get(id_employe=eid)
                poste = Poste.objects.get(id_poste=pid)
                Affectation.objects.create(
                    employe=employe,
                    poste=poste,
                    date_debut=timezone.now().date()
                )
            elif action == "ajouter_supervision":
                from .models import Supervision
                superviseur_id = request.POST.get("superviseur_id")
                employe_id = request.POST.get("employee_id")
                superviseur = Employe.objects.get(id_employe=superviseur_id)
                employe = Employe.objects.get(id_employe=employe_id)
                Supervision.objects.create(
                    superviseur=superviseur,
                    employe=employe,
                    date_debut=timezone.now().date()
                )
            elif action == "add_user":
                from django.contrib.auth.models import User, Group
                username = request.POST.get("username")
                password = request.POST.get("password")
                role_id = request.POST.get("role_id")
                
                user = User.objects.create_user(username=username, password=password)
                
                if role_id:
                    try:
                        group = Group.objects.get(id=role_id)
                        user.groups.add(group)
                        if group.name == "Administrateur":
                            user.is_superuser = True
                            user.is_staff = True
                    except Group.DoesNotExist:
                        pass
                
                user.save()
        except Exception as e:
            pass
            
    return redirect("restaurant:employees")


@login_required
def payroll(request):
    from django.utils import timezone
    context = {
        "employees": Employe.objects.prefetch_related("affectations__poste"),
        "current_month": timezone.now(),
    }
    return render(request, "restaurant/payroll.html", context)
    

@login_required
def operations(request):
    from .models import Equipement, Vehicule, ActionMarketing, RestaurantTable
    context = {
        "equipements": Equipement.objects.all(),
        "vehicules": Vehicule.objects.all(),
        "campagnes": ActionMarketing.objects.all().order_by("-date_debut"),
        "tables": RestaurantTable.objects.all(),
    }
    return render(request, "restaurant/operations.html", context)


@login_required
def operations_crud(request):
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "add_equipement" and request.user.has_perm("restaurant.add_equipement"):
                from .models import Equipement
                from django.db.models import Max
                max_id = Equipement.objects.aggregate(max_id=Max("id_equipement"))["max_id"] or 0
                Equipement.objects.create(
                    id_equipement=max_id + 1,
                    nom=request.POST.get("nom"),
                    etat=request.POST.get("etat"),
                    valeur=int(request.POST.get("valeur") or 0)
                )
            elif action == "add_vehicule" and request.user.has_perm("restaurant.add_vehicule"):
                from .models import Vehicule
                from django.db.models import Max
                max_id = Vehicule.objects.aggregate(max_id=Max("id_vehicule"))["max_id"] or 0
                Vehicule.objects.create(
                    id_vehicule=max_id + 1,
                    immatriculation=request.POST.get("immatriculation"),
                    modele=request.POST.get("modele"),
                    etat=request.POST.get("etat")
                )
            elif action == "add_marketing" and request.user.has_perm("restaurant.add_marketing"):
                from .models import ActionMarketing
                from django.db.models import Max
                max_id = ActionMarketing.objects.aggregate(max_id=Max("id_campagne"))["max_id"] or 0
                ActionMarketing.objects.create(
                    id_campagne=max_id + 1,
                    nom=request.POST.get("nom"),
                    canal=request.POST.get("canal"),
                    date_debut=request.POST.get("date_debut"),
                    date_fin=request.POST.get("date_fin"),
                    budget=int(request.POST.get("budget") or 0)
                )
            elif action == "add_table":
                from .models import RestaurantTable
                from django.db.models import Max
                max_id = RestaurantTable.objects.aggregate(max_id=Max("id_table"))["max_id"] or 0
                RestaurantTable.objects.create(
                    id_table=max_id + 1,
                    numero_table=request.POST.get("numero_table"),
                    capacite=int(request.POST.get("capacite") or 2),
                    commentaire=request.POST.get("commentaire")
                )
        except Exception as e:
            pass
    return redirect("restaurant:operations")


@login_required
def finance(request):
    context = {
        "invoices": Facture.objects.all()[:100],
    }
    return render(request, "restaurant/finance.html", context)


# Map static high-quality images and real-life prices aligned with SQL seed data
PRICES_MAP = {
    1: 5000,  # Poulet DG
    2: 8000,  # Ndolé
    3: 4500,  # Riz sauté
    4: 1500,  # Jus de Gingembre
    5: 1200,  # Jus de Bissap
}

IMAGES_MAP = {
    1: "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&auto=format&fit=crop&q=80",  # Poulet DG
    2: "https://images.unsplash.com/photo-1547058881-aa0edd92aab3?w=500&auto=format&fit=crop&q=80",  # Ndolé
    3: "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop&q=80",  # Riz sauté
    4: "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=500&auto=format&fit=crop&q=80",  # Jus de Gingembre
    5: "https://images.unsplash.com/photo-1497534446932-c925b458314e?w=500&auto=format&fit=crop&q=80",  # Jus de Bissap
}

@login_required
def pos_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            items = data.get("items", [])
            if not items:
                return JsonResponse({"success": False, "error": "Le panier est vide."}, status=400)

            client_id = data.get("client_id")
            mode_de_paiement = data.get("mode_de_paiement", "Espèces")
            type_commande = data.get("type_commande", "Sur place")

            client = Client.objects.filter(id_client=client_id).first() if client_id else None

            with transaction.atomic():
                # Get next Commande ID
                max_cmd_id = Commande.objects.aggregate(max_id=Max("id_commande"))["max_id"] or 0
                new_cmd_id = max_cmd_id + 1

                # Calculate total amount
                total_amount = 0
                lines_to_create = []

                for item in items:
                    prod_id = int(item["product_id"])
                    qty = float(item["quantity"])
                    product = Produit.objects.get(id_produit=prod_id)
                    price = product.prix
                    total_amount += int(price * qty)

                    lines_to_create.append({
                        "produit": product,
                        "quantite": qty,
                        "prix_unitaire": price
                    })

                # Create Commande
                commande = Commande.objects.create(
                    id_commande=new_cmd_id,
                    client=client,
                    date=timezone.now(),
                    type_commande=type_commande,
                    montant_total=total_amount,
                    mode_de_paiement=mode_de_paiement,
                    statut_cuisine="En attente"
                )

                # Create LigneCommandes
                for line in lines_to_create:
                    LigneCommande.objects.create(
                        commande=commande,
                        produit=line["produit"],
                        quantite=line["quantite"],
                        prix_unitaire=line["prix_unitaire"]
                    )
                    
                    # Deduct stock
                    from .models import CompositionProduit, VariationStock
                    compositions = CompositionProduit.objects.filter(produit=line["produit"])
                    for comp in compositions:
                        if comp.quantite_utilisee and comp.ingredient and hasattr(comp.ingredient, 'stock'):
                            qty_needed = comp.quantite_utilisee * line["quantite"]
                            stock = comp.ingredient.stock
                            if stock.quantite_actuelle is not None:
                                stock.quantite_actuelle -= qty_needed
                                stock.save()
                                max_var_id = VariationStock.objects.aggregate(max_id=Max("id_variation"))["max_id"] or 0
                                VariationStock.objects.create(
                                    id_variation=max_var_id + 1,
                                    ingredient=comp.ingredient,
                                    date=timezone.now().date(),
                                    type_variation="Sortie",
                                    quantite=qty_needed
                                )

                # Create Facture
                max_fac_id = Facture.objects.aggregate(max_id=Max("id_facture"))["max_id"] or 0
                Facture.objects.create(
                    id_facture=max_fac_id + 1,
                    date=timezone.now().date(),
                    montant=total_amount,
                    type_facture="Facture Client"
                )

            return JsonResponse({"success": True, "invoice_id": max_fac_id + 1, "order_id": new_cmd_id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    # GET request
    db_products = Produit.objects.all()
    products_list = []
    for p in db_products:
        products_list.append({
            "id": p.id_produit,
            "nom": p.nom,
            "description": p.description or "Plat délicieux du chef",
            "duree_cuisson": p.duree_cuisson or "15 mins",
            "prix": p.prix,
            "image": p.image.url if p.image else "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        })

    tables = RestaurantTable.objects.all()
    clients = Client.objects.all()

    context = {
        "products": products_list,
        "tables": tables,
        "clients": clients,
    }
    return render(request, "restaurant/pos.html", context)

def landing_page(request):
    db_products = Produit.objects.all()[:3]
    products_list = [
        {
            "id": p.id_produit,
            "nom": p.nom,
            "description": p.description or "Plat délicieux du chef",
            "duree_cuisson": p.duree_cuisson or "15 min",
            "prix": p.prix,
            "image": p.image.url if p.image else "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        }
        for p in db_products
    ]
    return render(request, "restaurant/landing.html", {"featured_products": products_list})


def client_reservation(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type", "cart_order")
        
        try:
            if form_type == "table_reservation":
                # ---- Réservation de table ----
                nom   = request.POST.get("nom", "").strip()
                tel   = request.POST.get("tel", "").strip()
                date_str   = request.POST.get("date")
                heure_str  = request.POST.get("heure")
                nb_persons = request.POST.get("nb_personnes", 2)
                commentaire = request.POST.get("commentaire", "")

                # Find or create Client
                client = Client.objects.filter(tel=tel).first()
                if not client:
                    max_c = Client.objects.aggregate(m=Max("id_client"))["m"] or 0
                    client = Client.objects.create(
                        id_client=max_c + 1, nom=nom, tel=tel, type_de_client="Régulier"
                    )

                # Create a Commande of type "Réservation" with zero amount
                max_cmd_id = Commande.objects.aggregate(m=Max("id_commande"))["m"] or 0
                from django.utils.dateparse import parse_date, parse_time
                from datetime import datetime as dt
                date_obj = parse_date(date_str) if date_str else timezone.now().date()
                heure_obj = parse_time(heure_str) if heure_str else None
                combined = dt.combine(date_obj, heure_obj) if heure_obj else dt.combine(date_obj, dt.min.time())
                commande = Commande.objects.create(
                    id_commande=max_cmd_id + 1,
                    client=client,
                    date=timezone.make_aware(combined),
                    type_commande="Réservation",
                    montant_total=0,
                    mode_de_paiement="Sur place",
                    statut_cuisine="En attente",
                )
                return render(request, "restaurant/client_reservation_success.html", {
                    "commande": commande,
                    "mode": "reservation",
                    "nb_personnes": nb_persons,
                    "commentaire": commentaire,
                })

            else:
                # ---- Commande panier multi-produits ----
                nom  = request.POST.get("nom", "").strip()
                tel  = request.POST.get("tel", "").strip()
                type_livraison = request.POST.get("type_livraison", "À emporter")
                mode_paiement = request.POST.get("mode_de_paiement", "À la livraison")

                # Cart items come as repeated fields: product_ids[] and quantities[]
                product_ids = request.POST.getlist("product_ids[]")
                quantities  = request.POST.getlist("quantities[]")

                if not product_ids:
                    raise ValueError("Le panier est vide.")

                # Find or create Client
                client = Client.objects.filter(tel=tel).first()
                if not client:
                    max_c = Client.objects.aggregate(m=Max("id_client"))["m"] or 0
                    client = Client.objects.create(
                        id_client=max_c + 1, nom=nom, tel=tel, type_de_client="Régulier"
                    )

                with transaction.atomic():
                    max_cmd_id = Commande.objects.aggregate(m=Max("id_commande"))["m"] or 0
                    total_amount = 0
                    lines_to_create = []

                    for pid_str, qty_str in zip(product_ids, quantities):
                        product = Produit.objects.get(id_produit=int(pid_str))
                        qty = max(float(qty_str), 1)
                        price = product.prix
                        total_amount += int(price * qty)
                        lines_to_create.append((product, qty, price))

                    commande = Commande.objects.create(
                        id_commande=max_cmd_id + 1,
                        client=client,
                        date=timezone.now(),
                        type_commande=type_livraison,
                        montant_total=total_amount,
                        mode_de_paiement=mode_paiement,
                        statut_cuisine="En attente",
                    )

                    from .models import CompositionProduit, VariationStock

                    for product, qty, price in lines_to_create:
                        LigneCommande.objects.create(
                            commande=commande,
                            produit=product,
                            quantite=qty,
                            prix_unitaire=price,
                        )
                        # Deduct stock
                        for comp in CompositionProduit.objects.filter(produit=product):
                            if comp.quantite_utilisee and comp.ingredient and hasattr(comp.ingredient, "stock"):
                                qty_needed = comp.quantite_utilisee * qty
                                stock = comp.ingredient.stock
                                if stock.quantite_actuelle is not None:
                                    stock.quantite_actuelle -= qty_needed
                                    stock.save()
                                    max_var = VariationStock.objects.aggregate(m=Max("id_variation"))["m"] or 0
                                    VariationStock.objects.create(
                                        id_variation=max_var + 1,
                                        ingredient=comp.ingredient,
                                        date=timezone.now().date(),
                                        type_variation="Sortie",
                                        quantite=qty_needed,
                                    )

                return render(request, "restaurant/client_reservation_success.html", {
                    "commande": commande, "mode": "order"
                })

        except Exception as e:
            db_products = Produit.objects.all()
            products_list = [
                {
                    "id": p.id_produit,
                    "nom": p.nom,
                    "description": p.description or "Plat délicieux du chef",
                    "duree_cuisson": p.duree_cuisson or "15 min",
                    "prix": p.prix,
                    "image": p.image.url if p.image else "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
                }
                for p in db_products
            ]
            return render(request, "restaurant/booking.html", {
                "products": products_list,
                "error": str(e),
                "tables": RestaurantTable.objects.all(),
            })

    # GET
    db_products = Produit.objects.all()
    products_list = [
        {
            "id": p.id_produit,
            "nom": p.nom,
            "description": p.description or "Plat délicieux du chef",
            "duree_cuisson": p.duree_cuisson or "15 min",
            "prix": p.prix,
            "image": p.image.url if p.image else "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        }
        for p in db_products
    ]
    return render(request, "restaurant/booking.html", {
        "products": products_list,
        "tables": RestaurantTable.objects.all(),
    })


@login_required
@permission_required("restaurant.view_cuisine", raise_exception=True)
def kitchen_view(request):
    # Only show commands that are not 'Prête' and that have products (lignes)
    pending_orders = Commande.objects.exclude(statut_cuisine="Prête").prefetch_related("lignes__produit").order_by("date")
    return render(request, "restaurant/kitchen.html", {"pending_orders": pending_orders})

@login_required
@permission_required("restaurant.change_statut_cuisine", raise_exception=True)
def update_order_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")
            new_status = data.get("status")
            
            commande = Commande.objects.get(id_commande=order_id)
            if new_status in ["En attente", "En cours", "Prête"]:
                commande.statut_cuisine = new_status
                commande.save()
                
                if new_status == "Prête":
                    from django.db.models import Max
                    from .models import Facture
                    facture_type = f"Commande #{commande.id_commande}"
                    if not Facture.objects.filter(type_facture=facture_type).exists():
                        max_facture_id = Facture.objects.aggregate(max_id=Max("id_facture"))["max_id"] or 0
                        Facture.objects.create(
                            id_facture=max_facture_id + 1,
                            date=commande.date.date() if commande.date else timezone.now().date(),
                            montant=commande.montant_total,
                            type_facture=facture_type
                        )
                        
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Statut invalide."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

@login_required
def profile_view(request):
    return render(request, "restaurant/profile.html", {"user": request.user})
