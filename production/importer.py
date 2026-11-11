"""Validated XLSX import for the five operational sheets."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.db import transaction
from django.db.models import DateField, DateTimeField, DecimalField, IntegerField
from django.utils import timezone
from openpyxl import load_workbook

from .models import DataImport, FinishGood, InProcess, NotFinish, RawMaterial, SalesOrder

SHEET_MODELS = {
    "Sales_Order": SalesOrder,
    "Finish_Good": FinishGood,
    "Not_Finish": NotFinish,
    "In_Process": InProcess,
    "Raw_Material": RawMaterial,
}
REQUIRED_COLUMNS = {
    "Sales_Order": {"repeat_no", "order_no"},
    "Finish_Good": {"repeat_no", "jsg_coil_no"},
    "Not_Finish": {"repeat_no", "jsg_coil_no"},
    "In_Process": {"repeat_no", "jsg_coil_no"},
    "Raw_Material": {"repeat_no", "jsg_coil_no"},
}
ALIASES = {"purchacer": "purchaser"}


def _parse_date(value, field):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date() if isinstance(field, DateField) and not isinstance(field, DateTimeField) else (timezone.make_aware(value) if timezone.is_naive(value) else value)
    if isinstance(value, date):
        return timezone.make_aware(datetime.combine(value, datetime.min.time())) if isinstance(field, DateTimeField) else value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(text, fmt)
            return timezone.make_aware(parsed) if isinstance(field, DateTimeField) else parsed.date()
        except ValueError:
            pass
    raise ValueError(f"format tanggal tidak valid: {text}")


def _convert(value, field):
    if value is None or value == "":
        return None if field.null else ""
    if isinstance(field, (DateField, DateTimeField)):
        return _parse_date(value, field)
    if isinstance(field, DecimalField):
        try:
            result = Decimal(str(value).replace(",", "").strip())
        except (InvalidOperation, ValueError):
            raise ValueError(f"angka tidak valid: {value}")
        if not result.is_finite():
            raise ValueError(f"angka tidak valid: {value}")
        if field.max_digits and len(result.as_tuple().digits) > field.max_digits:
            raise ValueError(f"angka melebihi kapasitas kolom: {value}")
        return result
    if isinstance(field, IntegerField):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"bilangan bulat tidak valid: {value}")
    return str(value).strip()


def _sheet_rows(sheet, model):
    values = sheet.iter_rows(values_only=True)
    headers = next(values, None)
    if not headers:
        raise ValueError(f"sheet {sheet.title}: header kosong")
    headers = [str(h).strip() if h is not None else "" for h in headers]
    model_fields = {f.name: f for f in model._meta.concrete_fields}
    mapped = []
    for header in headers:
        key = ALIASES.get(header, header)
        mapped.append(key if key in model_fields and key != "id" else None)
    source_headers = {h for h in headers if h}
    missing = REQUIRED_COLUMNS[sheet.title] - source_headers
    if missing:
        raise ValueError(f"sheet {sheet.title}: kolom wajib tidak ditemukan: {', '.join(sorted(missing))}")
    unique_fields = ("repeat_no",) if sheet.title == "Sales_Order" else ("repeat_no", "jsg_coil_no")
    normalized_keys = set()
    records = []
    errors = []
    for row_num, row in enumerate(values, start=2):
        if not any(v is not None and v != "" for v in row):
            continue
        raw = dict(zip(mapped, row))
        if not str(raw.get("repeat_no") or "").strip():
            errors.append({"row": row_num, "message": "repeat_no wajib diisi"})
            continue
        if sheet.title != "Sales_Order" and not str(raw.get("jsg_coil_no") or "").strip():
            errors.append({"row": row_num, "message": "jsg_coil_no wajib diisi"})
            continue
        identity = tuple(str(raw.get(name) or "").strip() for name in unique_fields)
        if identity in normalized_keys:
            errors.append({"row": row_num, "message": f"kunci duplikat dalam file: {' / '.join(identity)}"})
            continue
        normalized_keys.add(identity)
        item = {}
        try:
            for name, value in raw.items():
                if not name:
                    continue
                field = model_fields[name]
                target_name = field.attname if field.is_relation else name
                item[target_name] = _convert(value, field)
        except (ValueError, TypeError) as exc:
            errors.append({"row": row_num, "message": str(exc)})
            continue
        records.append((row_num, item, identity))
    return records, errors


def import_workbook(file_or_path, *, imported_by=None, dry_run=False):
    """Validate and import recognized sheets. Any validation error aborts all writes.

    Returns a JSON-serializable summary. In dry-run mode the workbook is validated
    and counts are estimated without writing rows or an import audit record.
    """
    filename = getattr(file_or_path, "name", None) or Path(str(file_or_path)).name
    if hasattr(file_or_path, "seek"):
        file_or_path.seek(0)
    workbook = load_workbook(file_or_path, read_only=True, data_only=True)
    prepared, errors, counts = {}, [], {}
    try:
        for sheet_name, model in SHEET_MODELS.items():
            if sheet_name not in workbook.sheetnames:
                errors.append({"sheet": sheet_name, "row": None, "message": "sheet wajib tidak ditemukan"})
                continue
            try:
                records, sheet_errors = _sheet_rows(workbook[sheet_name], model)
            except ValueError as exc:
                errors.append({"sheet": sheet_name, "row": None, "message": str(exc)})
                continue
            prepared[sheet_name] = records
            errors.extend({"sheet": sheet_name, **e} for e in sheet_errors)
            counts[sheet_name] = {"rows": len(records), "created": 0, "updated": 0}
    finally:
        workbook.close()

    if not errors and "Sales_Order" in prepared:
        incoming_orders = {identity[0] for _, _, identity in prepared["Sales_Order"]}
        existing_orders = set(SalesOrder.objects.values_list("repeat_no", flat=True))
        valid_orders = incoming_orders | existing_orders
        for sheet_name, records in prepared.items():
            if sheet_name == "Sales_Order":
                continue
            for row_num, _, identity in records:
                if identity[0] not in valid_orders:
                    errors.append({"sheet": sheet_name, "row": row_num,
                                   "message": f"repeat_no tidak ditemukan pada Sales_Order: {identity[0]}"})
    if errors:
        return {"status": "invalid", "filename": filename, "dry_run": dry_run,
                "counts": counts, "errors": errors}

    if dry_run:
        for sheet_name, records in prepared.items():
            model = SHEET_MODELS[sheet_name]
            for _, _, identity in records:
                query = ({"repeat_no": identity[0]} if model is SalesOrder else {"repeat_no_id": identity[0]}) if len(identity) == 1 else {"repeat_no_id": identity[0], "jsg_coil_no": identity[1]}
                counts[sheet_name]["updated" if model.objects.filter(**query).exists() else "created"] += 1
        return {"status": "valid", "filename": filename, "dry_run": True,
                "counts": counts, "errors": []}

    with transaction.atomic():
        for sheet_name, records in prepared.items():
            model = SHEET_MODELS[sheet_name]
            for _, values, identity in records:
                query = ({"repeat_no": identity[0]} if model is SalesOrder else {"repeat_no_id": identity[0]}) if len(identity) == 1 else {"repeat_no_id": identity[0], "jsg_coil_no": identity[1]}
                _, created = model.objects.update_or_create(**query, defaults=values)
                counts[sheet_name]["created" if created else "updated"] += 1
        log = DataImport.objects.create(
            filename=filename,
            imported_by=str(imported_by or "")[:150],
            status="completed",
            summary=counts,
        )
    return {"status": "completed", "filename": filename, "dry_run": False,
            "import_id": log.pk, "counts": counts, "errors": []}



