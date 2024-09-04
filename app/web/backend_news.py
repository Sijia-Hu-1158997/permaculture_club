from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.news import NewsModel
from app.forms.news_form import AddNewsForm
import datetime
from . import web


@web.route("/admin/news/add", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def add_news():
    me = session.get("me") or {}
    news_model = NewsModel()
    user_id = me.get("id")
    if request.method == "POST":
        data = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "author_id": user_id
        }   
        news_model.add_news(data) 
        flash("News add successfully!", "success")
    return render_template("admin_news_add.html", me=me)


@web.route("/admin/news", methods=["GET", "POST"])
@auth_required(roles=['manager', 'instructor'])
def admin_news():
    me = session.get("me") or {}
    news_model = NewsModel()
    query = request.args.get("query")
    news = news_model.get_news(query=query)

    search = False
    if query:
        search = True

    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    news = news_model.get_news(query=query)
    news_for_render = news[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(news), per_page=per_page, search=search, record_name='news')
    return render_template("admin_news.html", me=me, news=news_for_render, pagination=pagination)

@web.route("/admin/news/<id>", methods=["GET", "POST"])
@auth_required(roles=['manager'])
def update_news(id):
    me = session.get("me") or {}
    news_model = NewsModel()
    news = news_model.get_news_by_id(id)
    if request.method == "POST":
        form = AddNewsForm(request.form)
        if form.validate():
            news_model.update_news(id, form.data)
            flash("Updated successfully", "success")
        else:
            flash(form.errors, "danger")
    return render_template("admin_news_update.html", me=me, id=id, news=news)

@web.route("/admin/news/delete/<id>", methods=["GET", "POST"])
@auth_required(roles=["manager"])
def delete_news(id):
    me = session.get("me") or {}
    news_model = NewsModel()
    target = news_model.get_news_by_id(id)

    if target:
        news_model.delete_news(id)
        flash("Dlete successfully", "success")

    return redirect(url_for('web.admin_news')) 


@web.route("/view/news", methods=["GET", "POST"])
@auth_required(roles=['member', 'manager', 'instructor'])
def view_news():
    me = session.get("me") or {}
    news_model = NewsModel()
    query = request.args.get("query")
    news = news_model.view_news(query=query)

    search = False
    if query:
        search = True

    page = request.args.get('page', type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page
    news = news_model.view_news(query=query)
    news_for_render = news[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(news), per_page=per_page, search=search, record_name='news')
    return render_template("member_news.html", me=me, news=news_for_render, pagination=pagination)

@web.route("/view/<id>/news", methods=["GET"])
@auth_required(roles=['member', 'manager', 'instructor'])
def view_news_details(id):
    me = session.get("me") or {}
    news_model = NewsModel()
    news_info = news_model.get_news_by_id(id)
    return render_template("member_news_details.html", me=me, news_info=news_info, id=id)
