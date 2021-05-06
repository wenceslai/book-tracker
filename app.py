from flask import Flask, render_template, has_request_context, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'

db = SQLAlchemy(app)

class Books(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(40), nullable=False)
    author = db.Column(db.String(40), nullable=False)

    added_date = db.Column(db.DateTime, default=datetime.utcnow)

    start_date = db.Column(db.DateTime)
    finish_date = db.Column(db.DateTime)

    pages = db.Column(db.Integer)

    notes = db.Column(db.String(400))

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))

class Categories(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Languages(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2), nullable=False)

"""
db.session.add(Categories(name='unspecified'))
db.session.add(Categories(name='physics'))
db.session.add(Categories(name='psychology'))
db.session.add(Categories(name='philosophy'))
db.session.add(Categories(name='politics'))
db.session.add(Categories(name='poetry'))
db.session.add(Categories(name='drama'))
db.session.add(Categories(name='computer science'))
db.session.add(Categories(name='history'))
db.session.add(Categories(name='autobiography'))
db.session.add(Categories(name='engineering'))
db.session.add(Categories(name='economy'))
db.session.add(Categories(name='science paper'))
db.session.add(Categories(name='science'))
db.session.add(Categories(name='mythology'))
db.session.add(Categories(name='mathematics'))

db.session.add(Languages(name='CZ'))
db.session.add(Languages(name='EN'))

db.session.commit()
"""


@app.route("/", methods=['GET', 'POST'])
def login():

    password = "1234"

    if request.method == "POST":
        
        print("checking password")
        print(request.form["password"])
        
        if request.form["password"] == password:
            print("correct password")
            return redirect(url_for('edit'))

    else: return render_template("login.html")

@app.route("/edit", methods=['GET', 'POST'])
def edit():
 
    date2datetime = lambda date: datetime.strptime(date, '%Y-%m-%d')

    to_edit = False
    book_to_edit = None

    if request.method == "POST":
        print("post request incoming") 

        if 'update' in request.form:
            print("trying to add new book")
            
            if not request.form["finish_date"]: finish_date = None
            else: finish_date = date2datetime(request.form["finish_date"])

            if not request.form["added_date"]: added_date = None
            else: added_date = date2datetime(request.form["added_date"])

            if not request.form["start_date"]: start_date = None
            else: start_date = date2datetime(request.form["start_date"])

            if not request.form["pages"]: pages = None
            else: pages = request.form["pages"]

            #print(date2datetime(request.form["start_date"]))
            new_book = Books(name=request.form["name"], 
                            author=request.form["author"],
                            added_date=added_date,
                            start_date=start_date,
                            finish_date=finish_date,
                            category_id=request.form["category_id"],
                            language_id=request.form["language_id"],
                            notes=request.form["notes"],
                            pages=pages)
    
            try:
                db.session.add(new_book)
                db.session.commit()
                print("succesfully added new book")
            except:
                print("ERROR - COULDNT ADD NEW BOOK")
            
        elif 'submit_edit' in request.form:
            book = Books.query.get(request.form["book_id"])
            
            book.name=request.form["name"]
            book.author=request.form["author"]
            book.added_date=date2datetime(request.form["added_date"])
            book.start_date=date2datetime(request.form["start_date"])
            book.finish_date=date2datetime(request.form["finish_date"])
            book.category_id=request.form["category_id"]
            book.language_id=request.form["language_id"]
            book.pages=request.form["pages"]

            db.session.commit()
            print("book updated succesfully")

        elif 'edit' in request.form:
            print("editing book with id: ", request.form["book_id"])

            a = request.form["book_id"]
            #q = f"SELECT * FROM BOOKS WHERE id = {a}"
            q = f"SELECT b.id, b.name, b.author, b.added_date, b.start_date, b.finish_date, b.pages, c.name, c.id, l.name, b.notes FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE b.id = {a}"
            book_to_edit = db.session.execute(q)
          
            to_edit = True
            
        elif 'delete' in request.form:
            
            Books.query.filter_by(id=request.form["book_id"]).delete()
            db.session.commit()
            print("succesfully deleted book")         
    
    
    read_books = db.session.execute("SELECT b.id, b.name, b.author, b.added_date, b.start_date, b.finish_date, b.pages, c.name, l.name FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE finish_date IS NOT NULL")
    
    not_read_books = db.session.execute("SELECT b.id, b.name, b.author, b.added_date, b.start_date, b.finish_date, b.pages, c.name, l.name, b.notes FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE finish_date IS NULL")
    
    categories = db.session.execute('SELECT * FROM CATEGORIES')
    
    languages = db.session.execute("SELECT * FROM LANGUAGES")
    
    return render_template('edit.html', not_read_books=not_read_books, 
                                            read_books=read_books, 
                                            categories=categories, 
                                            to_edit=to_edit, 
                                            book_to_edit=book_to_edit,
                                            languages=languages)

@app.route("/statistics", methods=["POST", "GET"])
def stats():
    # using finish date
    
    #year_averages = db.session.execute("SELECT COUNT(book_id) / COUNT(DISTINCT TO_CHAR(finish_date, 'YYYY')), SUM(pages) / COUNT(DISTINCT TO_CHAR(finish_date, 'YYYY')) FROM BOOKS")
    #totals = db.session.execute("SELECT COUNT(book_id), AVG(pages)")
    #all_data = db.session.execute("SELECT * FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE finish_date IS NOT NULL")
    
    df = pd.read_sql(db.session.query(Books, Categories, Languages).filter(Books.category_id == Categories.id and Books.language_id == Languages.id).statement, db.session.bind)
    
    

    return render_template("statistics.html")

if __name__ == '__main__': 
          app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444))) 