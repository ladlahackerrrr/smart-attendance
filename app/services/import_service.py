"""Excel Import service stub."""

def parse_excel(file_path):
    return {"headers": [], "rows": [], "errors": []}

def validate_import_data(rows):
    return {"valid_rows": [], "errors": [], "warnings": []}

def preview_import(file_path):
    return {"valid_rows": [], "errors": [], "warnings": []}

def execute_import(valid_rows):
    return {"imported_count": 0, "errors": []}
