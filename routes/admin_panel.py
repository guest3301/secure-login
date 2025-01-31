from flask import render_template, request, Blueprint, abort, send_file
from flask_login import login_required, current_user
from models import Teacher, Class, db
from helpers.response import handle_error, make_response
from db_bak import restore_backup, db_path

admin = Blueprint('admin', __name__)

@admin.route("/admin-panel")
@login_required
def admin_panel():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    return render_template("admin_panel.html")

@admin.route('/create_class', methods=['POST'])
@login_required
def create_class():
    if current_user.id != 1:
        handle_error("You are not authorized to access this.", 403)
    data = request.json
    class_name = data.get('class_name')
    if not class_name:
        return handle_error("Class name is required", 400)
    existing_class = Class.query.filter_by(name=class_name).first()
    if existing_class:
        return handle_error("Class already exists", 400)
    new_class = Class(name=class_name, teacher_id=current_user.id)
    db.session.add(new_class)
    db.session.commit()
    return make_response(True, f"Class {class_name} created successfully", status_code=201)

@admin.route('/assign_class_to_teacher', methods=['POST'])
@login_required
def assign_class_to_teacher():
    if current_user.id != 1:
        handle_error("You are not authorized to access this.", 403)
    data = request.json
    teacher_name = data.get('teacher_name')
    class_names = data.get('class_names')
    if not teacher_name or not class_names:
        return handle_error("Teacher name and class names are required", 400)
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return handle_error("Teacher not found", 404)
    for class_name in class_names:
        class_instance = Class.query.get(class_name)
        if class_instance:
            class_instance.teacher_id = teacher.id
    db.session.commit()
    return make_response(True, f"Classes assigned to {teacher_name} successfully", status_code=200)

@admin.route('/add_subjects', methods=['POST'])
@login_required
def add_subjects():
    if current_user.id != 1:
        handle_error("You are not authorized to access this.", 403)
    data = request.json
    teacher_name = data.get('teacher_name')
    subjects = data.get('subjects')
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if teacher:
        teacher.subjects = subjects
        db.session.commit()
        return make_response(True, f"Subjects added to {teacher_name} successfully", status_code=200)
    return handle_error("Teacher not found", 404)

@admin.route('/create_teacher', methods=['POST'])
@login_required
def create_teacher():
    if current_user.id != 1:
        handle_error("You are not authorized to access this.", 403)
    data = request.json
    username = data.get('username')
    password = data.get('password') 
    if username is None or password is None:
        handle_error("Username and password are required", 400)
    existing_user = Teacher.query.filter_by(name=username).first()
    if existing_user is None:
        new_user = Teacher(name=username, password=password, subjects=[])
        db.session.add(new_user)
        db.session.commit()
        return make_response(True, f"Teacher {username} created successfully", status_code=201)
    else:
        return handle_error("Teacher already exists", 400)
    
@admin.route('/db', methods=['GET'])
@login_required
def db():
    if current_user.id != 1:
        return handle_error("You are not authorized to access this.", 403)
    q = request.args.get('q')
    if not q:
        return handle_error("Query parameter is required", 400)
    if q == "download":
        return send_file(db_path(), as_attachment=True)
    if q == "restore":
        date_str = request.args.get('date')
        if not date_str:
            return handle_error("Date parameter is required. Date format: YYYY-MM-DD", 400)
        result = restore_backup(date_str)
        if "Error" in result:
            return handle_error(result, 404)
        return make_response(result, 200)