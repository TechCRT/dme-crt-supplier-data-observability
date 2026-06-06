# Validation Rules

The validator applies public-safe product-data quality rules to each CSV row. Row status is derived from finding severity:

- `PASS`: no findings
- `WARNING`: one or more `WARNING` findings and no `ERROR` findings
- `REJECT`: one or more `ERROR` findings

Phase 4 keeps the Phase 1 validation rules and severity choices unchanged.

## Rules

| Rule | Field | Severity | Description |
| --- | --- | --- | --- |
| `required_supplier_name` | `supplier_name` | `ERROR` | Supplier name is required for intake accountability. |
| `required_manufacturer` | `manufacturer` | `ERROR` | Manufacturer is required for product traceability. |
| `required_model` | `model` | `ERROR` | Model is required for review and downstream matching. |
| `required_sku_or_mpn` | `sku`, `mpn` | `ERROR` | At least one supplier SKU or manufacturer part number is required. |
| `valid_product_category` | `product_category` | `ERROR` | Category must be in the supported sample taxonomy. |
| `valid_product_type` | `product_type` | `ERROR` | Product type must be in the supported sample taxonomy. |
| `category_type_alignment` | `product_type` | `WARNING` | Product type is valid but unusual for the selected category. |
| `hcpcs_candidate_present` | `hcpcs_candidate` | `WARNING` | HCPCS-like classification-support field is blank. |
| `hcpcs_candidate_format` | `hcpcs_candidate` | `ERROR` | HCPCS-like value must match one letter followed by four digits. |
| `documentation_source_present` | `documentation_source` | `WARNING` | Documentation source is missing or not reviewable. |
| `compatibility_notes_present` | `compatibility_notes` | `WARNING` | Compatibility-sensitive products need review notes. |
| `duplicate_sku` | `sku` | `ERROR` | Supplier SKU appears more than once in the input file. |
| `duplicate_mpn` | `mpn` | `ERROR` | Manufacturer part number appears more than once in the input file. |

## Supported Sample Categories

- `power_wheelchair`
- `controller`
- `seating`
- `positioning`
- `electronics`
- `mobility_accessory`
- `service_part`

## Supported Sample Product Types

- `accessory`
- `battery_charger`
- `electronic_module`
- `headrest`
- `joystick_controller`
- `mounting_hardware`
- `power_chair_base`
- `replacement_part`
- `seating_cushion`
- `standing_power_chair`

## Public-Safe Boundary

HCPCS-like values are classification-support examples only and are not billing guidance. These rules do not automate reimbursement, payer policy, clinical decisions, or production listing publication.

## Future Re-Entry Warnings

- Any severity change must update tests, documentation, DAX assumptions, and phase reports together.
- Keep warning rows separate from rejected rows in analytics and workflow routing.
- Do not add private-data validation examples to this public portfolio project.
