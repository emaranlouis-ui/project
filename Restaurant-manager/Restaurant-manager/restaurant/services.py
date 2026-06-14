from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from .models import Approvisionnement, Commande, LigneCommande, Produit, Stock


def month_bounds(year: int | None = None, month: int | None = None) -> tuple[int, int]:
    today = timezone.localdate()
    return year or today.year, month or today.month


def monthly_turnover(year: int | None = None, month: int | None = None) -> int:
    year, month = month_bounds(year, month)
    result = Commande.objects.filter(date__year=year, date__month=month).aggregate(
        total=Sum("montant_total")
    )
    return result["total"] or 0


def monthly_order_count(year: int | None = None, month: int | None = None) -> int:
    year, month = month_bounds(year, month)
    return Commande.objects.filter(date__year=year, date__month=month).count()


def monthly_supply_expenses(year: int | None = None, month: int | None = None) -> Decimal:
    year, month = month_bounds(year, month)
    line_total = ExpressionWrapper(
        F("quantite") * F("prix_unitaire"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    result = Approvisionnement.objects.filter(date__year=year, date__month=month).aggregate(
        total=Sum(line_total)
    )
    return result["total"] or Decimal("0")


def best_selling_products(limit: int = 5):
    return (
        Produit.objects.annotate(
            total_quantite=Sum("lignes_commande__quantite"),
            nombre_commandes=Count("lignes_commande__commande", distinct=True),
        )
        .filter(total_quantite__isnull=False)
        .order_by("-total_quantite", "nom")[:limit]
    )


def low_stock_items(limit: int = 10):
    return (
        Stock.objects.select_related("ingredient")
        .filter(quantite_actuelle__lte=F("seuil_alerte"))
        .order_by("quantite_actuelle")[:limit]
    )


def recompute_order_total(commande: Commande) -> int:
    total = (
        LigneCommande.objects.filter(commande=commande).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantite") * F("prix_unitaire"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
        )["total"]
        or 0
    )
    commande.montant_total = int(total)
    commande.save(update_fields=["montant_total"])
    return commande.montant_total

