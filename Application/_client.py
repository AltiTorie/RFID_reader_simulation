"""
SYMULACJA PRZYLOZENIA KARTY
"""
import time
from threading import Timer

import keyboard
import paho.mqtt.client as mqtt

import _setup
from _Classes import Card
import _conf
# The terminal ID - can be any string.
terminal_id = "T0"
# The broker name or IP address.
broker = _conf.broker  # change broker name to hostname provided
# in certificate configuration, please refer to section OpenSSL-step 4

# TLS port
port = _conf.port  # set up new port for TLS
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client("T0")

locked_cards = []


def send_info(msg):
    print(f"Sent {msg}.{terminal_id}")
    client.publish("terminal/card/id", f"{msg}.{terminal_id}", )


def press_card(card_info):
    if card_info not in locked_cards:
        print(f"Sent {card_info}.{terminal_id}")
        client.publish("terminal/card/id", f"{card_info}.{terminal_id}", )
        locked_cards.append(card_info)
        t = Timer(5, unlockCard, [card_info])
        t.start()


def unlockCard(card):
    locked_cards.remove(card)
    print(f"{card} unlocked")


def connect_to_broker():
    # Setting TLS
    client.tls_set("ca.crt")  # provide path to certification
    # Authenticate
    client.username_pw_set(username='client1', password='client1password')
    # Connect to the broker.
    client.connect(broker, port)
    # Send message about conenction.
    send_info("Client connected")
    print("connected")


def disconnect_from_broker():
    # Send message about disconenction.
    send_info("Client disconnected")
    # Disconnet the client.
    client.disconnect()


def run_sender():
    connect_to_broker()
    mainLoop()
    disconnect_from_broker()


def mainLoop():
    while True:  # making a loop
        # run mode
        if keyboard.is_pressed('q'):
            press_card(cards[0])
            time.sleep(0.3)

        if keyboard.is_pressed('w'):
            press_card(cards[1])
            time.sleep(0.3)

        if keyboard.is_pressed('e'):
            press_card(cards[2])
            time.sleep(0.3)

        if keyboard.is_pressed('p'):
            press_card(Card())
            time.sleep(0.3)

        if keyboard.is_pressed('esc'):
            break


if __name__ == '__main__':
    cards = _setup.load_cards()
    run_sender()
