from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    SelectField, DateField, TextAreaField, DecimalField, IntegerField
)
from wtforms.validators import (
    DataRequired, Length, Email, Regexp,
    EqualTo, NumberRange
)
import pycountry  # pip install pycountry for country list

COUNTRY_CHOICES = sorted(
    [(c.alpha_2, c.name) for c in pycountry.countries],
    key=lambda pair: pair[1]
)

GENDER_CHOICES = [
    ("male",   "Male"),
    ("female", "Female"),
    ("other",  "Other"),
]

# 1) define your groups once:
GROUPED_SKILLS = [
    ("Languages", [
        ("english","English"),("french","French"),("german","German"),
        ("spanish","Spanish"),("chinese","Chinese"),("italian","Italian"),
        ("arabic","Arabic"),("japanese","Japanese"),("korean","Korean"),
        ("russian","Russian")
    ]),
    ("Professional Skills", [
        ("python","Python"),("c","C"),("javascript","JavaScript"),
        ("css","CSS"),("html","HTML"),("java","Java"),("react","React"),
        ("graphic_design","Graphic Design"),("animation","Animation")
    ]),
    ("Crafts", [
        ("carpentry","Carpentry"),("knitting","Knitting"),
        ("pottery","Pottery"),("ceramics","Ceramics"),
        ("leatherwork","Leatherwork"),("woodcraft","Woodcraft"),
        ("weaving","Weaving"),("embroidery","Embroidery"),
        ("jewelry","Jewelry"),("crochet","Crochet")
    ]),
]

# 2) Flatten that into a simple list of (value,label) for WTForms validation:
FLAT_SKILLS = []
for grp, opts in GROUPED_SKILLS:
    FLAT_SKILLS.extend(opts)

class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(2,25)])
    last_name  = StringField("Last Name",  validators=[DataRequired(), Length(2,25)])
    username   = StringField("Username",   validators=[DataRequired(), Length(2,25)])
    email      = StringField("Email",      validators=[DataRequired(), Email(), Length(max=100)])
    password   = PasswordField("Password", validators=[
                    DataRequired(),
                    Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_]).{8,32}$",
                           message="…")
                  ])
    confirm_password = PasswordField("Confirm Password",
                        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])

    # your skill fields…
    primary_skill = SelectField("Primary Skill",
                                choices=FLAT_SKILLS,
                                validators=[DataRequired()],
                                coerce=str)
    skill_level   = SelectField("Skill Level",
                                choices=[("beginner","Beginner"),
                                         ("intermediate","Intermediate"),
                                         ("advanced","Advanced")],
                                validators=[DataRequired()],
                                coerce=str)

    # <— NEW! —>
    country       = SelectField(
        "Country",
        choices=COUNTRY_CHOICES,
        validators=[DataRequired()],
        coerce=str
    )
    gender        = SelectField(
        "Gender",
        choices=GENDER_CHOICES,
        validators=[DataRequired()],
        coerce=str
    )
    date_of_birth = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )
    submit        = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class TeacherRegistrationForm(FlaskForm):
    first_name = StringField(
        "First Name",
        validators=[DataRequired(), Length(min=2, max=25)]
    )
    last_name = StringField(
        "Last Name",
        validators=[DataRequired(), Length(min=2, max=25)]
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=2, max=25)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=100)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,32}$",
                message="Password must be 8–32 chars, include upper, lower, number & special."
            ),
        ],
    )
    confirm_pass = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )
    bio = TextAreaField(
        "Short Bio",
        validators=[DataRequired(), Length(max=500)]
    )
    # ─── NEW FIELDS ─────────────────────────────────────────────────────────
    country = SelectField(
        "Country",
        validators=[DataRequired()],
        choices=[(c.name, c.name) for c in pycountry.countries],
        validate_choice=True
    )

    gender = SelectField(
        "Gender",
        validators=[DataRequired()],
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        validate_choice=True
    )

    date_of_birth = DateField(
        "Date of Birth",
        format='%Y-%m-%d',
        validators=[DataRequired()],
        render_kw={"placeholder": "YYYY-MM-DD"}
    )
    # ──────────────────────────────────────────────────────────────────────

    submit = SubmitField("Create Account")


class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired()])
    password = PasswordField('Admin Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class MatchPreferencesForm(FlaskForm):
    skill_to_learn = SelectField(
        "Skill Looking to Learn",
        choices=FLAT_SKILLS,
        validators=[DataRequired()],
        coerce=str
    )
    preferred_skill_level = SelectField(
        "Preferred Skill Level",
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced")
        ],
        validators=[DataRequired()],
        coerce=str
    )
    country = SelectField(
        "Country",
        choices=COUNTRY_CHOICES,
        validators=[DataRequired()],
        coerce=str
    )
    preferred_gender = SelectField(
        "Preferred Gender",
        choices=[
            ("any", "Any"),
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other")
        ],
        validators=[DataRequired()],
        coerce=str
    )
    preferred_age = SelectField(
        "Preferred Age Group",
        choices=[
            ("18-25", "18-25"),
            ("26-35", "26-35"),
            ("36-45", "36-45"),
            ("46-99", "46+")
        ],
        validators=[DataRequired()],
        coerce=str
    )
    submit = SubmitField("Find Matches")

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=15, max=180)])
    submit = SubmitField('Create Lesson')


    