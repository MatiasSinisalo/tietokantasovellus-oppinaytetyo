import os
from json import load
from dotenv import load_dotenv
from flask import Flask, url_for
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

ALLOWED_EXTENSIONS = {'txt'}
UPLOAD_FOLDER = 'app/static/books'
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
    sql = "SELECT id, password FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        redirect("/")
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["user_id"] = user.id
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
    if username != '' and password != '' and adress != '' and phonenumber != '':
        sql = "SELECT COUNT(id) FROM users WHERE name=:username"
        result = db.session.execute(sql, {"username":username})
        usersWithSameName = result.fetchone()    
        if usersWithSameName[0] > 0:
            return redirect("/")


        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (name, password, adress, phonenumber) VALUES (:username, :password, :adress, :phonenumber)"
        db.session.execute(sql, {"username":username, "password":hash_value, "adress":adress, "phonenumber":phonenumber})
        db.session.commit()
    return redirect("/")

@app.route("/manageBooks")
def manageBooks():
    result = db.session.execute("SELECT * FROM books")
    books = result.fetchall()
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
        


    if name != '' and publishDate != '' and amountFree != '' and amountOverAll != '' and pathToFile != '':
        sql = "INSERT INTO books (name, publishDate, amount_free, amount_all, book_path) VALUES (:name, :publishDate, :amountFree, :amountOverAll, :pathToFile)"
        db.session.execute(sql, {"name":name, "publishDate":publishDate, "amountFree":amountFree, "amountOverAll":amountOverAll, "pathToFile": pathToFile})
        db.session.commit()
    return redirect("/manageBooks")

@app.route("/borrowBooks")
def borrowBooks():
    result = db.session.execute("SELECT * FROM books")
    books = result.fetchall()
    return render_template("borrowBooks.html", books=books)

@app.route("/borrowBooks/borrow", methods=["POST"])
def borrow():
   
    bookId = request.form["book-id"]
    if bookId == '':
         return redirect("/borrowBooks")
    sql = "SELECT COUNT(id) FROM borrows WHERE user_id=:userId AND book_id=:bookId"
    result = db.session.execute(sql, {"userId":session["user_id"], "bookId":bookId})
    maara = result.fetchone()
    if maara[0] > 0:
        return redirect("/borrowBooks")
    queryToUpdateBorrows = "INSERT INTO borrows (user_id, book_id) VALUES (:userId, :bookId)"
    queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free - 1 WHERE id=:bookId"
    db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId})
    db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
    db.session.commit()
    return redirect("/borrowBooks")

@app.route("/borrowinformation/")
def borrowinformation():
    sql = "SELECT books.id, name, publishdate FROM borrows JOIN books ON borrows.book_id = books.id;"
    result = db.session.execute(sql, {"userId":session["user_id"]})
    books = result.fetchall()
    return render_template("borrowinformation.html", books=books)

@app.route("/borrowinformation/returnBook", methods=["POST"])
def returnBook():
    bookId = request.form["book-id"]
    if bookId == '':
         return redirect("/borrowBooks")
    
    queryToUpdateBorrows = "DELETE FROM borrows WHERE user_id=:userId AND book_id=:bookId"
    queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free + 1 WHERE id=:bookId"
    db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId})
    db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
    db.session.commit()
    
    return redirect("/borrowinformation/")