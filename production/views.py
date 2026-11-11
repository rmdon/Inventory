from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.shortcuts import redirect, render

from .models import SalesOrder, FinishGood, NotFinish, InProcess, RawMaterial, DataImport

SOURCE_MODELS = {
    "A": (FinishGood, "Finish Good"),
    "B": (NotFinish, "Not Finish"),
    "C": (InProcess, "In Process"),
    "D": (RawMaterial, "Raw Material"),
}


def _number(value):
    return float(value or 0)


def _source_totals(repeat_no):
    totals = {}
    for key, (model, _) in SOURCE_MODELS.items():
        rows = model.objects.filter(repeat_no_id=repeat_no)
        weight_field = {"A": "end_weight", "B": "weight_end", "C": "end_weight", "D": "end_weight"}[key]
        totals[key] = _number(rows.aggregate(total=Sum(weight_field))["total"])
    return totals


def _status(order, totals):
    if order.due_date and order.due_date < date.today() and _number(order.balance) > 0:
        return "Kritis"
    if _number(order.balance) > sum(totals.values()):
        return "Perlu perhatian"
    return "Aman"


def _filtered_orders(request):
    orders = SalesOrder.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        orders = orders.filter(Q(order_no__icontains=query) | Q(repeat_no__icontains=query) |
                               Q(customer__icontains=query) | Q(purchaser__icontains=query))
    customer = request.GET.get("customer", "")
    if customer:
        orders = orders.filter(customer=customer)
    purchaser = request.GET.get("purchaser", "")
    if purchaser:
        orders = orders.filter(purchaser=purchaser)
    date_from, date_to = request.GET.get("date_from"), request.GET.get("date_to")
    if date_from:
        orders = orders.filter(due_date__gte=date_from)
    if date_to:
        orders = orders.filter(due_date__lte=date_to)
    return orders, query


@login_required
def dashboard(request):
    orders, _ = _filtered_orders(request)
    open_orders = orders.exclude(req_closed__iexact="Y")
    kpis = [
        {"label": "Sales Order terbuka", "value": open_orders.count(), "unit": "order"},
        {"label": "Total balance", "value": _number(open_orders.aggregate(v=Sum("balance"))["v"]), "unit": "ton"},
        {"label": "Finish Good", "value": FinishGood.objects.count(), "unit": "coil"},
        {"label": "Not Finish", "value": NotFinish.objects.count(), "unit": "coil"},
        {"label": "In Process", "value": InProcess.objects.count(), "unit": "coil"},
        {"label": "Raw Material", "value": RawMaterial.objects.count(), "unit": "coil"},
    ]
    monthly = defaultdict(float)
    status_counts = defaultdict(int)
    priorities = []
    for order in open_orders.order_by("due_date"):
        if order.due_date:
            monthly[order.due_date.strftime("%Y-%m")] += _number(order.balance)
        totals = _source_totals(order.repeat_no)
        status = _status(order, totals)
        status_counts[status] += 1
        if status != "Aman":
            priorities.append({"order_no": order.order_no, "repeat_no": order.repeat_no,
                               "customer": order.customer, "due_date": order.due_date,
                               "balance": order.balance, "status": status})
    max_month = max(monthly.values(), default=0)
    max_status = max(status_counts.values(), default=0)
    latest_import = DataImport.objects.first()
    return render(request, "production/dashboard.html", {
        "kpis": kpis, "active_nav": "dashboard",
        "monthly_items": [{"label": label, "value": round(value, 3),
                           "percent": round(value / max_month * 100) if max_month else 0}
                          for label, value in sorted(monthly.items())],
        "status_items": [{"label": label, "value": value,
                          "percent": round(value / max_status * 100) if max_status else 0}
                         for label, value in status_counts.items()],
        "priority_orders": priorities[:8],
        "last_updated": latest_import.created_at.strftime("%d %b %Y %H:%M") if latest_import else "Belum ada impor",
        "customers": SalesOrder.objects.values_list("customer", flat=True).distinct().order_by("customer"),
        "purchasers": SalesOrder.objects.values_list("purchaser", flat=True).distinct().order_by("purchaser"),
    })


@login_required
def sales_orders(request):
    source = request.GET.get("source", "ALL").upper()
    if source not in ("ALL", *SOURCE_MODELS.keys()):
        source = "ALL"
    orders, query = _filtered_orders(request)
    if source in SOURCE_MODELS:
        model, _ = SOURCE_MODELS[source]
        matching = model.objects.values_list("repeat_no_id", flat=True).distinct()
        orders = orders.filter(repeat_no__in=matching)
    order_rows = []
    for order in orders.order_by("due_date", "order_no"):
        totals = _source_totals(order.repeat_no)
        order_rows.append({
            "order_no": order.order_no, "repeat_no": order.repeat_no, "customer": order.customer,
            "purchaser": order.purchaser, "designation": order.designation, "due_date": order.due_date,
            "quantity": order.quantity, "shipped": order.shipped, "balance": order.balance,
            "source_totals": totals, "selected_source_total": totals.get(source, 0),
            "status": _status(order, totals),
        })
    page_obj = Paginator(order_rows, 10).get_page(request.GET.get("page"))
    customers = SalesOrder.objects.order_by("customer").values_list("customer", flat=True).distinct()
    return render(request, "production/sales_orders.html", {
        "sales_orders": page_obj.object_list, "page_obj": page_obj, "active_nav": "sales_orders", "active_source": source,
        "active_tab": "tracker" if request.GET.get("tab") == "tracker" else "orders",
        "query": query, "source_choices": [("ALL", "Semua"), *((k, v[1]) for k, v in SOURCE_MODELS.items())],
        "customers": customers, "selected_customer": request.GET.get("customer", ""),
    })


@login_required
def import_data(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses untuk mengimpor data.")
        return redirect("sales_orders")
    result = None
    if request.method == "POST" and request.FILES.get("workbook"):
        if request.POST.get("confirm") != "yes":
            messages.error(request, "Konfirmasi impor diperlukan.")
        else:
            from .importer import import_workbook
            raw_result = import_workbook(request.FILES["workbook"], imported_by=request.user.get_username())
            counts = raw_result.get("counts", {})
            processed = sum(item.get("rows", 0) for item in counts.values())
            succeeded = sum(item.get("created", 0) + item.get("updated", 0) for item in counts.values())
            errors = raw_result.get("errors", [])
            result = {
                "filename": raw_result.get("filename"), "processed": processed,
                "success": succeeded if raw_result.get("status") == "completed" else 0,
                "failed": len(errors), "errors": [f"{e.get('sheet', '')} baris {e.get('row') or '—'}: {e.get('message')}" for e in errors],
            }
            if raw_result.get("status") == "completed":
                messages.success(request, "Impor workbook berhasil disimpan.")
            else:
                messages.error(request, "Workbook tidak diimpor karena ada masalah validasi.")
    return render(request, "production/import.html", {"result": result, "active_nav": "imports"})

