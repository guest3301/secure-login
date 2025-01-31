from datetime import datetime

ALLOWED_EXTENSIONS = {'xlsx'}

def validate_student_data(data):
    errors = []
    if not data.get('full_name'):
        errors.append("Full name is required")
    if not data.get('class_name'):
        errors.append("Class name is required")
    if not data.get('roll_no') or not data.get('roll_no').isdigit():
        errors.append("Roll no. must be a number")
    return errors

def format_date(date):
    if not date: return None
    return date.strptime('%Y-%m-%d')

def validate_date_string(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
