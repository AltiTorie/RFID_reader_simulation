"""
SYMULACJA SERWERA

"""
import datetime
import sqlite3 as sql
import keyboard
import paho.mqtt.client as mqtt
from _Classes import Worker, Card
import _conf

# The broker name or IP address.
broker = _conf.broker  # change broker name to hostname provided
# in certificate configuration, please refer to section OpenSSL-step 4

# TLS port
port = _conf.port  # set up new port for TLS
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()

used_database = "system.db"


def findWorker(workerId):
    connection = sql.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_database")
    emp = cursor.fetchall()
    for worker in emp:
        if int(worker[0]) == workerId:
            worker_name = worker[1]
            worker_surname = worker[2]
            worker_id = int(worker[0])
            card_id = calc_card_num(worker[3])
            return Worker(worker_name, worker_surname, worker_id, card_id)
    return None


def findEntries(worker):
    connection = sql.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_log")
    ent_db = cursor.fetchall()
    w_entries = []
    for entry in ent_db:
        if entry[3] == worker.number:
            w_entries.append((entry[0], entry[1], entry[2], entry[3]))
    return w_entries


def get_cards_array():
    connection = sql.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cards_database")
    cards_db = cursor.fetchall()
    output = []
    for card in cards_db:
        output.append(Card(calc_card_num(card[0])))
    return output


def get_workers_array():
    connection = sql.connect(used_database)
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


def print_workers():
    connection = sql.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workers_database")
    emp = cursor.fetchall()
    w_arr = []
    for worker in emp:
        w_arr.append(Worker(worker[1], worker[2], worker[0], worker[3]))
    for w in w_arr:
        print(str(w))


def calc_card_num(card_str):
    if card_str == 0 or card_str == "0":
        return 0
    card_arr = card_str[1:len(card_str) - 1]
    card_id = list(map(int, card_arr.split(",")))
    return card_id


def process_message(cl, usr_dt, message):
    # Decode message.
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    # Print message to console.
    if message.topic == "terminal/card/id":
        process_card_id(message_decoded)


def process_card_id(message_decoded):
    if message_decoded[0] != "Client connected" and message_decoded[0] != "Client disconnected":
        card = Card(calc_card_num(message_decoded[0]))
        if card in get_cards_array():
            workersID = findAssignedWorkersID(card)
            terminal = str(message_decoded[1])
            use_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{use_time}, {card} was used by {workersID} at {terminal}")
            # Save to sqlite database.
            connection = sql.connect(used_database)
            cursor = connection.cursor()
            cursor.execute('''INSERT INTO workers_log VALUES (?,?,?,?)''',
                            (use_time, terminal, str(card.uid), workersID))
            connection.commit()
            connection.close()
        else:
            print("Card not approved! This incident will be registered!")
            register_unrecognized_card(message_decoded)
    else:
        print(message_decoded[0] + " : " + message_decoded[1])


def register_unrecognized_card(message):
    card = Card(calc_card_num(message[0]))
    terminal = message[1]
    use_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{use_time}, unknown card: {card} was used at {terminal}")
    connection = sql.connect(used_database)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO unrecognized_table VALUES (?,?,?)",
                   (str(card.uid), use_time, terminal))
    connection.commit()
    connection.close()


def findAssignedWorkersID(card):
    workers = get_workers_array()
    for worker in workers:
        if worker.card == card.uid:
            return worker.number
    return None


def connect_to_broker():
    # Setting TLS
    client.tls_set("ca.crt")  # provide path to certification
    # Authenticate
    client.username_pw_set(username='server', password='password')
    # Connect to the broker.
    client.connect(broker, port)  # modify connect call by adding port
    # Send message about connection.
    client.on_message = process_message
    # Starts client and subscribe.
    client.loop_start()
    client.subscribe("terminal/card/id")


def disconnect_from_broker():
    # Disconnect the client.
    client.loop_stop()
    client.disconnect()


def mainLoop():
    while True:
        if keyboard.is_pressed('esc'):
            break


def run_receiver():
    connect_to_broker()
    print("Receiver connected")
    # create_main_window()
    mainLoop()
    # window.mainloop()
    disconnect_from_broker()


if __name__ == '__main__':
    run_receiver()
