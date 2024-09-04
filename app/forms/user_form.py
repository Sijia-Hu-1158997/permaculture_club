import re
from flask import session
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
from app.models.user import UserModel


class UpdateUserInfoForm(Form):
    username = StringField(
        "Username",
        validators=[Optional(), Length(min=1, max=255)],
    )
    password = PasswordField("Password", validators=[Optional(), Length(min=1)])
    role = SelectField(
        "Role",
        choices=[
            ("member", "member"),
            ("instructor", "instructor"),
            ("manager", "manager"),
        ],
        validators=[Optional()],
    )
    title = SelectField(
        "Title",
        choices=[("Mr", "Mr"), ("Ms", "Ms"), ("Mrs", "Mrs"), ("", "")],
        validators=[Optional()],
    )
    first_name = StringField("First Name", validators=[Optional(), Length(max=255)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=255)])
    position = StringField("Position", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional()])
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[Optional()]
    )
    profile_image = TextAreaField("Profile Image", validators=[Optional()])
    permaculture_experience = TextAreaField("Permaculture experience", validators=[Optional()])
    instructor_profile = TextAreaField("Instructor Profile", validators=[Optional()])
    is_deleted = BooleanField("Is Deleted", validators=[Optional()])
    subscription = SelectField(
        "Subscription",
        choices=[("Monthly", "Monthly"), ("Annually", "Annually"), ("", "")],
        validators=[Optional()],
    )
    started_at = DateField("Started At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    expired_at = DateField("Expired At", format="%Y-%m-%dT%H:%M", validators=[Optional()])

    onboarding = IntegerField("Onboarding", validators=[Optional()])

    # Check if the username already exists
    def validate_username(form, field):
        me = session.get("me") or {}
        userModel = UserModel()
        user = userModel.get_user_by_field(
            field_name="username", field_value=field.data
        )
        # For update only
        if user and user.get("id") != me.get('id'):
            raise ValidationError("Username already exists.")


class RegisterForm(Form):
    print("RegisterForm")
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

     # Check if the username already exists
    def validate_username(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="username", field_value=field.data):
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="email", field_value=field.data):
            raise ValidationError("Email already exists.")

    def validate_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")


class AdminRegisterForm(Form):
    print("RegisterForm")
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    role = SelectField("Role", choices=[("member", "Member"), ("instructor", "Instructor"), ("manager", "Manager")], validators=[DataRequired()])

    # Check if the username already exists
    def validate_username(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="username", field_value=field.data):
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="email", field_value=field.data):
            raise ValidationError("Email already exists.")

    def validate_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")


class UpdatePasswordForm(Form):
    password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password", validators=[DataRequired()]
    )

    def validate_new_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")


class SignInForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])