from flask import Flask, render_template, send_file, request, url_for, redirect, g, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'

#app.secret_key = os.urandom(24)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

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
db.session.add(Categories(name='novel'))
db.session.add(Categories(name='fantasy'))
db.session.add(Categories(name='sci-fi'))
db.session.add(Categories(name='biography'))
db.session.add(Categories(name='politics'))


db.session.add(Languages(name='CZ'))
db.session.add(Languages(name='EN'))

db.session.commit()
"""




@app.route("/", methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        session.pop('user', None)
        
        if request.form["password"] == "3750":
            session['user'] = "wenceslai"
            return redirect(url_for('edit'))

        else:
            return render_template("login.html", wrong_login=True)

    return render_template("login.html", wrong_login=False)

@app.route("/logout")
def logout():
    session.pop('user', None)
    g.user = None

    return redirect(url_for('login'))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if g.user:   
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
                
                if not request.form["start_date"]: start_date = None
                else: start_date = date2datetime(request.form["start_date"])

                if not request.form["finish_date"]: finish_date = None
                else: finish_date = date2datetime(request.form["finish_date"])

                book.name=request.form["name"]
                book.author=request.form["author"]
                book.added_date=date2datetime(request.form["added_date"])
                #book.start_date=date2datetime(request.form["start_date"])
                #book.finish_date=date2datetime(request.form["finish_date"])
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

        read_books = db.session.execute("SELECT b.id, b.name, b.author, b.added_date, b.start_date, b.finish_date, b.pages, c.name, l.name FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE finish_date IS NOT NULL ORDER BY b.finish_date DESC")
        
        not_read_books = db.session.execute("SELECT b.id, b.name, b.author, b.added_date, b.start_date, b.finish_date, b.pages, c.name, l.name, b.notes FROM BOOKS b JOIN  CATEGORIES c ON (b.category_id = c.id) JOIN LANGUAGES l ON (b.language_id = l.id) WHERE finish_date IS NULL ORDER BY b.finish_date DESC")
        
        categories = db.session.execute('SELECT * FROM CATEGORIES')
        
        languages = db.session.execute("SELECT * FROM LANGUAGES")
        
        return render_template('edit.html', not_read_books=not_read_books, 
                                                read_books=read_books, 
                                                categories=categories, 
                                                to_edit=to_edit, 
                                                book_to_edit=book_to_edit,
                                                languages=languages)

    else:
        return redirect(url_for('login'))



@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']


@app.route("/statistics", methods=["POST", "GET"])
def stats():
    # using finish date
    if g.user:
        df = pd.read_sql(db.session.query(Books, Categories, Languages).join(Categories, Books.category_id == Categories.id).join(Languages, Books.language_id == Languages.id).statement, db.session.bind)

        df.to_csv("books_df.csv") # this is really bad, not working plain read sql 
        df = pd.read_csv("books_df.csv")
        
        df = df[df['finish_date'].notna()]
        df = df.drop_duplicates()

        df["finish_date"] = pd.to_datetime(df["finish_date"])
        df["added_date"] = pd.to_datetime(df["added_date"])
        df["start_date"] = pd.to_datetime(df["start_date"])
        
        year_avg = df.groupby(df['finish_date'].map(lambda x: x.year))["id"].count()
        
        years = df['finish_date'].map(lambda x: x.year).sort_values(ascending=True).unique().astype(np.int32)
        
        plt.figure(0)
        plt.xticks(range(years[0], years[-1]))
        plt.title("Number of books read each year")
        plt.plot(years, year_avg, '-o')
        
        plt.savefig("static/images/annual_counts.png")

        year_pages = df.groupby(df['finish_date'].map(lambda x: x.year))["pages"].sum()

        plt.figure(1)
        plt.xticks(range(years[0], years[-1]))
        plt.title("Number of read pages each year")
        plt.plot(years, year_pages, '-o', color="red")

        plt.savefig("static/images/annual_pages.png")
        
        total_stats = {
            "cnt" : df.id.count(),
            "pages" : df["pages"].sum(),
            "cz_cnt" : df[df["name_2"] == "CZ"].id.count(),
            "en_cnt" : df[df["name_2"] == "EN"].id.count(),
            "year_avg" : round(sum(year_avg) / len(year_avg), 2),
            "top_cats" : df.groupby(df["name_1"])["id"].count().sort_values(ascending=False).iloc[0:6]
        }
        
        annual_stats = {
            "years" : df['finish_date'].map(lambda x: x.year).sort_values(ascending=False).unique(),
            "total_cnt" : dict(df.groupby(df['finish_date'].map(lambda x: x.year))["id"].count()),
            "total_pages" : dict(df.groupby(df['finish_date'].map(lambda x: x.year))["pages"].sum()),
            "total_cz" : dict(df[df["name_2"] == "CZ"].groupby(df['finish_date'].map(lambda x: x.year)).id.count()),
            "total_en" : dict(df[df["name_2"] == "EN"].groupby(df['finish_date'].map(lambda x: x.year)).id.count()),
        }
    
        return render_template("statistics.html", total_stats=total_stats, annual_stats=annual_stats)
    
    else:
        return redirect(url_for('login'))


@app.route('/download')
def downloadFile ():
    path = "books.db"
    return send_file(path, as_attachment=True)


if __name__ == '__main__': 
          app.run(host='0.0.0.0', port="8000")