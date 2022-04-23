




from dotenv import load_dotenv
from flask import Flask, url_for
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from queries import QueryManager
import filemanager

app = Flask(__name__)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL_POSTGRES")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

ALLOWED_EXTENSIONS = {'txt'}
UPLOAD_FOLDER = 'static/books/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

queryManager = QueryManager(db)


@app.route("/")
def index():
   # result = db.session.execute("SELECT * FROM users")
   # users = result.fetchall()
    return render_template("index.html") 

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
   
    user = queryManager.getUser(username)

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


@app.route("/logout/")
def logout():
    del session["username"]
    del session["is_admin"]
    del session["user_id"]
    return redirect("/")

@app.route("/createaccount/")
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
    if queryManager.addUserToDataBase(username, hash_value, adress, phonenumber):
        return redirect("/")
    else:
        return redirect("/")

@app.route("/manageBooks/")
def manageBooks():
    if session["is_admin"]:
        books = []
        if session["is_admin"]:
            books = queryManager.getAllBooks()
        return render_template("manageBooks.html", count=len(books), books=books)
    else:
        return redirect("/")


#help from: https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/ for handling file uploads
@app.route("/manageBooks/addBook", methods=["POST"])
def addBook():
    if session["is_admin"]:
        name = request.form["name"]
        publishDate = request.form["publishDate"]
        amountFree = request.form["amountFree"]
        amountOverAll = request.form["amountOverall"]
       
        authorsString = request.form['authors']
        authorsList = authorsString.split(", ")

        content = request.files['content']        
        bookString = filemanager.ReturnUploadedFileContents(content, ALLOWED_EXTENSIONS, UPLOAD_FOLDER)
        
        #TODO: error handling
        if bookString:
            
            insertedBookId = queryManager.insertBook(name, publishDate, amountFree, amountOverAll, bookString)
            
            if insertedBookId:
                queryManager.addAuthorsToBook(insertedBookId, authorsList)           
                return redirect("/manageBooks")
            else:
                return redirect("/manageBooks")
        else:
            return redirect("/manageBooks")
    else:
        return redirect("/")
   
@app.route("/manageBooks/removeBook", methods=["POST"])
def removeBook():
    if session["is_admin"]:
        bookId = request.form["book-id"]
        #TODO: error handling
        if bookId != '':
            bookFilePathToRemove = queryManager.removeBook(bookId)
        return redirect("/manageBooks")
    return redirect("/")

@app.route("/manageRooms/")
def manageRooms():
    if session["is_admin"]:
        rooms = []
        rooms = queryManager.getAllRooms()
        reservations = queryManager.getAllRoomReservations()
        filteredReservations = []
        for reservation in reservations:
            if reservation.time_block_start != None and reservation.time_block_end != None:
                filteredReservations.append(reservation)
        return render_template("manageRooms.html", rooms=rooms, reservations=filteredReservations)
    else:
        return redirect("/")

@app.route("/manageRooms/addRoom", methods=["POST"])
def addRoom():
    if session["is_admin"]:
        roomName = request.form["name"]
        roomDescription = request.form["roomDescription"]
        
        #TODO error handling
        if queryManager.addRoom(roomName, roomDescription):
             return redirect("/manageRooms/")
        else:
            return redirect("/manageRooms/")
    else:
        return redirect("/")

@app.route("/manageRooms/addReservation", methods=["POST"])
def addReservation():
    if session["is_admin"]:
        roomId = request.form["room-id"]
        startTime = request.form["startTime"]
        endTime = request.form["endTime"]


        #TODO error handling
        if queryManager.addReservationTime(startTime, endTime, roomId):
             return redirect("/manageRooms/")
        else:
            return redirect("/manageRooms/")
    else:
        return redirect("/")

@app.route("/manageRooms/removeReservationTime", methods=["POST"])
def removeReservationTime():
    if session["is_admin"]:
        roomId = request.form["room-id"]
        #TODO error handling
        if queryManager.removeReservationTime(roomId):
             return redirect("/manageRooms/")
        else:
            return redirect("/manageRooms/")
    else:
        return redirect("/")

@app.route("/manageRooms/removeRoom", methods=["POST"])
def removeRoom():
    if session["is_admin"]:
        roomId = request.form["room-id"]

        #TODO: error handling
        if queryManager.removeRoom(roomId):
            return redirect("/manageRooms/")
        else:
            return redirect("/manageRooms/")




@app.route("/borrowBooks/")
def borrowBooks():
    if session["username"]:
        books = queryManager.getAllBooks()
        return render_template("borrowBooks.html", books=books)
    else:
        return redirect("/")

@app.route("/borrowBooks/borrow", methods=["POST"])
def borrow():
    if session["username"]:
        bookId = request.form["book-id"]
        borrowDuration = 14 #in the form of days from this day
        #TODO: error handling
        if queryManager.borrowBook(bookId, borrowDuration):
            return redirect("/borrowBooks")
        else:
            return redirect("/borrowBooks")
    else:
        return redirect("/")

@app.route("/borrowinformation/")
def borrowinformation():
    if session["username"]:
        books = queryManager.getBooksOfUser()
        
        return render_template("borrowinformation.html", books=books)
    else:
        return redirect("/")

@app.route("/borrowinformation/returnBook", methods=["POST"])
def returnBook():
    if session["username"]:
        bookId = request.form["book-id"]
        #TODO: error handling
        if queryManager.returnBook(bookId):
            return redirect("/borrowinformation")
        else:
            return redirect("/borrowInformation")
    else:
        return redirect("/")

@app.route("/readBook", methods=["POST"])
def readBook():
    if session["username"]:
        bookId = request.form["book-id"]
        bookData = queryManager.getBookReadingData(bookId)
        #TODO: error handling
        return render_template("readbook.html", bookName=bookData[0], bookContent=bookData[1])
       
    else:
        return redirect("")