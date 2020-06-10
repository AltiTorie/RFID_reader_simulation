import paho.mqtt.client as mqtt
import csv
import keyboard
import datetime
from _Classes import Worker, Card
import os
import sqlite3 as sql
import time
import _conf

# The broker name or IP address.
broker = _conf.broker  # change broker name to hostname provided
# in certificate configuration, please refer to section OpenSSL-step 4

# TLS port
port = _conf.port  # set up new port for TLS
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client("Office")

# for creating new card
last_card = None
is_empty = True
reading = False

database_name = "system.db"


def process_message(cl, usr_data, message):
    # Decode message.
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    if message.topic == "office/info":
        process_connection_message(message_decoded)
    elif message.topic == "office/card/id":
        process_card(message_decoded)


def process_connection_message(message_decoded):
    print(f"{message_decoded[0]} : {message_decoded[1]}")


def calc_card_num(card_str):
    if card_str == 0 or card_str == "0":
        return 0
    card_arr = card_str[1:len(card_str) - 1]
    card_id = list(map(int, card_arr.split(",")))
    return card_id


def process_card(message_decoded):
    global last_card, is_empty, reading
    if reading:
        card = Card(calc_card_num(message_decoded[0]))
        last_card = card
        is_empty = False
        reading = False


def wait_for_card():
    """
    :rtype: Card
    """
    global last_card, reading, is_empty
    reading = True
    print("Input desired card or press '`' to return")
    while is_empty:
        if keyboard.is_pressed('`'):
            return None
    card = last_card
    last_card = None
    is_empty = True
    return card


def worker_report():
    print_workers()
    choice = input("Input employees ID: ")
    if choice.isdigit() and 9_999_999 >= int(choice) >= 1_000_000:
        exportWorkerReport(choice)
    else:
        print("Incorrect ID!")


def print_workers():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_database")
    emp = cursor.fetchall()
    w_arr = []
    for worker in emp:
        w_arr.append(Worker(worker[1], worker[2], worker[0], worker[3]))
    for w in w_arr:
        print(str(w))


def exportWorkerReport(workerNumber):
    worker = findWorker(workerNumber)
    if worker is None:
        print("No employee found")
        return
    file_name = worker.name + "_" + worker.surname + "_Report.csv"
    data = findEntries(worker)

    if len(data) > 1:
        if len(data) % 2 != 0:
            up = len(data) - 2
        else:
            up = len(data) - 1
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Enter_day", "CardId", "Enter_time", "Enter_terminal",
                             "Exit_time", "Exit_terminal", "Work_time"])
            for index in range(up, 0, -2):
                enter_data = data[index - 1]
                out_data = data[index]
                date = datetime.datetime.strptime(enter_data[0], '%Y-%m-%d %H:%M:%S').date()
                cardId = out_data[2]
                enter_time = datetime.datetime.strptime(enter_data[0], '%Y-%m-%d %H:%M:%S')
                enter_terminal = enter_data[1]
                exit_time = datetime.datetime.strptime(out_data[0], '%Y-%m-%d %H:%M:%S')
                exit_terminal = out_data[1]
                work_time = exit_time - enter_time
                enter_time = enter_time.strftime("%Y-%m-%d %H:%M:%S")
                exit_time = exit_time.strftime("%Y-%m-%d %H:%M:%S")
                output = date, cardId, enter_time, enter_terminal, exit_time, exit_terminal, work_time
                writer.writerow(output)
            print(f"{worker.name}_{worker.surname}_Report.csv exported!")
    else:
        print("No entries for this worker")


def findWorker(workerId):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_database")
    emp = cursor.fetchall()
    for worker in emp:
        if int(worker[0]) == int(workerId):
            worker_name = worker[1]
            worker_surname = worker[2]
            worker_id = int(worker[0])
            card_id = calc_card_num(worker[3])
            return Worker(worker_name, worker_surname, worker_id, card_id)
    return None


def findEntries(worker):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_log")
    ent_db = cursor.fetchall()
    w_entries = []
    for entry in ent_db:
        if entry[3] == str(worker.number):
            w_entries.append((entry[0], entry[1], entry[2], entry[3]))
    return w_entries


