# File handling(save, load, generating)
import sqlite3

from _Classes import Card

cards_file = "cards.txt"
workers_file = "workers.txt"
entries_file = "entries.txt"

used_database = "system.db"


def calc_card_num(card_str):
    if card_str == 0 or card_str == "0":
        return 0
    card_arr = card_str[1:len(card_str) - 1]
    card_id = list(map(int, card_arr.split(",")))
    return card_id


def load_cards():
    connection = sqlite3.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cards_database")
    cards_db = cursor.fetchall()
    cards = []
    for card in cards_db:
        cards.append(Card(calc_card_num(card[0])))
    connection.commit()
    connection.close()
    return cards