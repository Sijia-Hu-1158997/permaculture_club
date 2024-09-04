from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.user import UserModel
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from app.models.workshop import WorkshopModel
from app.models.lesson import LessonModel
from . import web


# Write your CMS routes here
@web.route("/admin/home", methods=["GET", "POST"])
@auth_required(roles=['instructor', 'manager'])
def admin_home():
    me = session.get("me") or {}
    if not me:
        return redirect(url_for("web.login"))
    return render_template("dashboard.html", me=me)


@web.route("/admin/profile", methods=["GET", "POST"])
@auth_required(roles=['instructor', 'manager'])
def admin_profile():
    me = session.get("me") or {}
    if request.method == "POST":
        form = UpdateUserInfoForm(request.form)
        if form.validate():
            user_model = UserModel()
            user_model.update_user_info(me.get('id'), form.data)
            me = user_model.get_user_by_field(field_name="id", field_value=me.get('id'))
            session["me"] = me
            flash("Updated successfully", "success")
        else:
            flash(form.errors, "danger")
    return render_template("admin_profile.html", me=me)


@web.route("/admin/<user_id>/user", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def update_user(user_id):
    isEditProfile = request.args.get('profile')
    me = session.get("me") or {}
    user_model = UserModel()
    target = user_model.get_user_by_field('id', user_id)
    if request.method == "POST":
        form = UpdateUserInfoForm(request.form)
        user_model = UserModel()
        if form.validate() and isEditProfile == 'true':
            user_model.update_user_info(user_id, form.data)
            flash("Updated successfully", "success")
            return redirect(url_for('web.admin_users')) 
        elif form.data['password'] and isEditProfile == 'false':
            user_model.update_password(user_id, form.data['password'])
            flash("Password updated successfully", "success")
            return redirect(url_for('web.admin_users')) 
        else:
            flash(form.errors, "danger")
    return render_template("admin_user_profile.html", me=me, user_id=user_id, target=target)


@web.route("/admin/users", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def admin_users():
    me = session.get("me") or {}
    user_model = UserModel()
    if request.method == "POST":
        query = request.form.get("query")
    else:
        query = request.args.get("query")
        search = False
        if query:
            search = True
        page = request.args.get('page', type=int, default=1)
        per_page = 10
        offset = (page - 1) * per_page
        users = user_model.get_users(query=query)
        users_for_render = users[offset:offset + per_page]
        pagination = Pagination(page=page, total=len(users), per_page=per_page, search=search, record_name='users')
        return render_template("admin_users.html", me=me, users=users_for_render, pagination=pagination)

    users = user_model.get_users(query=query)
    
    return render_template("admin_users.html", me=me, users=users)


@web.route("/admin/users/adduser", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def add_user():
    me = session.get("me") or {}
    user_model = UserModel()
    if request.method == "POST":
        form = AdminRegisterForm(request.form)
        if form.validate():
            user_model = UserModel()
            data = {
                "username": form.username.data,
                "email": form.email.data,
                "password": form.password.data,
                "role": form.role.data
            }
            user_model.admin_register_user(data) 
            role = data.get("role")
            if role == "instructor":
                flash("Add a new instructor successful! Please go to the left side 'Instructor' to add more details.", "success")
            else:
                flash("Add a new user successfully", "success")
            return render_template("admin_user_adduser.html", me=me)
        else:
            flash(form.errors, "danger")
    return render_template("admin_user_adduser.html", me=me)


@web.route("/admin/<user_id>/deleteuser", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def delete_user(user_id):
    me = session.get("me") or {}
    user_model = UserModel()
    delete_users = user_model.delete_user(user_id)
    if request.method == "GET":
        query = request.args.get("query")
        search = False
        if query:
            search = True
        page = request.args.get('page', type=int, default=1)
        per_page = 10
        offset = (page - 1) * per_page
        users = user_model.get_users(query=query)
        users_for_render = users[offset:offset + per_page]
        pagination = Pagination(page=page, total=len(users), per_page=per_page, search=search, record_name='users')
    return render_template("admin_users.html", me=me, delete_users=delete_users, users=users_for_render, pagination=pagination)


@web.route("/member_feedback", methods=["GET", "POST"])
@auth_required(roles=['member'])
def add_feedback():
    me = session.get("me") or {}
    user_model = UserModel()
    user_id = me.get("id")
    if request.method == "POST":
        data = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "feedback_user_id": user_id
        }
        user_model.add_feedback(data) 
        flash("Thank you. Your feedback has been sent successfully!", "success")
    return render_template("member_feedback.html", me=me)

@web.route("/admin_feedback", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def admin_feedback():
    # TO DO: fix the bug for pagination "found 0 feedback, displaying 1 - 0"
    me = session.get("me") or {}
    user_model = UserModel()
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    feedbacks = user_model.get_feedback(query=query)
    feedbacks_for_render = feedbacks[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(feedbacks), per_page=per_page, search=search, record_name='feedback')
    return render_template("admin_feedback.html", me=me, feedbacks=feedbacks_for_render, pagination=pagination)

@web.route("/admin/attendance", methods=["GET", "POST"])
@auth_required(roles=["manager", "instructor"])
def admin_attendance():
    me = session.get("me") or {}
    
    workshop_model = WorkshopModel()
    workshop_courses = workshop_model.get_workshops()

    lesson_model = LessonModel()
    lesson_courses = lesson_model.get_lessons()
    return render_template("admin_attendance.html", me=me,workshop_courses=workshop_courses,lesson_courses=lesson_courses)
    
