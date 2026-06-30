"""Validation helpers."""

import re

def validate_email(email):
    """Validate email address format."""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Validate phone number format (simple check)."""
    if not phone:
        return True # Optional field
    pattern = r'^\+?[\d\s-]{10,15}$'
    return bool(re.match(pattern, phone))

def validate_roll_number(roll):
    """Ensure roll number is alphanumeric/dashes/slashes only and not empty."""
    if not roll:
        return False
    return bool(re.match(r'^[\w/-]+$', roll))

def validate_excel_headers(headers, required_headers):
    """Check if all required headers are present in the list."""
    headers_lower = [h.strip().lower() for h in headers]
    for req in required_headers:
        if req.strip().lower() not in headers_lower:
            return False, f"Missing required column: '{req}'"
    return True, None
