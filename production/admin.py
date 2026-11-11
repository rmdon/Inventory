from django.contrib import admin

from .models import DataImport, FinishGood, InProcess, NotFinish, RawMaterial, SalesOrder


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "repeat_no", "customer", "due_date", "quantity", "balance", "allocated")
    search_fields = ("order_no", "repeat_no", "customer", "purchaser")
    list_filter = ("customer", "due_date", "req_closed", "allocated")


@admin.register(FinishGood)
class FinishGoodAdmin(admin.ModelAdmin):
    list_display = ("jsg_product_no", "jsg_coil_no", "repeat_no", "customer", "weight", "yard_c_r_s", "ship_hold_reason")
    search_fields = ("jsg_product_no", "jsg_coil_no", "repeat_no__order_no", "customer")


@admin.register(NotFinish)
class NotFinishAdmin(admin.ModelAdmin):
    list_display = ("jsg_product_no", "jsg_coil_no", "repeat_no", "customer", "weight", "final_line", "finish_hold_reason")
    search_fields = ("jsg_product_no", "jsg_coil_no", "repeat_no__order_no", "customer")


@admin.register(InProcess)
class InProcessAdmin(admin.ModelAdmin):
    list_display = ("jsg_coil_no", "repeat_no", "customer", "weight", "leading_process", "status")
    search_fields = ("jsg_coil_no", "repeat_no__order_no", "customer")
    list_filter = ("coil_status", "leading_process", "status")


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("jsg_coil_no", "repeat_no", "customer", "weight", "yard", "raw_material_designation")
    search_fields = ("jsg_coil_no", "repeat_no__order_no", "customer", "ship_name")


@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    list_display = ("filename", "imported_by", "status", "created_at")
    readonly_fields = ("filename", "imported_by", "status", "summary", "created_at")
