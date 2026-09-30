from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "booknest.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "booknest-development-secret-change-me")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE,
        description TEXT DEFAULT '',
        cover_url TEXT DEFAULT '',
        total_copies INTEGER NOT NULL DEFAULT 1,
        available_copies INTEGER NOT NULL DEFAULT 1,
        subject_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        reserved_at TEXT NOT NULL,
        pickup_deadline TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Reserved',
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    );
    """)

    subjects = [
        ("Computer Science", "Programming, software, AI, data structures and computing."),
        ("Mathematics", "Pure and applied mathematics."),
        ("Physics", "Classical, modern and engineering physics."),
        ("Chemistry", "Organic, inorganic and physical chemistry."),
        ("English", "Language, communication and literature."),
        ("Tamil", "தமிழ் மொழி, இலக்கியம் மற்றும் பண்பாடு."),
        ("History", "World, Indian and regional history."),
        ("Commerce", "Accounting, business and finance."),
        ("Economics", "Microeconomics, macroeconomics and development."),
        ("Electronics", "Digital systems, circuits and embedded systems.")
    ]
    for name, desc in subjects:
        conn.execute("INSERT OR IGNORE INTO subjects(name, description) VALUES (?, ?)", (name, desc))

    admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@booknest.com",)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users(name,email,password,role,created_at) VALUES(?,?,?,?,?)",
            ("BookNest Admin", "admin@booknest.com", generate_password_hash("admin123"), "admin",
             datetime.now().isoformat(timespec="seconds"))
        )

    sample_books = [
        ("Python Programming Mastery", "A. Sharma", "978100000001", "A practical introduction to Python programming.", "https://covers.openlibrary.org/b/isbn/978100000001-M.jpg", 5, "Computer Science"),
        ("Data Structures & Algorithms", "R. Kumar", "978100000002", "Core data structures and algorithmic problem solving.", "", 4, "Computer Science"),
        ("Engineering Mathematics", "S. Narayanan", "978100000003", "Essential mathematics for engineering students.", "", 6, "Mathematics"),
        ("Concepts of Modern Physics", "J. Mehta", "978100000004", "An accessible guide to modern physics concepts.", "", 3, "Physics"),
        ("Organic Chemistry Essentials", "P. Iyer", "978100000005", "Fundamentals of organic chemistry with examples.", "", 4, "Chemistry"),
        ("Technical English", "K. Priya", "978100000006", "Communication skills for academic and professional life.", "", 5, "English"),
        ("தமிழ் இலக்கிய வரலாறு", "மு. வரதராசன்", "978100000007", "தமிழ் இலக்கியத்தின் வளர்ச்சி மற்றும் வரலாறு.", "", 3, "Tamil"),
        ("Indian History: A Survey", "N. Rao", "978100000008", "A concise survey of Indian history.", "", 4, "History"),
        ("Principles of Accounting", "M. Joseph", "978100000009", "Fundamentals of financial accounting.", "", 5, "Commerce"),
        ("Microeconomics Made Simple", "D. Thomas", "978100000010", "Core microeconomic principles explained clearly.", "", 3, "Economics"),
        ("Digital Electronics", "V. Raj", "978100000011", "Logic gates, combinational and sequential circuits.", "", 4, "Electronics")
    ]
    for title, author, isbn, desc, cover, copies, subject in sample_books:
        sid = conn.execute("SELECT id FROM subjects WHERE name=?", (subject,)).fetchone()["id"]
        exists = conn.execute("SELECT id FROM books WHERE isbn=?", (isbn,)).fetchone()
        if not exists:
            conn.execute("""INSERT INTO books
                (title,author,isbn,description,cover_url,total_copies,available_copies,subject_id,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (title, author, isbn, desc, cover, copies, copies, sid, datetime.now().isoformat(timespec="seconds")))

    conn.commit()
    conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access required.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_globals():
    return {"year": datetime.now().year}

@app.route("/")
def index():
    conn = get_db()
    q = request.args.get("q", "").strip()
    subject_id = request.args.get("subject", "").strip()
    subjects = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    sql = """SELECT b.*, s.name AS subject_name FROM books b
             LEFT JOIN subjects s ON s.id=b.subject_id WHERE 1=1"""
    params = []
    if q:
        sql += " AND (b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?)"
        like = f"%{q}%"
        params += [like, like, like]
    if subject_id.isdigit():
        sql += " AND b.subject_id=?"
        params.append(int(subject_id))
    sql += " ORDER BY b.title"
    books = conn.execute(sql, params).fetchall()
    stats = {
        "books": conn.execute("SELECT COUNT(*) c FROM books").fetchone()["c"],
        "subjects": conn.execute("SELECT COUNT(*) c FROM subjects").fetchone()["c"],
        "available": conn.execute("SELECT COALESCE(SUM(available_copies),0) c FROM books").fetchone()["c"],
        "reservations": conn.execute("SELECT COUNT(*) c FROM reservations WHERE status='Reserved'").fetchone()["c"]
    }
    conn.close()
    return render_template("index.html", books=books, subjects=subjects, stats=stats, q=q, selected_subject=subject_id)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return redirect(url_for("register"))
        conn = get_db()
        try:
            conn.execute("INSERT INTO users(name,email,password,created_at) VALUES(?,?,?,?)",
                         (name,email,generate_password_hash(password),datetime.now().isoformat(timespec="seconds")))
            conn.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "danger")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/book/<int:book_id>")
