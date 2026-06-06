// Power Query / M template for the DME/CRT Supplier Data Validation dashboard.
// Source: SQLite database through an ODBC DSN.
// Replace the DSN value with the local DSN that points to data/runtime/supplier_observability.sqlite.

let
    OdbcConnectionString = "dsn=DME_CRT_SUPPLIER_OBSERVABILITY",

    NormalizeTextValue = (value as any) as nullable text =>
        let
            asText = if value = null then null else Text.Trim(Text.From(value)),
            normalized = if asText = null or asText = "" then null else asText
        in
            normalized,

    NormalizeTextColumns = (sourceTable as table, columnNames as list) as table =>
        List.Accumulate(
            columnNames,
            sourceTable,
            (state as table, columnName as text) =>
                if Table.HasColumns(state, columnName)
                then Table.TransformColumns(state, {{columnName, each NormalizeTextValue(_), type nullable text}})
                else state
        ),

    AddDateHelpers = (sourceTable as table, sourceColumn as text, prefix as text) as table =>
        let
            withDateTime = Table.AddColumn(
                sourceTable,
                prefix & "_datetime",
                each try DateTime.FromText(Record.Field(_, sourceColumn)) otherwise null,
                type nullable datetime
            ),
            withDate = Table.AddColumn(
                withDateTime,
                prefix & "_date",
                each if Record.Field(_, prefix & "_datetime") = null then null else Date.From(Record.Field(_, prefix & "_datetime")),
                type nullable date
            ),
            withHour = Table.AddColumn(
                withDate,
                prefix & "_hour",
                each if Record.Field(_, prefix & "_datetime") = null then null else Time.Hour(Time.From(Record.Field(_, prefix & "_datetime"))),
                Int64.Type
            )
        in
            withHour,

    PipelineLogsRaw = Odbc.Query(
        OdbcConnectionString,
        "select pipeline_log_id, run_id, script_source, source_filename, started_at, completed_at, total_rows_detected, rows_passed, rows_warning, rows_rejected_validation, status, error_message, created_at from pipeline_logs"
    ),
    PipelineLogsTextClean = NormalizeTextColumns(
        PipelineLogsRaw,
        {"run_id", "script_source", "source_filename", "started_at", "completed_at", "status", "error_message", "created_at"}
    ),
    PipelineLogsTyped = Table.TransformColumnTypes(
        PipelineLogsTextClean,
        {
            {"pipeline_log_id", Int64.Type},
            {"total_rows_detected", Int64.Type},
            {"rows_passed", Int64.Type},
            {"rows_warning", Int64.Type},
            {"rows_rejected_validation", Int64.Type}
        }
    ),
    PipelineLogsWithStarted = AddDateHelpers(PipelineLogsTyped, "started_at", "started"),
    PipelineLogsWithCompleted = AddDateHelpers(PipelineLogsWithStarted, "completed_at", "completed"),
    PipelineLogs = Table.AddColumn(
        Table.AddColumn(
            Table.AddColumn(
                PipelineLogsWithCompleted,
                "run_has_warning_or_failure",
                each [status] <> "SUCCESS" or [rows_warning] > 0 or [rows_rejected_validation] > 0,
                type logical
            ),
            "run_success_flag",
            each [status] = "SUCCESS",
            type logical
        ),
        "run_integrity_rate",
        each if [total_rows_detected] = null or [total_rows_detected] = 0 then null else Number.From([rows_passed]) / Number.From([total_rows_detected]),
        Percentage.Type
    ),

    ValidationErrorsRaw = Odbc.Query(
        OdbcConnectionString,
        "select error_id, run_id, source_filename, row_number, field_name, rejected_value, validation_rule, severity, validation_status, error_message, created_at from validation_errors"
    ),
    ValidationErrorsTextClean = NormalizeTextColumns(
        ValidationErrorsRaw,
        {"run_id", "source_filename", "field_name", "rejected_value", "validation_rule", "severity", "validation_status", "error_message", "created_at"}
    ),
    ValidationErrorsTyped = Table.TransformColumnTypes(
        ValidationErrorsTextClean,
        {{"error_id", Int64.Type}, {"row_number", Int64.Type}}
    ),
    ValidationErrorsWithDate = AddDateHelpers(ValidationErrorsTyped, "created_at", "error_created"),
    ValidationErrors = Table.AddColumn(
        Table.AddColumn(
            ValidationErrorsWithDate,
            "is_blocking_error",
            each [severity] = "ERROR" or [validation_status] = "REJECT",
            type logical
        ),
        "is_warning_finding",
        each [severity] = "WARNING",
        type logical
    ),

    ProductRecordAuditRaw = Odbc.Query(
        OdbcConnectionString,
        "select audit_id, run_id, source_filename, row_number, supplier_name, manufacturer, model, sku, mpn, product_category, product_type, hcpcs_candidate, compatible_chair_family, documentation_source, listing_status, compatibility_notes, validation_status, needs_review, warning_count, error_count, source_row_hash, created_at from product_record_audit"
    ),
    ProductRecordAuditTextClean = NormalizeTextColumns(
        ProductRecordAuditRaw,
        {"run_id", "source_filename", "supplier_name", "manufacturer", "model", "sku", "mpn", "product_category", "product_type", "hcpcs_candidate", "compatible_chair_family", "documentation_source", "listing_status", "compatibility_notes", "validation_status", "source_row_hash", "created_at"}
    ),
    ProductRecordAuditTyped = Table.TransformColumnTypes(
        ProductRecordAuditTextClean,
        {
            {"audit_id", Int64.Type},
            {"row_number", Int64.Type},
            {"needs_review", Int64.Type},
            {"warning_count", Int64.Type},
            {"error_count", Int64.Type}
        }
    ),
    ProductRecordAuditWithDate = AddDateHelpers(ProductRecordAuditTyped, "created_at", "audit_created"),
    ProductRecordAudit = Table.AddColumn(
        Table.AddColumn(
            Table.AddColumn(
                Table.AddColumn(
                    ProductRecordAuditWithDate,
                    "needs_review_flag",
                    each [needs_review] = 1,
                    type logical
                ),
                "is_rejected_record",
                each [validation_status] = "REJECT",
                type logical
            ),
            "is_warning_record",
            each [validation_status] = "WARNING",
            type logical
        ),
        "record_integrity_weight",
        each if [validation_status] = "PASS" then 1 else if [validation_status] = "WARNING" then 0.5 else 0,
        type number
    ),

    FileIntakeRegistryRaw = Odbc.Query(
        OdbcConnectionString,
        "select file_id, run_id, source_filename, source_path, detected_at, processed_at, file_status, file_hash, row_count, notes from file_intake_registry"
    ),
    FileIntakeRegistryTextClean = NormalizeTextColumns(
        FileIntakeRegistryRaw,
        {"run_id", "source_filename", "source_path", "detected_at", "processed_at", "file_status", "file_hash", "notes"}
    ),
    FileIntakeRegistryTyped = Table.TransformColumnTypes(
        FileIntakeRegistryTextClean,
        {{"file_id", Int64.Type}, {"row_count", Int64.Type}}
    ),
    FileIntakeRegistryWithDetected = AddDateHelpers(FileIntakeRegistryTyped, "detected_at", "detected"),
    FileIntakeRegistryWithProcessed = AddDateHelpers(FileIntakeRegistryWithDetected, "processed_at", "processed"),
    FileIntakeRegistry = Table.AddColumn(
        FileIntakeRegistryWithProcessed,
        "file_has_findings",
        each [file_status] = "PROCESSED_WITH_FINDINGS" or [file_status] = "FAILED",
        type logical
    ),

    DataQualityByRun = Table.Group(
        ProductRecordAudit,
        {"run_id", "source_filename"},
        {
            {"records_total", each Table.RowCount(_), Int64.Type},
            {"records_passed", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "PASS")), Int64.Type},
            {"records_warning", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "WARNING")), Int64.Type},
            {"records_rejected", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "REJECT")), Int64.Type},
            {"records_requiring_review", each Table.RowCount(Table.SelectRows(_, each [needs_review_flag] = true)), Int64.Type},
            {"average_record_integrity_weight", each List.Average([record_integrity_weight]), type nullable number}
        }
    ),
    DataQualityByRunWithRate = Table.AddColumn(
        DataQualityByRun,
        "data_integrity_rate",
        each if [records_total] = 0 then null else Number.From([records_passed]) / Number.From([records_total]),
        Percentage.Type
    ),

    SupplierProductQuality = Table.Group(
        ProductRecordAudit,
        {"supplier_name", "manufacturer", "product_category", "product_type"},
        {
            {"records_total", each Table.RowCount(_), Int64.Type},
            {"records_passed", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "PASS")), Int64.Type},
            {"records_warning", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "WARNING")), Int64.Type},
            {"records_rejected", each Table.RowCount(Table.SelectRows(_, each [validation_status] = "REJECT")), Int64.Type},
            {"records_requiring_review", each Table.RowCount(Table.SelectRows(_, each [needs_review_flag] = true)), Int64.Type}
        }
    ),

    ErrorReviewQueue = Table.Sort(
        Table.SelectRows(
            ValidationErrors,
            each [is_blocking_error] = true or [is_warning_finding] = true
        ),
        {{"error_created_datetime", Order.Descending}, {"severity", Order.Ascending}, {"row_number", Order.Ascending}}
    )
in
    [
        PipelineLogs = PipelineLogs,
        ValidationErrors = ValidationErrors,
        ProductRecordAudit = ProductRecordAudit,
        FileIntakeRegistry = FileIntakeRegistry,
        DataQualityByRun = DataQualityByRunWithRate,
        SupplierProductQuality = SupplierProductQuality,
        ErrorReviewQueue = ErrorReviewQueue
    ]
