import time
import keyboard
import paho.mqtt.client as mqtt
import _setup
from _Classes import Card
import _conf

# The terminal ID - can be any string.
terminal_id = "Office_reader"
# The broker name or IP address.
# The broker name or IP address.
broker = _conf.broker  # change broker name to hostname provided
# in certificate configuration, please refer to section OpenSSL-step 4

# TLS port
port = _conf.port  # set up new port for TLS
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client("Office_reader")


def send_info(info):
    client.publish("office/info", f"{info}.{terminal_id}")


def scan_card(card):
    print("Scan new card...")
    client.publish("office/card/id", f"{card}.{terminal_id}")


def connect_to_broker():
    # Setting TLS
    client.tls_set("ca.crt")  # provide path to certification
    # Authenticate
    client.username_pw_set(username='officeclient', password='officeclientpassword')
    # Connect to the broker.
    client.connect(broker, port)
    # Send message about conenction.
    send_info("Client connected")


def disconnect_from_broker():
    # Send message about disconenction.
    scan_card("Client disconnected")
    # Disconnet the client.
    client.disconnect()


def run_sender():
    connect_to_broker()
    mainLoop()
    disconnect_from_broker()


def print_menu():
    print("__MENU__")
    print("b - card 0")
    print("n - card 1")
    print("m - card 7")
    print(", - new card")


def mainLoop():
    cards = _setup.load_cards()
    print_menu()
    while True:
        if keyboard.is_pressed('b'):
            time.sleep(0.3)
            scan_card(cards[0])
        if keyboard.is_pressed('n'):
            time.sleep(0.3)
            scan_card(cards[1])
        if keyboard.is_pressed('m'):
            time.sleep(0.3)
            scan_card(cards[7])
        if keyboard.is_pressed(','):
            time.sleep(0.3)
            scan_card(Card())


if __name__ == '__main__':
    run_sender()