def update_workers_card(worker):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""Update workers_database set cardNumber = (?) where id = (?)""",
                   (str(worker.card), worker.number))
    connection.commit()
    connection.close()


def assign():
    print()
    card = wait_for_card()
    if card is None:
        print("Assignment broken")
        return
    print(f"Found card: {card}")
    if check_if_card_belongs(card):
        print("This card is already assigned!")
        return
    print_workers()
    workNum = input("Choose workers ID: ")
    if workNum.isdigit() and 9_999_999 >= int(workNum) > 999_999:
        worker = findWorker(int(workNum))
        if worker is not None and card is not None:
            worker.card = card.uid
            update_workers_card(worker)
            print("Card assigned " + str(worker))
        else:
            print("Employee not found!")
    else:
        print("Number incorrect!")


def check_if_card_belongs(card):
    work = get_workers_array()
    for worker in work:
        if worker.card == card.uid:
            return True
    return False


def get_workers_array():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_database")
    emp = cursor.fetchall()
    output = []
    for worker in emp:
        output.append(Worker(worker[1], worker[2], worker[0], calc_card_num(worker[3])))
    return output


def printArray(array):
    for index in range(len(array)):
        print(f"{index}. {array[index]}")


def get_cards_array():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cards_database")
    cards_db = cursor.fetchall()
    output = []
    for card in cards_db:
        output.append(Card(calc_card_num(card[0])))
    return output


def unassign():
    print("")
    print_workers()
    workNum = input("Choose workers ID whose card you want to unassign: ")
    if workNum.isdigit() and 9_999_999 >= int(workNum) > 999_999:
        worker = findWorker(int(workNum))
        if worker is not None:
            worker.card = 0
            update_workers_card(worker)
            print(f"Card unassigned {worker}")
        else:
            print("Number incorrect!")
    else:
        print("Number incorrect!")


def erase_entries():
    if os.path.exists("logs.db"):
        os.remove("logs.db")
        print("An old logs database removed.")


def add_card():
    global reading, is_empty, last_card
    # reading = True
    # print("Press desired card to the reader or 'b' to back: ")
    card = wait_for_card()
    print(f"Card found: {card}")
    if card in get_cards_array():
        print("Card already in database")
        return
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""
                    INSERT INTO cards_database
                    VALUES (?)
                    """,
                   (str(card),))
    connection.commit()
    connection.close()
    print("New card successfully added to database")


def add_worker_to_db(worker):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO workers_database
                    VALUES (?,?,?,?)""",
                   (worker.number, worker.name, worker.surname, worker.card))
    connection.commit()
    connection.close()


def add_worker():
    print("__Adding worker__")

    check = True
    while check:
        name = input("Input the name: ")
        surname = input("Input the surname: ")
        inp = 'O'
        while inp != 'N' and inp != 'Y':
            inp = input(f"Is data: {name} {surname} correct?[Y/N]")
            if inp == 'Y':
                check = False
                worker = Worker(name, surname)
                add_worker_to_db(worker)
                print(f"{worker} successfully added to database")
            elif inp == 'N':
                print("Data incorrect, input again...")
            else:
                print("Please insert (Y)es or (N)o")


def delete_card():
    print()
    cards = get_cards_array()
    printArray(cards)
    card_num = input(f"Please input desired card number [0-{len(cards) - 1}]:")
    if card_num.isdigit() and len(cards) > int(card_num) >= 0:
        connection = sql.connect(database_name)
        card = cards[int(card_num)]
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM cards_database
                        where id = (?)""",
                       (str(card.uid),))
        connection.commit()
        connection.close()
    else:
        print("Incorrect number, procedure stopped")


def run_card_management():
    # options mode
    print_card_management_options()
    while True:
        if keyboard.is_pressed('a'):
            time.sleep(0.3)
            print()
            assign()
            print_card_management_options()

        if keyboard.is_pressed('d'):
            time.sleep(0.3)
            print()
            unassign()
            print_card_management_options()

        if keyboard.is_pressed('+'):
            time.sleep(0.3)
            print()
            add_card()
            print_card_management_options()

        if keyboard.is_pressed('*'):
            time.sleep(0.3)
            print()
            delete_card()
            print_card_management_options()

        if keyboard.is_pressed('-'):
            time.sleep(0.3)
            print()
            add_worker()
            print_card_management_options()

        if keyboard.is_pressed('g'):
            time.sleep(0.3)
            print_workers()
            print_card_management_options()

        if keyboard.is_pressed(']'):
            time.sleep(0.3)
            break


def print_card_management_options():
    print()
    print("_______MANAGEMENT_______")
    print("a - Assign card")
    print("d - Unassign card")
    print("+ - approve new card")
    print("* - delete approved card")
    print("- - add new worker")
    print("] - back")


def mainLoop():
    print_mainLoop_options()
    while True:
        if keyboard.is_pressed('c'):
            time.sleep(0.2)
            run_card_management()
            print_mainLoop_options()
        if keyboard.is_pressed('d'):
            time.sleep(0.2)
            worker_report()
            print_mainLoop_options()
        if keyboard.is_pressed('esc'):
            break


def print_mainLoop_options():
    print("")
    print("_______MAIN MENU_______")
    print("c - Card/Worker management")
    print("d - Export workers report")
    print("esc - Exit")


def connect_to_broker():
    # Setting TLS
    client.tls_set("ca.crt")  # provide path to certification
    # Authenticate
    client.username_pw_set(username='officeserver', password='officeserverpassword')
    # Connect to the broker.
    client.connect(broker, port)  # modify connect call by adding port
    # Send message about conenction.
    client.on_message = process_message
    # Starts client and subscribe.
    client.loop_start()
    client.subscribe("office/#")


def disconnect_from_broker():
    # Disconnect the client.
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()
    print("connected")
    # create_main_window()
    mainLoop()
    # window.mainloop()
    disconnect_from_broker()


if __name__ == '__main__':
    run_receiver()
