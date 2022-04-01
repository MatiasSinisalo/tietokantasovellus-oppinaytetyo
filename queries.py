from dotenv import load_dotenv
from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from os import getenv




from werkzeug.security import check_password_hash, generate_password_hash
app = Flask(__name__)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

def addUserToDataBase(username, hash_value, adress, phonenumber):
     if username != '' and hash_value != '' and adress != '' and phonenumber != '':
        sql = "SELECT COUNT(id) FROM users WHERE name=:username"
        result = db.session.execute(sql, {"username":username})
        usersWithSameName = result.fetchone()    
        if usersWithSameName[0] > 0:
            return False

        sql = "INSERT INTO users (name, password, adress, phonenumber) VALUES (:username, :password, :adress, :phonenumber)"
        db.session.execute(sql, {"username":username, "password":hash_value, "adress":adress, "phonenumber":phonenumber})
        db.session.commit()
        return True

def getUser(username):
    sql = "SELECT id, password, is_admin FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    return user    

def getAllBooks():
     result = db.session.execute("SELECT * FROM books")
     books = result.fetchall()
     return books

def insertBook(name, publishDate, amountFree, amountOverAll, pathToFile):
    if name != '' and publishDate != '' and amountFree != '' and amountOverAll != '' and pathToFile != '':
        sql = "INSERT INTO books (name, publishDate, amount_free, amount_all, book_path) VALUES (:name, :publishDate, :amountFree, :amountOverAll, :pathToFile)"
        db.session.execute(sql, {"name":name, "publishDate":publishDate, "amountFree":amountFree, "amountOverAll":amountOverAll, "pathToFile": pathToFile})
        db.session.commit()

def borrowBook(bookId):
    if bookId == '':
         return False
  
    sql = "SELECT COUNT(id) FROM borrows WHERE user_id=:userId AND book_id=:bookId"
    result = db.session.execute(sql, {"userId":session["user_id"], "bookId":bookId})
    maara = result.fetchone()
    if maara[0] > 0:
        return False
    queryToUpdateBorrows = "INSERT INTO borrows (user_id, book_id) VALUES (:userId, :bookId)"
    queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free - 1 WHERE id=:bookId"
    db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId})
    db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
    db.session.commit()
    return True

def getBooksOfUser():
    sql = "SELECT books.id, name, publishdate FROM borrows JOIN books ON borrows.book_id = books.id WHERE borrows.user_id=:userId;"
    result = db.session.execute(sql, {"userId":session["user_id"]})
    books = result.fetchall()
    return books

def returnBook(bookId):
    if bookId == '':
         return False
    
    queryToUpdateBorrows = "DELETE FROM borrows WHERE user_id=:userId AND book_id=:bookId"
    queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free + 1 WHERE id=:bookId"
    db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId})
    db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
    db.session.commit()
    return True

def getBookReadingData(bookId):
    if bookId == '':
        return None
    sql = "SELECT books.name, book_path FROM borrows JOIN books ON books.id = borrows.book_id WHERE borrows.user_id =:userId AND borrows.book_id =:bookId"
    result = db.session.execute(sql, {"userId":session["user_id"], "bookId":bookId})
    bookData = result.fetchone()
    return bookData