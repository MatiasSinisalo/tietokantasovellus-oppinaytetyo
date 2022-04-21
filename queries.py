from dotenv import load_dotenv
from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy import false




from werkzeug.security import check_password_hash, generate_password_hash


class QueryManager:
    def __init__(self, db):
        load_dotenv()
        self.db = db
        
        
    def addUserToDataBase(self, username, hash_value, adress, phonenumber):
        if username != '' and hash_value != '' and adress != '' and phonenumber != '':
            sql = "SELECT COUNT(id) FROM users WHERE name=:username"
            result = self.db.session.execute(sql, {"username":username})
            usersWithSameName = result.fetchone()    
            if usersWithSameName[0] > 0:
                return False

            sql = "INSERT INTO users (name, password, adress, phonenumber) VALUES (:username, :password, :adress, :phonenumber)"
            self.db.session.execute(sql, {"username":username, "password":hash_value, "adress":adress, "phonenumber":phonenumber})
            self.db.session.commit()
            return True

    def getUser(self, username):
        sql = "SELECT id, password, is_admin FROM users WHERE name=:username"
        result = self.db.session.execute(sql, {"username":username})
        user = result.fetchone()
        return user    

    def getAllBooks(self):
        result = self.db.session.execute("SELECT * FROM books")
        books = result.fetchall()
        allBookInformationList = []
        for book in books:
            authorsOfBook = self.getAuthorsOfBook(book[0])
            allBookInformationList.append((book, authorsOfBook))
        return allBookInformationList

    def insertBook(self, name, publishDate, amountFree, amountOverAll, fileString):
        if name != '' and publishDate != '' and amountFree != '' and amountOverAll != '' and fileString != '':
            sql = "INSERT INTO books (name, publishDate, amount_free, amount_all) VALUES (:name, :publishDate, :amountFree, :amountOverAll) RETURNING id"
            queryResult = self.db.session.execute(sql, {"name":name, "publishDate":publishDate, "amountFree":amountFree, "amountOverAll":amountOverAll})
            insertedBookId = queryResult.fetchone()[0]

            sqlToInsertBookString = "INSERT INTO bookcontents (content, book_id) VALUES (:fileString, :insertedBookId)"
            self.db.session.execute(sqlToInsertBookString, {"fileString":fileString, "insertedBookId":insertedBookId})
            self.db.session.commit()
            return insertedBookId
        return False

    def addAuthorsToBook(self, book_id, authorsList):
        if book_id == '' or authorsList == '':
            return false
        for author in authorsList:
            sql = "INSERT INTO authors (name, book_id) VALUES (:author, :book_id)"
            self.db.session.execute(sql, {"author":author, "book_id":book_id})
        self.db.session.commit()
                    
    def removeBook(self, id):
        if id != '':
            sqlToRemoveTheBook = "DELETE FROM books WHERE id=:id"
            self.db.session.execute(sqlToRemoveTheBook, {"id":id})
            self.db.session.commit()
            return True
        return False
            

    def borrowBook(self, bookId, borrow_days):
        if bookId == '' or borrow_days == '':
            return False
        
        sqlCheckAvailable = "SELECT amount_free from books WHERE id=:bookId"
        result = self.db.session.execute(sqlCheckAvailable, {"bookId":bookId})
        amountFree = result.fetchone()
        if amountFree.amount_free < 1:
            return False

        
        sql = "SELECT COUNT(id) FROM borrows WHERE user_id=:userId AND book_id=:bookId"
        result = self.db.session.execute(sql, {"userId":session["user_id"], "bookId":bookId})
        usersNumberOfBorrows = result.fetchone()
        if usersNumberOfBorrows.count > 0:
            return False
        
        queryToUpdateBorrows = "INSERT INTO borrows (user_id, book_id, borrow_end_date) VALUES (:userId, :bookId, CURRENT_DATE + :borrow_days)"
        queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free - 1 WHERE id=:bookId"
        self.db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId, "borrow_days": borrow_days})
        self.db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
        self.db.session.commit()
        return True


    def checkForBorrowsThatEnded(self, userId):
        sql = "SELECT book_id FROM borrows WHERE CURRENT_DATE > borrow_end_date AND user_id = :userId"
        result = self.db.session.execute(sql, {"userId":userId})
        bookIdsToBeRemoved = result.fetchall()
        for bookId in bookIdsToBeRemoved:
            self.returnBook(bookId[0])
        
    def getBooksOfUser(self):
    
        self.checkForBorrowsThatEnded(session["user_id"])
    
        sql = "SELECT books.id, books.name, books.publishDate, borrow_date, borrow_end_date FROM borrows JOIN books ON borrows.book_id = books.id WHERE borrows.user_id=:userId;"
        result = self.db.session.execute(sql, {"userId":session["user_id"]})
        books = result.fetchall()
        
        allBookInformationList = []
        for book in books:
            authorsOfBook = self.getAuthorsOfBook(book[0])
            allBookInformationList.append((book, authorsOfBook))

        return allBookInformationList

    def getAuthorsOfBook(self, bookId):
        sql = "SELECT name FROM authors WHERE book_id=:bookId"
        result = self.db.session.execute(sql, {"bookId":bookId})
        authorsList = result.fetchall()
        return authorsList



    def returnBook(self, bookId):
        if bookId == '':
            return False
        
        queryToUpdateBorrows = "DELETE FROM borrows WHERE user_id=:userId AND book_id=:bookId"
        queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free + 1 WHERE id=:bookId"
        self.db.session.execute(queryToUpdateBorrows, {"userId":session["user_id"], "bookId":bookId})
        self.db.session.execute(queryToUpdateBookAmounts, {"bookId":bookId})
        self.db.session.commit()
        return True

    def getBookReadingData(self, bookId):
        if bookId == '':
            return None
        sql = "SELECT books.name, book_id FROM borrows JOIN books ON books.id = borrows.book_id WHERE borrows.user_id =:userId AND borrows.book_id =:bookId"
        result = self.db.session.execute(sql, {"userId":session["user_id"], "bookId":bookId})
        bookData = result.fetchone()
        if bookData.book_id != '':
            sqlToGetBookContent = "SELECT content FROM bookcontents WHERE book_id=:bookId"
            result = self.db.session.execute(sqlToGetBookContent, {"bookId":bookData.book_id})
            bookString = result.fetchone()
        return (bookData[0], bookString.content)

    def addRoom(self):
        return 0
    
    def getAllRooms(self):
        return 0