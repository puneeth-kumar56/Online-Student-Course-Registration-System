from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("courses.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create database tables
with get_db() as conn:

    conn.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            duration TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            email TEXT NOT NULL,
            course_id INTEGER,
            FOREIGN KEY(course_id) REFERENCES courses(id),
            UNIQUE(email, course_id)
        )
    """)

    # Insert sample courses
    count = conn.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    if count == 0:
        conn.executemany(
            "INSERT INTO courses (course_name, duration) VALUES (?, ?)",
            [
                ("Python Programming", "3 Months"),
                ("Web Development", "4 Months"),
                ("Java Programming", "3 Months"),
                ("Data Science", "5 Months")
            ]
        )

# Home page
@app.route('/')
def index():
    conn = get_db()
    courses = conn.execute(
        "SELECT * FROM courses"
    ).fetchall()
    conn.close()

    return render_template("index.html", courses=courses)

# Course registration
@app.route('/register/<int:course_id>', methods=['GET', 'POST'])
def register(course_id):

    conn = get_db()

    course = conn.execute(
        "SELECT * FROM courses WHERE id=?",
        (course_id,)
    ).fetchone()

    if course is None:
        conn.close()
        return "Course not found", 404

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        try:
            conn.execute(
                """INSERT INTO registrations
                (student_name, email, course_id)
                VALUES (?, ?, ?)""",
                (name, email, course_id)
            )

            conn.commit()
            conn.close()

            return redirect('/registrations')

        except sqlite3.IntegrityError:
            conn.close()
            return "You are already registered for this course!"

    conn.close()

    return render_template("register.html", course=course)

# Display registrations
@app.route('/registrations')
def registrations():

    conn = get_db()

    records = conn.execute("""
        SELECT registrations.id,
               student_name,
               email,
               course_name
        FROM registrations
        JOIN courses
        ON registrations.course_id = courses.id
    """).fetchall()

    conn.close()

    return render_template(
        "registrations.html",
        records=records
    )

if __name__ == '__main__':
    app.run(debug=True)