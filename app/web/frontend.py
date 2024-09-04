from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.booking import BookingModel
from app.models.user import UserModel
from app.models.categories import CategoryModel
from app.models.workshop import WorkshopModel
from app.models.lesson import LessonModel
from app.models.instructor import InstructorModel
from . import web


# Write your frontend website routes here
# Example - Home route
@web.route("/")
def home():
    me = session.get("me") or {}
    category_model = CategoryModel()
    search = False
    page = request.args.get("page", type=int, default=1)
    per_page = 4
    offset = (page - 1) * per_page
    categories = category_model.get_categories()
    categories_for_render = categories[offset : offset + per_page]
    pagination = Pagination(
        page=page,
        total=len(categories),
        per_page=per_page,
        search=search,
        record_name="categories",
    )
    return render_template(
        "home.html", me=me, categories=categories_for_render, pagination=pagination
    )


@web.route("/workshop", methods=["GET", "POST"])
def workshop():
    me = session.get("me") or {}
    workshop_model = WorkshopModel()
    query = ""
    search = False
    if query:
        search = True
    page = request.args.get("page", type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page
    courses = workshop_model.get_workshops(query=query)
    courses_for_render = courses[offset : offset + per_page]
    pagination = Pagination(
        page=page,
        total=len(courses),
        per_page=per_page,
        search=search,
        record_name="courses",
    )
    return render_template(
        "workshop.html", me=me, courses=courses_for_render, pagination=pagination
    )


@web.route("/workshop_detail/<workshop_id>/")
@auth_required(roles=["member", "instructor", "manager"])
def workshop_detail(workshop_id):
    me = session.get("me") or {}
    workshop_model = WorkshopModel()
    target = workshop_model.get_workshops_by_field("id", workshop_id)
    instructors = InstructorModel().get_all_Instructors()
    instructor_dict = {}
    for item in instructors:
        item_id = item['id']
        instructor_dict[item_id] = {
            'last_name':item['last_name'],
            'first_name':item['first_name'],
            'instructor_profile':item['instructor_profile'],
            'permaculture_experience':item['permaculture_experience']       
        }
        
  
    # check if the user has already booked this course
    booking_model = BookingModel()
    booked_courses = booking_model.get_bookings_by_user_id(me["id"])
    booked_courses_ids = [
        booked_courses["course_id"] for booked_courses in booked_courses
    ]
    return render_template(
        "workshop_details.html",
        me=me,
        target=target,
        booked_courses_ids=booked_courses_ids,
        instructor_dict=instructor_dict
    )





@web.route("/lesson", methods=["GET", "POST"])
@auth_required(roles=["member", "instructor", "manager"])
def lesson():
    me = session.get("me") or {}
    lesson_model = LessonModel()
    query = ""
    search = False
    if query:
        search = True
    page = request.args.get("page", type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page
    courses = lesson_model.get_lessons(query=query)
    courses_for_render = courses[offset : offset + per_page]
    pagination = Pagination(
        page=page,
        total=len(courses),
        per_page=per_page,
        search=search,
        record_name="courses",
    )
    return render_template(
        "lesson.html", me=me, courses=courses_for_render, pagination=pagination
    )


@web.route("/lesson_detail/<lesson_id>/")
@auth_required(roles=["member", "instructor", "manager"])
def lesson_detail(lesson_id):
    me = session.get("me") or {}
    lesson_model = LessonModel()
    target = lesson_model.get_lessons_by_field("id", lesson_id)
    # check if the user has already booked this course
    booking_model = BookingModel()
    booked_courses = booking_model.get_bookings_by_user_id(me["id"])
    booked_courses_ids = [
        booked_courses["course_id"] for booked_courses in booked_courses
    ]
    instructors = InstructorModel().get_all_Instructors()
    instructor_dict = {}
    for item in instructors:
        item_id = item['id']
        instructor_dict[item_id] = {
            'last_name':item['last_name'],
            'first_name':item['first_name'],
            'instructor_profile':item['instructor_profile'],
            'permaculture_experience':item['permaculture_experience']       
        }
    return render_template(
        "lesson_details.html",
        me=me,
        target=target,
        booked_courses_ids=booked_courses_ids,
        instructor_dict=instructor_dict
    )
