
import os
from json import load
from re import template
from dotenv import load_dotenv
from flask import Flask, url_for
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import queries

app = Flask(__name__)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

ALLOWED_EXTENSIONS = {'txt'}
UPLOAD_FOLDER = '/static/books'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/")
def index():
   # result = db.session.execute("SELECT * FROM users")
   # users = result.fetchall()
    return render_template("index.html") 

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
   
    user = queries.getUser(username)

    if not user:
        return redirect("/")
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin
        return redirect("/")
    else:
        return redirect("/")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/createaccount")
def createaccount():        
    return render_template("createAccount.html")


@app.route("/createaccount/addaccount", methods=["POST"])
def addaccount():        
    username = request.form["username"]
    password = request.form["password"]
    adress = request.form["adress"]
    phonenumber = request.form["phonenumber"]
   
    hash_value = generate_password_hash(password)
   
    #TODO: error handling
    if queries.addUserToDataBase(username, hash_value, adress, phonenumber):
        return redirect("/")
    else:
        return redirect("/")

@app.route("/manageBooks")
def manageBooks():
    books = []
    if session["is_admin"]:
        books = queries.getAllBooks()
    return render_template("manageBooks.html", count=len(books), books=books)

#help from: https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/ for handling file uploads
@app.route("/manageBooks/addBook", methods=["POST"])
def addBook():
    name = request.form["name"]
    publishDate = request.form["publishDate"]
    amountFree = request.form["amountFree"]
    amountOverAll = request.form["amountOverall"]
    content = request.files['content']        
    filename = content.filename
    pathToFile = ''
    if filename.split(".", 1)[1] in ALLOWED_EXTENSIONS:
        filenameToWrite = secure_filename(filename)
        pathToFile = os.path.join(app.config['UPLOAD_FOLDER'], filenameToWrite)
        content.save(pathToFile)
        
    #TODO: error handling
    if queries.insertBook(name, publishDate, amountFree, amountOverAll, pathToFile):
        return redirect("/manageBooks")
    else:
        return redirect("/manageBooks")
   
  
   

@app.route("/borrowBooks")
def borrowBooks():
    books = queries.getAllBooks()
    return render_template("borrowBooks.html", books=books)

@app.route("/borrowBooks/borrow", methods=["POST"])
def borrow():
   
    bookId = request.form["book-id"]
     #TODO: error handling
    if queries.borrowBook(bookId):
       return redirect("/borrowBooks")
    else:
        return redirect("/borrowBooks")

@app.route("/borrowinformation/")
def borrowinformation():

    books = queries.getBooksOfUser()
    
    return render_template("borrowinformation.html", books=books)

@app.route("/borrowinformation/returnBook", methods=["POST"])
def returnBook():
    bookId = request.form["book-id"]
    #TODO: error handling
    if queries.returnBook(bookId):
        return redirect("/borrowinformation/")
    else:
        return redirect("/borrowInformation")

@app.route("/readBook", methods=["POST"])
def readBook():
    bookId = request.form["book-id"]
   
    bookData = queries.getBookReadingData(bookId)
    #TODO: error handling
    if bookData:
        bookFile = open(bookData.book_path, "r")
        bookContent = []
        for rivi in bookFile:
            bookContent.append(rivi)
        return render_template("readbook.html", bookName=bookData.name, bookContent=bookContent)
    else:
        return render_template("/borrowInformation")