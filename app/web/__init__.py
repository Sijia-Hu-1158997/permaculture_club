from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter

web = Blueprint("web", __name__, template_folder="templates")


from app.web import auth,frontend,backend,frontend_profile,backend_workshop,backend_lesson,backend_instructor,backend_generic, frontend_membership, frontend_instructor_freetime,instructor_course, backend_subscriptions,backend_payments,backend_bookings,backend_news
