from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.user import UserModel
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from . import web
import os


@web.route("/admin/instructor", methods=["GET", "POST"])
@auth_required(roles=["manager", "instructor"])
def admin_instructor():
    me = session.get("me") or {}
    user_model = UserModel()
    if request.method == "POST":
        query = request.form.get("query")
        users = user_model.get_instructors()
    else:
        query = request.args.get("query")
        search = False
        if query:
            search = True
        page = request.args.get('page', type=int, default=1)
        per_page = 10
        offset = (page - 1) * per_page
        instructors = user_model.get_instructors()
        instructors_for_render = instructors[offset:offset + per_page]
        pagination = Pagination(page=page, total=len(instructors), per_page=per_page, search=search, record_name='users')
        return render_template("admin_instructor.html", me=me, instructors=instructors_for_render, pagination=pagination)
    return render_template("admin_instructor.html", me=me, instructors=instructors)




@web.route("/admin/<user_id>/instructor", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def update_instructor(user_id):
    me = session.get("me") or {}
    user_model = UserModel()
    target = user_model.get_user_by_field('id', user_id)
    if request.method == "POST":
        form = UpdateUserInfoForm(request.form)
        user_model = UserModel()
        if form.validate():
            user_model.update_user_info(user_id, form.data)
            flash("Updated successfully", "success")
            return render_template("admin_instructor_update.html", me=me, user_id=user_id, target=target)
        else:
            flash(form.errors, "danger")
    return render_template("admin_instructor_update.html", me=me, user_id=user_id, target=target)



@web.route("/admin/<user_id>/delete_instructor", methods=["GET"])
@auth_required(roles=['manager'])
def delete_instructor(user_id):
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
    flash("Delete the instructor successfully!", "success")
    return render_template("admin_instructor.html", me=me, delete_users=delete_users, users=users_for_render, pagination=pagination)



@web.route("/admin/<user_id>/instructors", methods=["GET", "POST"])
@auth_required(roles=['manager', 'instructor'])
def update_instructor_pic(user_id):
    me = session.get("me") or {}
    user_model = UserModel()
    if request.method == "POST":
        target = user_model.get_user_by_field('id', user_id)
        user_id = target.get("id")
        file_info = request.files['profile_image']
        # for local computer:
        # folder_path = os.path.join(os.getcwd(),'app/static/data/user_profile',str(user_id))

        # for PythonAnywhere:/home/HexaDec/COMP639S1_Group_I/app/static
        folder_path = os.path.join(os.getcwd(),'app/static/data/user_profile',str(user_id))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_type = file_info.content_type
        file_name = file_info.filename

        if file_name:
            file_full_path = os.path.join(folder_path,file_name)
            print("file_full_path:",file_full_path)
            file_info.save(file_full_path)
        # file_path = os.path.join('static/data/user_profile',str(user_id),file_name)
        file_path = os.path.join('static/data/user_profile',str(user_id),file_name)

        user_model = UserModel()
        user_model.update_profile_img(target.get("id"), file_path)

        user = user_model.get_user_by_field(field_name="id", field_value=target.get("id"))
        flash("Updated successfully", "success")
        return redirect(url_for("web.admin_instructor"))
    else:
        return redirect(url_for("web.admin_instructor"))
    
