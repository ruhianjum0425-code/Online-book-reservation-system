import sqlite3

DB = "booknest.db"

subjects = [
    "Biology",
    "Geography",
    "Psychology",
    "Sociology",
    "Statistics",
    "Environmental Science",
    "Political Science",
    "Accounting",
    "Business Studies",
    "Programming",
    "Astronomy",
    "Philosophy"
]

books = [
    ("Biology Basics", "A. Sharma", "biology.jpg", "Biology fundamentals", "Biology"),
    ("World Geography", "R. Kumar", "geography.jpg", "Introduction to world geography", "Geography"),
    ("Introduction to Psychology", "S. Patel", "psychology.jpg", "Basic psychology concepts", "Psychology"),
    ("Modern Sociology", "M. Singh", "sociology.jpg", "Introduction to sociology", "Sociology"),
    ("Statistics Made Easy", "P. Rao", "statistics.jpg", "Basic statistics and data analysis", "Statistics"),
    ("Environmental Science", "K. Thomas", "environment.jpg", "Environment and sustainability", "Environmental Science"),
    ("Political Science Today", "N. Kumar", "political_science.jpg", "Fundamentals of political science", "Political Science"),
    ("Accounting Fundamentals", "J. Wilson", "accounting.jpg", "Basic accounting concepts", "Accounting"),
    ("Business Studies", "R. Mehta", "business.jpg", "Introduction to business studies", "Business Studies"),
    ("Python Programming", "A. Verma", "programming.jpg", "Learn programming with Python", "Programming"),
    ("Introduction to Astronomy", "D. Brown", "astronomy.jpg", "Stars, planets and the universe", "Astronomy"),
    ("Introduction to Philosophy", "S. Martin", "philosophy.jpg", "Basic philosophy concepts", "Philosophy")
]

conn = sqlite3.connect(DB)
cursor = conn.cursor()

# Add subjects
for subject in subjects:
    cursor.execute(
        "INSERT OR IGNORE INTO subjects (name, description) VALUES (?, ?)",
        (subject, f"Books related to {subject}")
    )

# Add books
for title, author, image, description, subject_name in books:

    cursor.execute(
        "SELECT id FROM subjects WHERE name = ?",
        (subject_name,)
    )

    subject_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO books
        (title, author, isbn, description, cover_url,total_copies, available_copies, subject_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        title,
        author,
        None,
        description,
        "/static/" + image,
        5,
        5,
        subject_id
    ))

conn.commit()
conn.close()

print("12 subjects and 12 books added successfully!")