from django.db import models


class DataImport(models.Model):
    """Audit record for an imported workbook."""

    filename = models.CharField(max_length=255)
    imported_by = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, default="completed")
    summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.status})"


class SalesOrder(models.Model):
    repeat_no = models.CharField(max_length=40, primary_key=True)
    purchaser = models.CharField(max_length=100, blank=True)
    customer = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    order_no = models.CharField(max_length=80, blank=True, db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    month_due_date = models.CharField(max_length=20, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    shipped = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    shipped_of_previous_month = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    shipped_of_current_month = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    finishing_products = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    waiting_finish = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    in_process = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    raw_material_jsg = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    not_allotment = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    comp_mark = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    imitation_order = models.CharField(max_length=100, blank=True)
    reference_number_for_purchaser_4 = models.CharField(max_length=100, blank=True)
    allowance = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    min_packing = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    balance = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    req_closed = models.CharField(max_length=10, blank=True)
    allocated = models.CharField(max_length=10, blank=True)
    upload_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "order_no"]
        indexes = [models.Index(fields=["customer", "due_date"])]

    def __str__(self):
        return self.order_no or self.repeat_no


class InventoryRecord(models.Model):
    repeat_no = models.ForeignKey(SalesOrder, to_field="repeat_no", on_delete=models.CASCADE)
    jsg_coil_no = models.CharField(max_length=80, blank=True, db_index=True)
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["repeat_no", "jsg_coil_no"])]


class FinishGood(InventoryRecord):
    jsg_product_no = models.CharField(max_length=80, blank=True)
    order_no1 = models.CharField(max_length=80, blank=True)
    order_no2 = models.CharField(max_length=80, blank=True)
    customer = models.CharField(max_length=100, blank=True)
    purchaser = models.CharField(max_length=100, blank=True)
    delivery_place = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    length = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    target_grade_cd = models.CharField(max_length=80, blank=True)
    cgl_working_date = models.DateField(null=True, blank=True)
    finishing_date = models.DateField(null=True, blank=True)
    order_due_date = models.DateField(null=True, blank=True)
    required_delivery_date = models.DateField(null=True, blank=True)
    yard_c_r_s = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    ship_hold_reason = models.TextField(blank=True)
    kategori = models.CharField(max_length=80, blank=True)
    probabilitas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    end_weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    upload_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(InventoryRecord.Meta):
        ordering = ["repeat_no", "jsg_coil_no"]
        constraints = [models.UniqueConstraint(fields=["repeat_no", "jsg_coil_no"], name="uq_fg_repeat_coil")]

    def __str__(self):
        return self.jsg_product_no or self.jsg_coil_no or str(self.pk)


class NotFinish(InventoryRecord):
    jsg_product_no = models.CharField(max_length=80, blank=True)
    cgl_working_date = models.DateTimeField(null=True, blank=True)
    final_line = models.CharField(max_length=80, blank=True)
    final_line_date = models.DateTimeField(null=True, blank=True)
    rslt_cd = models.CharField(max_length=40, blank=True)
    delivery_place = models.CharField(max_length=100, blank=True)
    customer = models.CharField(max_length=100, blank=True)
    purchaser = models.CharField(max_length=100, blank=True)
    jsg_designation = models.CharField(max_length=100, blank=True)
    thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    target_grade_cd = models.CharField(max_length=80, blank=True)
    yard_c_r_s = models.CharField(max_length=100, blank=True)
    ship_hold_reason = models.TextField(blank=True)
    finish_hold_reason = models.TextField(blank=True)
    count_ng = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hold_number = models.CharField(max_length=80, blank=True)
    remarks_hold = models.TextField(blank=True)
    kategori = models.CharField(max_length=80, blank=True)
    probabilitas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    weight_end = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    product_051 = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    upload_batch = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(InventoryRecord.Meta):
        ordering = ["repeat_no", "jsg_coil_no"]
        constraints = [models.UniqueConstraint(fields=["repeat_no", "jsg_coil_no"], name="uq_nf_repeat_coil")]


class InProcess(InventoryRecord):
    coil_status = models.CharField(max_length=80, blank=True)
    leading_process = models.CharField(max_length=100, blank=True)
    leading_process_date_shift = models.CharField(max_length=80, blank=True)
    rslt_cd = models.CharField(max_length=40, blank=True)
    post_process = models.CharField(max_length=100, blank=True)
    actual_coil_thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    actual_coil_width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    yard_c_r_s = models.CharField(max_length=100, blank=True)
    order_no1 = models.CharField(max_length=80, blank=True)
    order_no2 = models.CharField(max_length=80, blank=True)
    order_due_date = models.DateField(null=True, blank=True)
    delivery_place = models.CharField(max_length=100, blank=True)
    customer = models.CharField(max_length=100, blank=True)
    purchaser = models.CharField(max_length=100, blank=True)
    product_category = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    order_thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    order_width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    imitation_order = models.CharField(max_length=100, blank=True)
    target_grade_cd = models.CharField(max_length=80, blank=True)
    instructed_date = models.DateField(null=True, blank=True)
    cgl_working_date = models.DateField(null=True, blank=True)
    facility = models.CharField(max_length=100, blank=True)
    trim_width = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    total_trim = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    status = models.CharField(max_length=80, blank=True)
    cp = models.CharField(max_length=255, blank=True)
    probabilitas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    end_weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(InventoryRecord.Meta):
        ordering = ["repeat_no", "jsg_coil_no"]
        constraints = [models.UniqueConstraint(fields=["repeat_no", "jsg_coil_no"], name="uq_ip_repeat_coil")]


class RawMaterial(InventoryRecord):
    weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    yard = models.CharField(max_length=100, blank=True)
    class_name = models.CharField(max_length=80, blank=True)
    ship_name = models.CharField(max_length=100, blank=True)
    maker_shipped_date = models.DateTimeField(null=True, blank=True)
    outside_warehouse_accept_date = models.DateTimeField(null=True, blank=True)
    jsg_accept_date = models.DateTimeField(null=True, blank=True)
    raw_material_designation = models.CharField(max_length=100, blank=True)
    raw_material_thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    raw_material_width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    customer = models.CharField(max_length=100, blank=True)
    purchaser = models.CharField(max_length=100, blank=True)
    order_designation = models.CharField(max_length=100, blank=True)
    designation_jsg = models.CharField(max_length=100, blank=True)
    order_thickness = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    order_width = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    order_no1 = models.CharField(max_length=80, blank=True)
    kategori = models.CharField(max_length=80, blank=True)
    probabilitas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    end_weight = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(InventoryRecord.Meta):
        ordering = ["repeat_no", "jsg_coil_no"]
        constraints = [models.UniqueConstraint(fields=["repeat_no", "jsg_coil_no"], name="uq_rm_repeat_coil")]
