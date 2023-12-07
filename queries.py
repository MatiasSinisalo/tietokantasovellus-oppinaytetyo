
from dotenv import load_dotenv
from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text







from werkzeug.security import check_password_hash, generate_password_hash


class QueryManager:
    def __init__(self, db):
        load_dotenv()
        self.db = db
        
        
    def addUserToDataBase(self, username, hash_value, adress, phonenumber):
        if username != '' and hash_value != '':
            sql = "SELECT COUNT(id) FROM users WHERE name=:username"
            result = self.db.session.execute(text(sql), {"username":username})
            usersWithSameName = result.fetchone()    
            if usersWithSameName[0] > 0:
                session["message"] = "Virhe tiliä luodessa: käyttäjä on jo olemassa"
                return False

            sql = "INSERT INTO users (name, password, adress, phonenumber) VALUES (:username, :password, :adress, :phonenumber)"
            self.db.session.execute(text(sql), {"username":username, "password":hash_value, "adress":adress, "phonenumber":phonenumber})
            self.db.session.commit()
            return True
        else:
            session["message"] = "Virhe tiliä luodessa: salasana tai käyttäjänimi puuttuu"
            return False

    def getUser(self, username):
        sql = "SELECT id, password, is_admin FROM users WHERE name=:username"
        result = self.db.session.execute(text(sql), {"username":username})
        user = result.fetchone()
        return user    

    def getAllBooks(self):
        result = self.db.session.execute(text("SELECT * FROM books"))
        books = result.fetchall()
        allBookInformationList = []
        for book in books:
            authorsOfBook = self.getAuthorsOfBook(book[0])
            allBookInformationList.append((book, authorsOfBook))
        return allBookInformationList

    def insertBook(self, name, publishDate, amountFree, amountOverAll, fileString):
        if name != '' and publishDate != '' and amountFree != '' and amountOverAll != '' and fileString != '':
            sql = "INSERT INTO books (name, publishDate, amount_free, amount_all) VALUES (:name, :publishDate, :amountFree, :amountOverAll) RETURNING id"
            queryResult = self.db.session.execute(text(sql), {"name":name, "publishDate":publishDate, "amountFree":amountFree, "amountOverAll":amountOverAll})
            insertedBookId = queryResult.fetchone()[0]
            
            sqlToInsertBookString = "INSERT INTO bookcontents (content, book_id) VALUES (:fileString, :insertedBookId)"
            self.db.session.execute(text(sqlToInsertBookString), {"fileString":fileString, "insertedBookId":insertedBookId})
            self.db.session.commit()
            return insertedBookId
        return False

    def addAuthorsToBook(self, book_id, authorsList):
        if book_id == '' or authorsList == '':
            return False
        for author in authorsList:
            sql = "INSERT INTO authors (name, book_id) VALUES (:author, :book_id)"
            self.db.session.execute(text(sql), {"author":author, "book_id":book_id})
        self.db.session.commit()
                    
    def removeBook(self, id):
        if id != '':
            sqlToRemoveTheBook = "DELETE FROM books WHERE id=:id"
            self.db.session.execute(text(sqlToRemoveTheBook), {"id":id})
            self.db.session.commit()
            return True
        return False
            

    def borrowBook(self, bookId, borrow_days):
        if bookId == '' or borrow_days == '':
            return False
        
        sqlCheckAvailable = "SELECT amount_free from books WHERE id=:bookId"
        result = self.db.session.execute(text(sqlCheckAvailable), {"bookId":bookId})
        amountFree = result.fetchone()
        if amountFree.amount_free < 1:
            return False

        
        sql = "SELECT COUNT(id) FROM borrows WHERE user_id=:userId AND book_id=:bookId"
        result = self.db.session.execute(text(sql), {"userId":session["user_id"], "bookId":bookId})
        usersNumberOfBorrows = result.fetchone()
        if usersNumberOfBorrows.count > 0:
            return False
        
        queryToUpdateBorrows = "INSERT INTO borrows (user_id, book_id, borrow_end_date) VALUES (:userId, :bookId, CURRENT_DATE + :borrow_days)"
        queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free - 1 WHERE id=:bookId"
        self.db.session.execute(text(queryToUpdateBorrows), {"userId":session["user_id"], "bookId":bookId, "borrow_days": borrow_days})
        self.db.session.execute(text(queryToUpdateBookAmounts), {"bookId":bookId})
        self.db.session.commit()
        return True


    def checkForBorrowsThatEnded(self, userId):
        sql = "SELECT book_id FROM borrows WHERE CURRENT_DATE > borrow_end_date AND user_id = :userId"
        result = self.db.session.execute(text(sql), {"userId":userId})
        bookIdsToBeRemoved = result.fetchall()
        for bookId in bookIdsToBeRemoved:
            self.returnBook(bookId[0])
     
    def getBooksOfUser(self):
    
        self.checkForBorrowsThatEnded(session["user_id"])
    
        sql = "SELECT books.id, books.name, books.publishDate, borrow_date, borrow_end_date FROM borrows JOIN books ON borrows.book_id = books.id WHERE borrows.user_id=:userId;"
        result = self.db.session.execute(text(sql), {"userId":session["user_id"]})
        books = result.fetchall()
        
        allBookInformationList = []
        for book in books:
            authorsOfBook = self.getAuthorsOfBook(book[0])
            allBookInformationList.append((book, authorsOfBook))

        return allBookInformationList

    def getAuthorsOfBook(self, bookId):
        sql = "SELECT name FROM authors WHERE book_id=:bookId"
        result = self.db.session.execute(text(sql), {"bookId":bookId})
        authorsList = result.fetchall()
        return authorsList



    def returnBook(self, bookId):
        if bookId == '':
            return False
        
        queryToUpdateBorrows = "DELETE FROM borrows WHERE user_id=:userId AND book_id=:bookId"
        queryToUpdateBookAmounts = "UPDATE books SET amount_free = amount_free + 1 WHERE id=:bookId"
        self.db.session.execute(text(queryToUpdateBorrows), {"userId":session["user_id"], "bookId":bookId})
        self.db.session.execute(text(queryToUpdateBookAmounts), {"bookId":bookId})
        self.db.session.commit()
        return True

    def getBookReadingData(self, bookId):
        if bookId == '':
            return None
        sql = "SELECT books.name, book_id FROM borrows JOIN books ON books.id = borrows.book_id WHERE borrows.user_id =:userId AND borrows.book_id =:bookId"
        result = self.db.session.execute(text(sql), {"userId":session["user_id"], "bookId":bookId})
        bookData = result.fetchone()
        if bookData.book_id != '':
            sqlToGetBookContent = "SELECT content FROM bookcontents WHERE book_id=:bookId"
            result = self.db.session.execute(text(sqlToGetBookContent), {"bookId":bookData.book_id})
            bookString = result.fetchone()
        return (bookData[0], bookString.content)

    def addRoom(self, name, roomDescription):
        if name == '' or roomDescription == '':
            return False
        sql = "INSERT INTO meetingrooms (name, description) VALUES (:name, :roomDescription)"
        self.db.session.execute(text(sql), {"name":name, "roomDescription":roomDescription})
        self.db.session.commit()
        return True
    
    def getAllRooms(self):
        sql = "SELECT id, name, description FROM meetingrooms"
        result = self.db.session.execute(text(sql))
        rooms = result.fetchall()
        return rooms
    
    def getAllRoomReservations(self):
        sql  = "SELECT meetingrooms.id, meetingrooms.name, time_block_start, time_block_end, meetingroomreservetimes.id FROM meetingrooms LEFT JOIN meetingroomreservetimes ON meetingrooms.id = meetingroomreservetimes.meeting_room_id WHERE time_block_start IS NOT NULL AND time_block_end IS NOT NULL"
        result = self.db.session.execute(text(sql))
        reservations = result.fetchall()
        return reservations


    def getAllFreeRoomReservations(self):
        sql  = "SELECT meetingrooms.id, meetingrooms.name, meetingrooms.description, time_block_start, time_block_end, meetingroomreservetimes.id FROM meetingrooms LEFT JOIN meetingroomreservetimes ON meetingrooms.id = meetingroomreservetimes.meeting_room_id WHERE time_block_start IS NOT NULL AND time_block_end IS NOT NULL AND is_reserved IS FALSE"
        result = self.db.session.execute(text(sql))
        reservations = result.fetchall()
        return reservations

    def getAllRoomInformation(self):
        sql  = "SELECT meetingrooms.id, meetingrooms.name, meetingrooms.description, time_block_start, time_block_end, meetingroomreservetimes.id FROM meetingrooms LEFT JOIN meetingroomreservetimes ON meetingrooms.id = meetingroomreservetimes.meeting_room_id WHERE time_block_start IS NOT NULL AND time_block_end IS NOT NULL AND is_reserved IS FALSE"
        result = self.db.session.execute(text(sql))
        information = result.fetchall()
        return information


    def removeRoom(self, roomId):
        if roomId == '':
            return False
        sql = "DELETE FROM meetingrooms WHERE id = :roomId"
        self.db.session.execute(text(sql), {"roomId":roomId})
        self.db.session.commit()
        return True
    
  
    
    def addReservationTime(self, time_block_start, time_block_end, roomId):
        if time_block_start == '' or time_block_end == '' or roomId == '':
            return False
        try:
            sql = "INSERT INTO meetingRoomReserveTimes (time_block_start, time_block_end, meeting_room_id) VALUES (TO_TIMESTAMP(:time_block_start, 'MI:HH24 DD-MM-YYYY'), TO_TIMESTAMP(:time_block_end, 'MI:HH24 DD-MM-YYYY'), :roomId)"
            self.db.session.execute(text(sql), {"time_block_start":time_block_start, "time_block_end":time_block_end, "roomId":roomId})
            self.db.session.commit()
            return True
        except:
            session["message"] = "Virhe lisättäessä aikaa tietokantaan"
            return False
   
    
    def removeReservationTime(self, roomId):
        if roomId == '' or roomId == 'None':
            return False
        sql = "DELETE FROM meetingRoomReserveTimes WHERE id = :roomId"
        self.db.session.execute(text(sql), {"roomId":roomId})
        self.db.session.commit()
        return True

    def makeReservation(self, reservationTimeId):
        if reservationTimeId == '':
            return False
        
        sqlToCheckIfRoomIsFree = "SELECT is_reserved FROM meetingRoomReserveTimes WHERE id=:reservationTimeId"
        result = self.db.session.execute(text(sqlToCheckIfRoomIsFree), {"reservationTimeId":reservationTimeId})
        
        isReserved = result.fetchone()[0]
        if isReserved:
            return False
        
        sqlToUpdateIsReservedBool = "UPDATE meetingRoomReserveTimes SET is_reserved = True WHERE id=:reservationTimeId"
        self.db.session.execute(text(sqlToUpdateIsReservedBool), {"reservationTimeId":reservationTimeId})
        
        sqlToUpdateReservations = "INSERT INTO MeetingRoomReservations (user_id, meeting_room_reserve_times_id) VALUES (:userId, :reservationTimeId)"
        self.db.session.execute(text(sqlToUpdateReservations), {"userId":session["user_id"], "reservationTimeId":reservationTimeId})
        
        self.db.session.commit()

        return True
    
    def cancelReservation(self, reservationId):
        if reservationId == '':
            return False
        sqlToUpdateReservations = "DELETE FROM MeetingRoomReservations WHERE id=:reservationId AND user_id=:userId RETURNING meeting_room_reserve_times_id"
        result = self.db.session.execute(text(sqlToUpdateReservations), {"reservationId":reservationId, "userId":session["user_id"]})
        reservationTimeId = result.fetchone()[0]
        if reservationTimeId != None:
           sqlToUpdateReservationTimes = "UPDATE meetingRoomReserveTimes SET is_reserved = False WHERE id=:reservationTimeId"
           self.db.session.execute(text(sqlToUpdateReservationTimes), {"reservationTimeId":reservationTimeId})
           self.db.session.commit()

    def getUsersAllReservedRooms(self):
        sql = "SELECT mr.id id, m.name name, m.description description, mt.time_block_start start, mt.time_block_end end FROM meetingRoomReservations mr JOIN meetingRoomReserveTimes mt ON mr.meeting_room_reserve_times_id = mt.id JOIN MeetingRooms m ON m.id = mt.meeting_room_id WHERE mr.user_id = :userId"
        result = self.db.session.execute(text(sql), {"userId":session["user_id"]})
        reservationInfo = result.fetchall()
        return reservationInfo
       
