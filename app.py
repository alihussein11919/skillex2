import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from forms import RegistrationForm, LoginForm, TeacherRegistrationForm, MatchPreferencesForm, AdminLoginForm, LessonForm
from forms import GROUPED_SKILLS
from datetime import date
from functools import wraps
from flask_wtf.csrf import CSRFProtect
# ... your other imports ...

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some-static-key-for-dev'
csrf = CSRFProtect(app)
              # ← now CSRFProtect can use it

# now set up DB, Migrate, blueprints, etc.

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',       # XAMPP default user
    'password': '',       # XAMPP default empty password
    'database': 'skillex'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

# For production you'd load these from env-vars instead of hard-coding
ADMIN_CREDENTIALS = {
    "shahd24": "Shahd**6503",
    "malaky25":  "M@7@KY$25",
    "shams29": "Shams@222",
    "zeinaa27":  "zeIna2712",
    "haneen10": "H1012*03",
    "alii16":  "aLi*163*"
}

@app.route("/contact")
def contact():
    return render_template("contact.html")

# @app.route('/')
# def home():
#     return render_template('landing.html')
    
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route("/teacher_home")
def teacher_home():
    if "user_email" not in session:
        return redirect(url_for("login"))

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT username FROM users WHERE email = %s",
        (session["user_email"],)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("teacher_home.html",
        user_name = row['username']
    )






@app.route('/choice')
def choice():
    return render_template('choice.html')

from forms import RegistrationForm

