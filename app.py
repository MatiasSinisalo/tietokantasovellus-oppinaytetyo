






import secrets
from dotenv import load_dotenv
from flask import Flask, abort, url_for
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
    if "message" in session:
        message = session["message"]
        session["message"] = None
    else:
        session["message"] = None
        message = session["message"] 
    return render_template("index.html", message=message) 

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
   
    user = queryManager.getUser(username)

    if not user:
        session["message"] = "Väärä käyttäjänimi tai salansana"
        return redirect("/")
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        session["message"] = "Väärä käyttäjänimi tai salansana"
        return redirect("/")


@app.route("/logout/")
def logout():
    del session["username"]
    del session["is_admin"]
    del session["user_id"]
    del session["csrf_token"]
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
    if queryManager.addUserToDataBase(username, hash_value, adress, phonenumber):
        session["message"] = "Luotiing käyttäjä onnistuneesti!"
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        name = request.form["name"]
        publishDate = request.form["publishDate"]
        amountFree = request.form["amountFree"]
        amountOverAll = request.form["amountOverall"]
       
        authorsString = request.form['authors']
        authorsList = authorsString.split(", ")

        content = request.files['content']
        if len(content.filename) > 0:        
            bookString = filemanager.ReturnUploadedFileContents(content, ALLOWED_EXTENSIONS, UPLOAD_FOLDER)
        else:
            session["message"] = "Kirjan tiedosto oli tyhja"
            return redirect("/")
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        return render_template("manageRooms.html", rooms=rooms, reservations=reservations)
    else:
        return redirect("/")

@app.route("/manageRooms/addRoom", methods=["POST"])
def addRoom():
    if session["is_admin"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        roomId = request.form["room-id"]



        startTime = f"{request.form['startMinute']}:{request.form['startHour']} {request.form['startDay']}-{request.form['startMonth']}-{request.form['startYear']}"

        endTime = f"{request.form['endMinute']}:{request.form['endHour']} {request.form['endDay']}-{request.form['endMonth']}-{request.form['endYear']}"



        #TODO error handling
        if queryManager.addReservationTime(startTime, endTime, roomId):
             return redirect("/manageRooms/")
        else:
            return redirect("/")
    else:
        return redirect("/")

@app.route("/manageRooms/removeReservationTime", methods=["POST"])
def removeReservationTime():
    if session["is_admin"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        roomId = request.form["room-id"]

        #TODO: error handling
        if queryManager.removeRoom(roomId):
            return redirect("/manageRooms/")
        else:
            return redirect("/manageRooms/")

@app.route("/reserveRooms")
def reserveRoom():
    if session["username"]:
        roomInformation = queryManager.getAllFreeRoomReservations()
        if roomInformation:
            return render_template("reserveRooms.html", reservations=roomInformation)
        else:
            return render_template("reserveRooms.html")

@app.route("/reserveRooms/makeReservation", methods=["POST"])
def makeReservation():
    if session["username"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        reservationTimeId = request.form["reservationtime-id"]
        if queryManager.makeReservation(reservationTimeId):
            return redirect("/reserveRooms")
        else:
            return redirect("/reserveRooms")

@app.route("/reservedRoomsInformation")
def reserveRoomInformation():
    if session["username"]:
        reservedRooms = queryManager.getUsersAllReservedRooms()
        if reservedRooms:
            return render_template("reservedRoomsInformation.html", reservedRooms=reservedRooms)
        else:
            return render_template("reservedRoomsInformation.html")

@app.route("/reservedRoomsInformation/cancelReservation", methods=["POST"])
def cancelReservation():
    if session["username"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        reservationid = request.form["reservation-id"]
        queryManager.cancelReservation(reservationid)


    return redirect("/reservedRoomsInformation")



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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        bookId = request.form["book-id"]
        bookData = queryManager.getBookReadingData(bookId)
        #TODO: error handling
        return render_template("readbook.html", bookName=bookData[0], bookContent=bookData[1])
       
    else:
        return redirect("")