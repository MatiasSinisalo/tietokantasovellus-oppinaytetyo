CREATE SCHEMA IF NOT EXISTS tietokantasovellus_kirjastonhallinta;

CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    name varchar(100),
    password varchar,
    adress varchar(100),
    phonenumber varchar(20)
);

CREATE TABLE IF NOT EXISTS Books (
    id SERIAL PRIMARY KEY,
    name varchar(100),
    publishDate varchar(100),
    amount_free int,
    amount_all int
    
);

CREATE TABLE IF NOT EXISTS Borrows(
    id SERIAL PRIMARY KEY,
    user_id integer,
    book_id integer,
    CONSTRAINT fk_users FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_books FOREIGN KEY (book_id) REFERENCES books(id)
);


CREATE TABLE IF NOT EXISTS Authors(
    id SERIAL PRIMARY KEY,
    name varchar(100),
    book_id integer,
    CONSTRAINT fk_books FOREIGN KEY (book_id) REFERENCES books(id)
);