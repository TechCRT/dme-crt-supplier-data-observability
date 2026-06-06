PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pipeline_logs (
    pipeline_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,
    script_source TEXT NOT NULL,
    source_filename TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    total_rows_detected INTEGER NOT NULL DEFAULT 0,
    rows_passed INTEGER NOT NULL DEFAULT 0,
    rows_warning INTEGER NOT NULL DEFAULT 0,
    rows_rejected_validation INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'WARNING', 'FAILED')),
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS validation_errors (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    source_filename TEXT,
    row_number INTEGER,
    field_name TEXT,
    rejected_value TEXT,
    validation_rule TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'ERROR')),
    validation_status TEXT NOT NULL CHECK (validation_status IN ('PASS', 'WARNING', 'REJECT')),
    error_message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES pipeline_logs(run_id)
);

CREATE TABLE IF NOT EXISTS file_intake_registry (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    source_filename TEXT NOT NULL,
    source_path TEXT NOT NULL,
    detected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    file_status TEXT NOT NULL CHECK (
        file_status IN ('DETECTED', 'PROCESSED', 'PROCESSED_WITH_FINDINGS', 'FAILED')
    ),
    file_hash TEXT,
    row_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (run_id) REFERENCES pipeline_logs(run_id)
);

CREATE TABLE IF NOT EXISTS product_record_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    source_filename TEXT,
    row_number INTEGER NOT NULL,
    supplier_name TEXT,
    manufacturer TEXT,
    model TEXT,
    sku TEXT,
    mpn TEXT,
    product_category TEXT,
    product_type TEXT,
    hcpcs_candidate TEXT,
    compatible_chair_family TEXT,
    documentation_source TEXT,
    listing_status TEXT,
    compatibility_notes TEXT,
    validation_status TEXT NOT NULL CHECK (validation_status IN ('PASS', 'WARNING', 'REJECT')),
    needs_review INTEGER NOT NULL CHECK (needs_review IN (0, 1)),
    warning_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    source_row_hash TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES pipeline_logs(run_id)
);

CREATE INDEX IF NOT EXISTS idx_validation_errors_run_id ON validation_errors(run_id);
CREATE INDEX IF NOT EXISTS idx_validation_errors_severity ON validation_errors(severity);
CREATE INDEX IF NOT EXISTS idx_file_intake_registry_run_id ON file_intake_registry(run_id);
CREATE INDEX IF NOT EXISTS idx_product_record_audit_run_id ON product_record_audit(run_id);
CREATE INDEX IF NOT EXISTS idx_product_record_audit_status ON product_record_audit(validation_status);
