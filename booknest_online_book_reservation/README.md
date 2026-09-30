# BookNest — Online Book Reservation System
**Author:P.RuhiAnjum**
A complete, GitHub-ready online library/book reservation system built with **Python Flask + SQLite + Bootstrap-style custom CSS**.

## Features

- User registration and secure password hashing
- User/admin authentication
- Book catalogue with title, author, ISBN and description
- **Subjects** for books (Computer Science, Mathematics, Physics, Chemistry, English, Tamil, History, Commerce, Economics, Electronics)
- Search by title, author or ISBN
- Filter by subject
- Book availability tracking
- Online reservation with a 3-day pickup deadline
- Reservation history
- Reservation cancellation
- Admin dashboard
- Admin book and subject management
- Admin reservation completion
- Responsive design
- Sample data automatically loaded on first run
- GitHub-ready structure

## Project structure

```text
booknest_online_book_reservation/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── book_detail.html
│   ├── reservations.html
│   └── admin.html
└── static/
    └── css/
        └── style.css
```

`booknest.db` is generated automatically when the application starts.

## Requirements

- Python 3.10+
- pip

## Run on Windows

```powershell
cd booknest_online_book_reservation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

## Run on macOS/Linux

```bash
cd booknest_online_book_reservation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

## Demo admin login

- Email: `admin@booknest.com`
- Password: `admin123`

Change the admin password before deploying publicly.

## GitHub

```bash
git init
git add .
git commit -m "Initial BookNest project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/booknest-online-book-reservation.git
git push -u origin main
```

## Database design

### users
Stores users and roles.

### subjects
Stores book subjects/categories.

### books
Stores book information and inventory counts.

### reservations
Connects users to books and stores reservation status/deadline.

## Unique project idea

BookNest treats reservation as a short **pickup window** rather than a simple "borrow" action. When a user reserves a book, one available copy is held for 3 days. Admins can complete the reservation and return the copy to inventory. This makes the system suitable for college libraries where students reserve books online and collect them physically.

## Future enhancements

- Email/SMS reservation reminders
- QR code pickup
- Fine calculation
- Librarian role
- Book ratings/reviews
- Recommendation engine
- PDF/ebook links
- REST API
- MySQL/PostgreSQL production database
- Deployment with Gunicorn