def book_detail(book_id):
    conn = get_db()
    book = conn.execute("""SELECT b.*, s.name subject_name, s.description subject_description
                           FROM books b LEFT JOIN subjects s ON s.id=b.subject_id WHERE b.id=?""", (book_id,)).fetchone()
    conn.close()
    if not book:
        return "Book not found", 404
    return render_template("book_detail.html", book=book)

@app.route("/reserve/<int:book_id>", methods=["POST"])
@login_required
def reserve(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not book:
        conn.close(); flash("Book not found.", "danger"); return redirect(url_for("index"))
    existing = conn.execute("""SELECT id FROM reservations
                               WHERE user_id=? AND book_id=? AND status='Reserved'""",
                            (session["user_id"], book_id)).fetchone()
    if existing:
        conn.close(); flash("You already have an active reservation for this book.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))
    if book["available_copies"] < 1:
        conn.close(); flash("This book is currently unavailable.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))
    now = datetime.now()
    deadline = now + timedelta(days=3)
    conn.execute("""INSERT INTO reservations(user_id,book_id,reserved_at,pickup_deadline,status)
                    VALUES(?,?,?,?,?)""",
                 (session["user_id"], book_id, now.isoformat(timespec="seconds"),
                  deadline.isoformat(timespec="seconds"), "Reserved"))
    conn.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?", (book_id,))
    conn.commit(); conn.close()
    flash("Book reserved successfully. Pickup deadline is 3 days.", "success")
    return redirect(url_for("my_reservations"))

@app.route("/reservations")
@login_required
def my_reservations():
    conn = get_db()
    rows = conn.execute("""SELECT r.*, b.title, b.author, b.cover_url
                           FROM reservations r JOIN books b ON b.id=r.book_id
                           WHERE r.user_id=? ORDER BY r.reserved_at DESC""",
                        (session["user_id"],)).fetchall()
    conn.close()
    return render_template("reservations.html", reservations=rows)

@app.route("/cancel/<int:reservation_id>", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    conn = get_db()
    r = conn.execute("SELECT * FROM reservations WHERE id=? AND user_id=?", (reservation_id, session["user_id"])).fetchone()
    if r and r["status"] == "Reserved":
        conn.execute("UPDATE reservations SET status='Cancelled' WHERE id=?", (reservation_id,))
        conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?", (r["book_id"],))
        conn.commit()
        flash("Reservation cancelled and the copy was released.", "success")
    conn.close()
    return redirect(url_for("my_reservations"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    stats = {
        "books": conn.execute("SELECT COUNT(*) c FROM books").fetchone()["c"],
        "users": conn.execute("SELECT COUNT(*) c FROM users WHERE role='user'").fetchone()["c"],
        "reservations": conn.execute("SELECT COUNT(*) c FROM reservations").fetchone()["c"],
        "active": conn.execute("SELECT COUNT(*) c FROM reservations WHERE status='Reserved'").fetchone()["c"],
    }
    reservations = conn.execute("""SELECT r.*, u.name user_name, u.email, b.title
                                   FROM reservations r JOIN users u ON u.id=r.user_id
                                   JOIN books b ON b.id=r.book_id ORDER BY r.reserved_at DESC LIMIT 20""").fetchall()
    books = conn.execute("""SELECT b.*, s.name subject_name FROM books b
                            LEFT JOIN subjects s ON s.id=b.subject_id ORDER BY b.id DESC""").fetchall()
    subjects = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    conn.close()
    return render_template("admin.html", stats=stats, reservations=reservations, books=books, subjects=subjects)

@app.route("/admin/book/add", methods=["POST"])
@admin_required
def add_book():
    data = request.form
    conn = get_db()
    try:
        copies = max(1, int(data["copies"]))
        conn.execute("""INSERT INTO books(title,author,isbn,description,cover_url,total_copies,available_copies,subject_id,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                     (data["title"].strip(), data["author"].strip(), data.get("isbn","").strip() or None,
                      data.get("description","").strip(), data.get("cover_url","").strip(),
                      copies, copies, int(data["subject_id"]), datetime.now().isoformat(timespec="seconds")))
        conn.commit(); flash("Book added successfully.", "success")
    except (ValueError, sqlite3.IntegrityError):
        flash("Could not add book. Check the ISBN and form values.", "danger")
    finally: conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/book/delete/<int:book_id>", methods=["POST"])
@admin_required
def delete_book(book_id):
    conn = get_db()
    active = conn.execute("SELECT COUNT(*) c FROM reservations WHERE book_id=? AND status='Reserved'", (book_id,)).fetchone()["c"]
    if active:
        flash("Cannot delete a book with an active reservation.", "warning")
    else:
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit(); flash("Book deleted.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/subject/add", methods=["POST"])
@admin_required
def add_subject():
    name = request.form["name"].strip()
    desc = request.form.get("description","").strip()
    conn = get_db()
    try:
        conn.execute("INSERT INTO subjects(name,description) VALUES(?,?)", (name,desc))
        conn.commit(); flash("Subject added.", "success")
    except sqlite3.IntegrityError:
        flash("That subject already exists.", "warning")
    finally: conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reservation/<int:reservation_id>/complete", methods=["POST"])
@admin_required
def complete_reservation(reservation_id):
    conn = get_db()
    r = conn.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,)).fetchone()
    if r and r["status"] == "Reserved":
        conn.execute("UPDATE reservations SET status='Completed' WHERE id=?", (reservation_id,))
        conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?", (r["book_id"],))
        conn.commit(); flash("Reservation marked completed and copy returned to inventory.", "success")
    conn.close()
    return redirect
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
