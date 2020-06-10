#!/usr/bin/env python3

import sqlite3 as sql
import os
from _Classes import Worker, Card

database_name = "system.db"
unrecognized_table = "unrecognized_table"
workers_table = "workers_database"
cards_table = "cards_database"
workers_log = "workers_log"


def fill_workers_db():
    workers = [Worker("Jan", "Kowalski"),
               Worker("Anna", "Nowak"),
               Worker("Tomasz", "Armstrong"),
               Worker("Zuzanna", "Mozart"),
               Worker("Antoni", "Skłodowski")]
    connection = sql.connect(database_name)
    for i in range(len(workers)):
        cursor = connection.cursor()
        w = workers[i]
        cursor.execute("INSERT INTO workers_database VALUES (?,?,?,?)",
                       (w.number, w.name, w.surname, w.card))
        connection.commit()
    connection.close()


def fill_cards_db(count):
    connection = sql.connect(database_name)
    for i in range(count):
        card = Card()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cards_database VALUES (?)",
                       (str(card.uid),))
        connection.commit()
    connection.close()


def create_database():
    if os.path.exists(database_name):
        os.remove(database_name)
        print("An old logs database removed.")
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE workers_log (
        log_time text,
        terminal_id text,
        card text,
        worker_id text
    )""")
    print("The workers_log table created.")
    cursor.execute(""" CREATE TABLE workers_database (
                id text,
                name text,
                surname text,
                cardNumber text 
            )""")
    print("The workers table created.")
    cursor.execute(""" CREATE TABLE unrecognized_table (
                   card_id text,
                   data text,
                   terminal_id text
               )""")
    print("The unrecognized entries table created.")
    cursor.execute(""" CREATE TABLE cards_database (
                   id text
               )""")
    print("The cards table created.")
    connection.commit()
    connection.close()
    print("The new database created.")


def assign_default_cards():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cards_database")
    cards_db = cursor.fetchall()

    conn2 = sql.connect(database_name)
    curs_work = conn2.cursor()
    curs_work.execute("SELECT * FROM workers_database")
    work_db = curs_work.fetchall()
    for i in range(len(work_db)):
        curs_work.execute("""Update workers_database set cardNumber = (?) where id = (?)""",
                          (cards_db[i][0], work_db[i][0]))

    conn2.commit()
    conn2.close()
    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    fill_workers_db()
    fill_cards_db(10)
    assign_default_cards()
