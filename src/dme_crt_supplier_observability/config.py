"""Configuration values for the local validation pipeline."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "automation" / "database" / "schema.sql"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "runtime" / "supplier_observability.sqlite"
SAMPLE_INPUT_DIR = PROJECT_ROOT / "data" / "sample_input"
DEFAULT_SAMPLE_FILE = SAMPLE_INPUT_DIR / "supplier_product_records_sample.csv"
RUN_REPORT_DIR = PROJECT_ROOT / "outputs" / "run_reports"
PHASE_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

REQUIRED_COLUMNS = [
    "supplier_name",
    "manufacturer",
    "model",
    "sku",
    "mpn",
    "product_category",
    "product_type",
    "hcpcs_candidate",
    "compatible_chair_family",
    "documentation_source",
    "listing_status",
    "compatibility_notes",
]

VALID_PRODUCT_CATEGORIES = {
    "power_wheelchair",
    "controller",
    "seating",
    "positioning",
    "electronics",
    "mobility_accessory",
    "service_part",
}

VALID_PRODUCT_TYPES = {
    "accessory",
    "battery_charger",
    "electronic_module",
    "headrest",
    "joystick_controller",
    "mounting_hardware",
    "power_chair_base",
    "replacement_part",
    "seating_cushion",
    "standing_power_chair",
}

CATEGORY_TYPE_MAP = {
    "power_wheelchair": {"power_chair_base", "standing_power_chair"},
    "controller": {"joystick_controller", "electronic_module"},
    "seating": {"seating_cushion", "headrest"},
    "positioning": {"headrest", "mounting_hardware"},
    "electronics": {"battery_charger", "electronic_module", "joystick_controller"},
    "mobility_accessory": {"accessory", "mounting_hardware"},
    "service_part": {"replacement_part", "electronic_module", "accessory"},
}

COMPATIBILITY_SENSITIVE_TYPES = {
    "battery_charger",
    "electronic_module",
    "headrest",
    "joystick_controller",
    "mounting_hardware",
    "seating_cushion",
}

MISSING_MARKERS = {"", "missing", "n/a", "na", "none", "unknown", "not provided"}
