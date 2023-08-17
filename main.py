from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
import os

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
Bootstrap(app)
db = SQLAlchemy(app)


class BookForm(FlaskForm):
    book_name = StringField('Book Name', validators=[InputRequired()])
    book_author = StringField('Book Author', validators=[InputRequired()])
    rating = FloatField('Rating', validators=[InputRequired()])
    submit = SubmitField('Add Book')


class EditForm(FlaskForm):
    new_rating = FloatField('', validators=[InputRequired()])
    submit = SubmitField('Change Rating')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'


with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def home():
    id = request.args.get('id')
    print(f"id is {id}")
    if id is not None:
        book_to_delete = db.session.get(Book, id)
        db.session.delete(book_to_delete)
        db.session.commit()
    all_books = []
    all_books = db.session.query(Book).all()
    return render_template('index.html', booklist = all_books)


@app.route('/add', methods=['POST', 'GET'])
def add():
    my_book_form = BookForm()
    if my_book_form.validate_on_submit():
        print(True)
        new_book = Book(title=my_book_form.book_name.data, author=my_book_form.book_author.data,
                        rating=my_book_form.rating.data)
        db.session.add(new_book)
        db.session.commit()

        my_book_form = BookForm(formdata=None)
    return render_template('add.html', form=my_book_form)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    edit_form = EditForm()
    id = request.args.get('id')
    book_to_update = db.session.get(Book, id)

    if edit_form.validate_on_submit():
        book_to_update.rating = edit_form.new_rating.data
        db.session.commit()
        all_books = []
        all_books = db.session.query(Book).all()
        return render_template('index.html', booklist=all_books)
    return render_template('edit.html', form=edit_form, book_to_update=book_to_update)


if __name__ == "__main__":
    app.run(debug=True)
