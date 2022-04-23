CREATE SCHEMA IF NOT EXISTS tietokantasovellus_kirjastonhallinta;

CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    name varchar(100),
    password varchar,
    adress varchar(100) DEFAULT NULL,
    phonenumber varchar(20) DEFAULT NULL,
    is_admin boolean DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Books (
    id SERIAL PRIMARY KEY,
    name varchar(100),
    publishDate varchar(100),
    amount_free int,
    amount_all int
);

CREATE TABLE IF NOT EXISTS BookContents(
    id SERIAL PRIMARY KEY,
    content varchar,
    book_id integer,
    CONSTRAINT fk_books FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Borrows(
    id SERIAL PRIMARY KEY,
    user_id integer,
    book_id integer,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    borrow_end_date DATE NOT NULL,
    CONSTRAINT fk_users FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_books FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Authors(
    id SERIAL PRIMARY KEY,
    name varchar(100),
    book_id integer,
    CONSTRAINT fk_books FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MeetingRooms(
    id SERIAL PRIMARY KEY,
    name varchar(100),
    description varchar
);

CREATE TABLE IF NOT EXISTS MeetingRoomReserveTimes(
    id SERIAL PRIMARY KEY,
    time_block_start TIMESTAMP,
    time_block_end TIMESTAMP,
    is_reserved BOOLEAN DEFAULT FALSE,
    meeting_room_id integer,
    CONSTRAINT fk_meeting_rooms FOREIGN KEY (meeting_room_id) REFERENCES MeetingRooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MeetingRoomReservations(
    id SERIAL PRIMARY KEY,
    user_id integer,
    meeting_room_reserve_times_id integer,
    CONSTRAINT fk_users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT fk_meetingRoomReserveTimes FOREIGN KEY (meeting_room_reserve_times_id) REFERENCES MeetingRoomReserveTimes(id) ON DELETE CASCADE
);