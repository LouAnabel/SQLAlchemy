from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


# Author Model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    # Relationship to link books to authors
    books = db.relationship("Book", backref="author", lazy=True)

    #customizes the string representation of the Author Instance
    def __repr__(self):
        return f"<Author {self.name} (ID: {self.id})>"

    # It allows you to override the string representation for an object
    def __str__(self):
        return f"Author: {self.name}, Born: {self.birth_date}, Died: {self.date_of_death}"


# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    # Foreign key linking the book to an author
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    # customizes the string representation of the Author Instance
    def __repr__(self):
        return f"<Book {self.title} (ID: {self.id})>"

    def __str__(self):
        return f"Book: {self.title}, ISBN: {self.isbn}, Published: {self.publication_year}"
