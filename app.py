from flask import Flask, request, render_template, redirect, url_for, flash
from data_models import db, Author, Book  # Import models
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key

# Get absolute path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "data", "library.sqlite")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#connects the Flask app to the flask-sqlalchemy code
db.init_app(app)


@app.route("/", methods=["GET", "POST"])
def home():
    """handles the homepage with search and sort functionality"""
    search_query = request.args.get('search', '')  # Get search query from the form
    sort_by = request.args.get('sort_by', 'title')  # Default sort by title

    # Perform the search using SQLAlchemy with a LIKE query
    books_query = Book.query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort_by == 'title':
        books_query = books_query.order_by(Book.title)
    elif sort_by == 'author':
        books_query = books_query.join(Author).order_by(Author.name)

    # Fetch the books based on search and sorting criteria
    books = books_query.all()

    return render_template("home.html", books=books, search_query=search_query)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """handles author creation with form validation"""
    if request.method == "POST":
        name = request.form["name"].strip()

        # Convert birth_date and date_of_death
        birth_date_str = request.form["birth_date"]
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date() if birth_date_str else None

        date_of_death_str = request.form["date_of_death"]
        date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date() if date_of_death_str else None

        # Check if the author already exists
        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            flash("Author already exists!", "danger")
            return redirect(url_for("add_author"))

        # Add new author
        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        flash("Author added successfully!", "success")
        return redirect(url_for("add_author"))

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """handles book creation functionality"""
    authors = Author.query.all()

    if request.method == "POST":
        title = request.form["title"]
        isbn = request.form["isbn"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]

        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        flash("Book added successfully!", "success")
        return redirect(url_for("add_book"))

    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """deletes books by its IDs"""
    book_to_delete = Book.query.get_or_404(book_id)

    author = book_to_delete.author

    db.session.delete(book_to_delete)

    # Check if the author has any other books
    if not author.books:
        # If no books are left, delete the author as well
        db.session.delete(author)

    # Commit changes to the database
    db.session.commit()

    # Flash a success message
    flash(f"Successfully deleted '{book_to_delete.title}'", "success")

    # Redirect back to the homepage
    return redirect(url_for('home'))


def add_sample_data():
    # Add the sample data
    authors_and_books = [
        {
            "author": {
                "name": "J.K. Rowling",
                "birth_date": datetime.strptime("1965-07-31", "%Y-%m-%d").date(),
                "date_of_death": None
            },
            "books": [
                {"title": "Harry Potter and the Philosopher's Stone", "isbn": "9780747532743",
                 "publication_year": "1997"}
            ]
        },
        {
            "author": {
                "name": "George Orwell",
                "birth_date": datetime.strptime("1903-06-25", "%Y-%m-%d").date(),
                "date_of_death": datetime.strptime("1950-01-21", "%Y-%m-%d").date()
            },
            "books": [
                {"title": "1984", "isbn": "9780451524935", "publication_year": "1949"}
            ]
        },
        {
            "author": {
                "name": "Jane Austen",
                "birth_date": datetime.strptime("1775-12-16", "%Y-%m-%d").date(),
                "date_of_death": datetime.strptime("1817-07-18", "%Y-%m-%d").date()
            },
            "books": [
                {"title": "Pride and Prejudice", "isbn": "9780141439518", "publication_year": "1813"}
            ]
        },
        {
            "author": {
                "name": "Gabriel García Márquez",
                "birth_date": datetime.strptime("1927-03-06", "%Y-%m-%d").date(),
                "date_of_death": datetime.strptime("2014-04-17", "%Y-%m-%d").date()
            },
            "books": [
                {"title": "One Hundred Years of Solitude", "isbn": "9780060883287", "publication_year": "1967"}
            ]
        },
        {
            "author": {
                "name": "Agatha Christie",
                "birth_date": datetime.strptime("1890-09-15", "%Y-%m-%d").date(),
                "date_of_death": datetime.strptime("1976-01-12", "%Y-%m-%d").date()
            },
            "books": [
                {"title": "Murder on the Orient Express", "isbn": "9780062693662", "publication_year": "1934"}
            ]
        }
    ]

    for entry in authors_and_books:
        # Check if author already exists
        existing_author = Author.query.filter_by(name=entry["author"]["name"]).first()

        if not existing_author:
            # Create new author
            author = Author(
                name=entry["author"]["name"],
                birth_date=entry["author"]["birth_date"],
                date_of_death=entry["author"]["date_of_death"]
            )
            db.session.add(author)
            db.session.flush()  # Flush to get the author ID
        else:
            author = existing_author

        # Add books for this author
        for book_data in entry["books"]:
            # Check if book already exists
            existing_book = Book.query.filter_by(
                title=book_data["title"],
                author_id=author.id
            ).first()

            if not existing_book:
                book = Book(
                    title=book_data["title"],
                    isbn=book_data["isbn"],
                    publication_year=book_data["publication_year"],
                    author_id=author.id
                )
                db.session.add(book)

        # Commit all changes
    db.session.commit()
    print("Added 5 authors and their books successfully!")


if __name__ == "__main__":
    with app.app_context():
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Database tables: {tables}")

        if 'author' not in tables or 'book' not in tables:
            print("Creating tables...")
            db.create_all()
            print("Tables created!")

        # Now add sample data
        add_sample_data()

    app.run(debug=True, port=5000)
