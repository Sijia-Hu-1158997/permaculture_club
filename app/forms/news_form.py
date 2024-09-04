import re
from flask import session, g

from wtforms import (
    Form,
    IntegerField,
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    TextAreaField,
    DateField,
)
from wtforms.validators import (
    Length,
    Optional,
    DataRequired,
    EqualTo,
    ValidationError,
)
from app.models.news import NewsModel


class AddNewsForm(Form):
    title = StringField(
        "title", validators=[DataRequired(), Length(min=2, max=50)]
    )
    status = SelectField("Type", choices=[
        ("draft", "draft"),
        ("published", "published"),
        ],
        validators=[Optional()],
    )
    content = TextAreaField("content", validators=[DataRequired()])


