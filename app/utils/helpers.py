"""Helper functions for templates and controllers."""

import random
from datetime import datetime

def format_date(date_val, fmt='%d %b %Y'):
    """Format Date or DateTime object to string."""
    if not date_val:
        return ''
    return date_val.strftime(fmt)

def format_datetime(dt_val, fmt='%d %b %Y %H:%M'):
    """Format DateTime object to string."""
    if not dt_val:
        return ''
    return dt_val.strftime(fmt)

def get_academic_year():
    """Get current academic year string, e.g., '2026-27'."""
    now = datetime.now()
    year = now.year
    if now.month >= 6: # Academic session starts in June
        return f"{year}-{str(year+1)[2:]}"
    else:
        return f"{year-1}-{str(year)[2:]}"

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = {'xlsx', 'xls'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_random_color():
    """Generate random hex color for chart display."""
    r = lambda: random.randint(50, 200) # Keep them reasonably visible
    return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

def get_greeting():
    """Return appropriate greeting based on time of day."""
    hour = datetime.now().hour
    if hour < 12:
        return 'Good Morning'
    elif hour < 17:
        return 'Good Afternoon'
    else:
        return 'Good Evening'