@app.route("/learn", methods=["GET", "POST"])
def learn():
    form = RegistrationForm()
    if form.validate_on_submit():
        # 1) grab all the form fields
        fname         = form.first_name.data
        lname         = form.last_name.data
        username      = form.username.data
        email         = form.email.data
        pwd_hash      = generate_password_hash(form.password.data)
        country = form.country.data
        gender  = form.gender.data
        date_of_birth     = form.date_of_birth.data
        primary_skill = form.primary_skill.data
        skill_level   = form.skill_level.data

        conn   = get_db_connection()
        cursor = conn.cursor()
        try:

            # 2) insert into users

            cursor.execute(
                """
                INSERT INTO users
                 (first_name, last_name, username, email,
                 password_hash, role,
                 country, gender, date_of_birth)
                VALUES (%s,%s,%s,%s,
                        %s,%s,
                        %s,%s,%s)
                """,
                (fname, lname, username, email,
                pwd_hash, "student",
                country, gender, date_of_birth)
            )

            user_id = cursor.lastrowid

            # 3) now insert into students with your two new fields
            cursor.execute(
                """
                INSERT INTO students
                  (student_id, primary_skill, skill_level)
                VALUES (%s, %s, %s)
                """,
                (user_id, primary_skill, skill_level)
            )

            conn.commit()

            # 4) set up the session & redirect
            session["user_email"] = email
            session["user_name"]  = fname
            session["user_role"]  = "student"
            flash("Welcome aboard! Your account has been created.", "success")
            return redirect(url_for("student_home"))

        except Error as e:
            conn.rollback()
            app.logger.error("Registration failed: %s", e)
            flash("Oops, something went wrong. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    # either GET or validation errors
    return render_template("learn.html",
                           form=form,
                           grouped_skills=GROUPED_SKILLS)



@app.route("/teach", methods=["GET","POST"])
def teach():
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        # extract & hash
        fname, lname = form.first_name.data, form.last_name.data
        username     = form.username.data
        email        = form.email.data
        pwd_hash     = generate_password_hash(form.password.data)
        bio          = form.bio.data
        country = form.country.data
        gender = form.gender.data
        dob     = form.date_of_birth.data   # a datetime.date object
        
        from datetime import date 
        today = date.today()
        age = (
            today.year - dob.year
            - ((today.month, today.day) < (dob.month, dob.day))
            )

        conn   = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1) insert into users
            cursor.execute(
                """
                INSERT INTO users 
                (first_name, last_name, username, email, password_hash,
                country, gender, date_of_birth, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    fname,
                    lname,
                    username,
                    email,
                    pwd_hash,
                    country,        # new
                    gender,         # new
                    dob,            # new (a date object)
                    "teacher"
                )
            )
            user_id = cursor.lastrowid

            # 2) insert into teachers
            cursor.execute(
              """
              INSERT INTO teachers
                (teacher_id, bio)
              VALUES (%s, %s)
              """,
              (user_id, bio)
            )

            conn.commit()

            # set session & redirect
            session["user_email"] = email
            session["user_name"]  = fname
            session["user_role"]  = "teacher"
            flash("Teacher account created—welcome aboard!", "success")
            return redirect(url_for("teacher_dashboard"))

        except Error as e:
            conn.rollback()
            app.logger.error("Teacher registration failed: %s", e)
            flash("Sorry, we couldn't register you right now. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("teach.html", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # lookup user, check password, set session, flash, redirect…
        email    = form.email.data
        password = form.password.data

        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            session.permanent = form.remember.data

            session["user_email"] = user["email"]
            session["user_name"]  = user["first_name"]
            session["user_role"]  = user["role"]
            flash("Logged in successfully.", "success")

            # redirect based on role
            if user["role"] == "student":
                return redirect(url_for("student_home"))
            elif user["role"] == "teacher":
                return redirect(url_for("teacher_home"))

            # any other role—kick back to login
            flash("Unrecognized role, please contact support.", "danger")
            return redirect(url_for("login"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("landing"))


@app.route("/student_home")
def student_home():
    if "user_email" not in session:
        return redirect(url_for("login"))

    # Fetch the student's username from the database
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT username FROM users WHERE email = %s",
        (session["user_email"],)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    # Pass the username into your template exactly the same way
    return render_template(
        "student_home.html",
        user_name=row['username']
    )

@app.route("/student_dashboard")
def student_dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    # Fetch the student's data from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user information
    cursor.execute(
        """
        SELECT u.*, s.primary_skill, s.skill_level
        FROM users u
        JOIN students s ON u.user_id = s.student_id
        WHERE u.email = %s
        """,
        (session["user_email"],)
    )
    user_data = cursor.fetchone()
    
    if not user_data:
        cursor.close()
        conn.close()
        flash("User not found or not a student.", "danger")
        return redirect(url_for("login"))
    
    cursor.close()
    conn.close()

    return render_template(
        "student_dashboard.html",
        user=user_data,
        grouped_skills=GROUPED_SKILLS
    )

@app.route("/teacher_dashboard")
def teacher_dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    # Fetch the teacher's data from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user information
    cursor.execute(
        """
        SELECT u.*, t.bio
        FROM users u
        JOIN teachers t ON u.user_id = t.teacher_id
        WHERE u.email = %s
        """,
        (session["user_email"],)
    )
    user_data = cursor.fetchone()
    
    if not user_data:
        cursor.close()
        conn.close()
        flash("User not found or not a teacher.", "danger")
        return redirect(url_for("login"))
    
    # Get students with their skills (simplified for now, in a real app this would use a teacher-student relationship)
    cursor.execute(
        """
        SELECT u.username, s.primary_skill, s.skill_level 
        FROM users u
        JOIN students s ON u.user_id = s.student_id
        WHERE u.role = 'student'
        LIMIT 3
        """
    )
    students_data = cursor.fetchall()
    
    # Get teacher's lessons
    cursor.execute(
        """
        SELECT l.*,
               CASE WHEN l.student_id IS NOT NULL THEN 1 ELSE 0 END as student_count,
               COALESCE(sk.name, 'General Lesson') as skill_name
        FROM lessons l
        LEFT JOIN skills sk ON l.skill_id = sk.skill_id
        WHERE l.teacher_id = %s
        ORDER BY l.created_at DESC
        """,
        (user_data["user_id"],)
    )
    lessons_data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template(
        "teacher_dashboard.html",
        user=user_data,
        students=students_data,
        lessons=lessons_data,
        grouped_skills=GROUPED_SKILLS
    )

@app.route("/browse_matches", methods=["GET", "POST"])
def browse_matches():
    if "user_email" not in session:
        return redirect(url_for("login"))

    # load current user
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT user_id, username, date_of_birth "
        "FROM users WHERE email = %s",
        (session["user_email"],)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        flash("Account not found, please log in again.", "warning")
        return redirect(url_for("login"))

    form  = MatchPreferencesForm()
    match = None

    # prefill on GET
    if request.method == "GET" and user["date_of_birth"]:
        dob   = user["date_of_birth"]
        today = date.today()
        age   = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 26:
            form.preferred_age.data = "18-25"
        elif age < 36:
            form.preferred_age.data = "26-35"
        elif age < 46:
            form.preferred_age.data = "36-45"
        else:
            form.preferred_age.data = "46+"

    # on POST
    if form.validate_on_submit():
        low, high = map(int, form.preferred_age.data.split("-"))

        filters = [
            "u.role = 'student'",
            "u.user_id != %s",
            "s.primary_skill = %s",
            "s.skill_level = %s",
            "u.country = %s",
            "TIMESTAMPDIFF(YEAR, u.date_of_birth, CURDATE()) BETWEEN %s AND %s"
        ]
        params = [
            user["user_id"],
            form.skill_to_learn.data,
            form.preferred_skill_level.data,
            form.country.data,
            low, high
        ]

        if form.preferred_gender.data.lower() != "any":
            filters.insert(4, "u.gender = %s")
            params.insert(4, form.preferred_gender.data)

        where_clause = " AND ".join(filters)

        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        sql = f"""
            SELECT
              u.user_id,
              u.username,
              u.country,
              u.date_of_birth,
              s.primary_skill,
              s.skill_level
            FROM users u
            JOIN students s
              ON s.student_id = u.user_id
            WHERE {where_clause}
            LIMIT 1
        """
        cur.execute(sql, params)
        match = cur.fetchone()

        # **only** if no exact match, do the fallback
        if not match:
            cur.execute("""
                SELECT
                  u.user_id,
                  u.username,
                  u.country,
                  u.date_of_birth,
                  s.primary_skill,
                  s.skill_level
                FROM users u
                JOIN students s
                  ON s.student_id = u.user_id
                WHERE u.role = 'student'
                  AND u.user_id != %s
                ORDER BY RAND()
                LIMIT 1
            """, (user["user_id"],))
            match = cur.fetchone()

        cur.close()
        conn.close()

    return render_template(
        "browse_matches.html",
        user_name=user["username"],
        form=form,
        match=match,
        grouped_skills=GROUPED_SKILLS,
        date=date
    )


@app.route('/chat/<int:recipient_id>')
def chat(recipient_id):
    # look up the recipient's info if you like:
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id, username FROM users WHERE user_id = %s", (recipient_id,))
    recipient = cur.fetchone()
    cur.close()
    conn.close()

    # then render a chat template—pass along recipient
    return render_template('chatroom.html',
                           recipient=recipient)

    

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in as admin to view that page.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        uname = form.username.data
        pwd   = form.password.data

        if ADMIN_CREDENTIALS.get(uname) == pwd:
            # mark them as logged-in admin
            session["is_admin"]  = True
            session["admin_user"] = uname
            flash(f"Welcome, {uname}!", "success")

            # ← here's the magic line that sends them to the portal:
            return redirect(url_for("admin_portal"))
        else:
            flash("Invalid admin credentials.", "danger")

    return render_template("admin_login.html", form=form)

@app.route("/admin/logout")
@admin_required
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_user", None)
    flash("You've been logged out of the admin portal.", "info")
    return redirect(url_for("admin_login"))

@app.route("/browse_teachers")
def browse_teachers():
    return render_template("browse_teachers.html")

@app.route("/marketplace")
def marketplace():
    return render_template("marketplace.html")

@app.route("/update_skill", methods=["POST"])
def update_skill():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    # Get form data
    primary_skill = request.form.get("primary_skill")
    skill_level = request.form.get("skill_level")
    
    # Validate inputs
    if not primary_skill or not skill_level:
        flash("Please provide both skill and level", "danger")
        return redirect(url_for("student_dashboard"))
    
    # Update the database
    conn = get_db_connection()
    if not conn:
        flash("Database connection error. Please try again.", "danger")
        return redirect(url_for("student_dashboard"))
    
    # Use dictionary cursor consistently
    cursor = conn.cursor(dictionary=True)
    try:
        # Get user_id from session email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (session["user_email"],))
        result = cursor.fetchone()
        
        if not result:
            flash("User not found", "danger")
            return redirect(url_for("student_dashboard"))
        
        user_id = result["user_id"]
        
        # Update the student's skills
        cursor.execute(
            """
            UPDATE students 
            SET primary_skill = %s, skill_level = %s
            WHERE student_id = %s
            """,
            (primary_skill, skill_level, user_id)
        )
        
        conn.commit()
        flash("Your skill has been updated successfully!", "success")
    
    except Error as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
    
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for("student_dashboard"))

@app.route("/create_lesson", methods=["POST"])
def create_lesson():
    print("==================== CREATE LESSON ROUTE TRIGGERED ====================")
    if "user_email" not in session or session.get("user_role") != "teacher":
        print(f"User role check failed: email={session.get('user_email')}, role={session.get('user_role')}")
        flash("You must be logged in as a teacher to create lessons.", "danger")
        return redirect(url_for("login"))
    
    # Get form data
    skill_id = request.form.get("skill_id")
    scheduled_time = request.form.get("scheduled_time")
    duration = request.form.get("duration")
    price = request.form.get("price", "0.00")
    
    print(f"Form data: skill_id={skill_id}, scheduled_time={scheduled_time}, duration={duration}, price={price}")
    
    # Validate inputs
    if not scheduled_time or not duration:
        print("Form validation failed: missing required fields")
        flash("Please fill out all required fields", "danger")
        return redirect(url_for("teacher_dashboard"))
    
    try:
        duration = int(duration)
        if duration < 15 or duration > 180:
            print(f"Duration validation failed: {duration} not between 15-180")
            flash("Duration must be between 15 and 180 minutes", "danger")
            return redirect(url_for("teacher_dashboard"))
    except ValueError:
        print(f"Duration validation failed: {duration} is not a number")
        flash("Duration must be a number", "danger")
        return redirect(url_for("teacher_dashboard"))
    
    try:
        price = float(price)
        if price < 0:
            print(f"Price validation failed: {price} is negative")
            flash("Price cannot be negative", "danger")
            return redirect(url_for("teacher_dashboard"))
    except ValueError:
        print(f"Price validation failed: {price} is not a number")
        flash("Price must be a valid number", "danger")
        return redirect(url_for("teacher_dashboard"))
    
    # Get teacher ID
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        flash("Database connection error. Please try again.", "danger")
        return redirect(url_for("teacher_dashboard"))
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (session["user_email"],))
        result = cursor.fetchone()
        
        if not result:
            print(f"Teacher not found for email: {session['user_email']}")
            flash("Teacher not found", "danger")
            return redirect(url_for("teacher_dashboard"))
        
        teacher_id = result["user_id"]
        print(f"Found teacher_id: {teacher_id}")
        
        # Convert scheduled_time from HTML datetime-local format to MySQL datetime
        if scheduled_time:
            try:
                from datetime import datetime
                # HTML datetime-local format is: YYYY-MM-DDThh:mm
                scheduled_datetime = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
                print(f"Parsed scheduled time: {scheduled_datetime}")
            except ValueError as e:
                print(f"Error parsing scheduled time: {e}")
                flash("Invalid date format for scheduled time", "danger")
                return redirect(url_for("teacher_dashboard"))
        else:
            # Default to 24 hours from now
            from datetime import datetime, timedelta
            scheduled_datetime = datetime.now() + timedelta(days=1)
        
        # Insert the new lesson - matching existing database schema
        print("Attempting to insert lesson into database...")
        if skill_id and skill_id.strip():
            query = """
            INSERT INTO lessons 
            (teacher_id, student_id, skill_id, scheduled_time, duration_minutes, status, price)
            VALUES (%s, NULL, %s, %s, %s, 'scheduled', %s)
            """
            params = (teacher_id, skill_id, scheduled_datetime, duration, price)
        else:
            query = """
            INSERT INTO lessons 
            (teacher_id, student_id, skill_id, scheduled_time, duration_minutes, status, price)
            VALUES (%s, NULL, NULL, %s, %s, 'scheduled', %s)
            """
            params = (teacher_id, scheduled_datetime, duration, price)
        
        print(f"Query: {query}")
        print(f"Params: {params}")
        
        cursor.execute(query, params)
        
        # Get the ID of the newly inserted lesson
        lesson_id = cursor.lastrowid
        print(f"Inserted lesson with ID: {lesson_id}")
        
        conn.commit()
        print("Database commit successful")
        flash("Lesson created successfully!", "success")
    
    except Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        flash(f"An error occurred: {str(e)}", "danger")
    
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed")
    
    print("Redirecting to teacher_dashboard")
    return redirect(url_for("teacher_dashboard"))

# Database setup - create tables if they don't exist
def setup_database():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database during setup")
        return False
    
    cursor = conn.cursor()
    
    # Create lessons table if it doesn't exist
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            lesson_id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            duration INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(user_id)
        )
        """)
        
        # Create lesson_enrollments table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_enrollments (
            enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
            lesson_id INT NOT NULL,
            student_id INT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id),
            FOREIGN KEY (student_id) REFERENCES users(user_id),
            UNIQUE KEY unique_enrollment (lesson_id, student_id)
        )
        """)
        
        conn.commit()
        print("Database setup completed successfully")
    except Error as e:
        print(f"Error setting up database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return True

# Run setup on import
setup_database()

# Check and add created_at column if it doesn't exist
def add_created_at_column():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    try:
        # Check if column exists
        cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'skillex' 
        AND TABLE_NAME = 'lessons' 
        AND COLUMN_NAME = 'created_at'
        """)
        
        result = cursor.fetchone()
        if result[0] == 0:
            # Add the column if it doesn't exist
            print("Adding created_at column to lessons table")
            cursor.execute("""
            ALTER TABLE lessons 
            ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("Added created_at column successfully")
        else:
            print("created_at column already exists")
    except Error as e:
        print(f"Error checking or adding created_at column: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return True

# Run column check on import
add_created_at_column()

if __name__ == '__main__':
    app.run(debug=True, port=5001)

    


