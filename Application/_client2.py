"""
SYMULACJA terminala 2
"""
import time
from threading import Timer

import keyboard
import paho.mqtt.client as mqtt

import _conf
import _setup

# The terminal ID - can be any string.
terminal_id = "T1"
# The broker name or IP address.
broker = _conf.broker  # change broker name to hostname provided
# in certificate configuration, please refer to section OpenSSL-step 4

# TLS port
port = _conf.port  # set up new port for TLS
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client("T1")
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


def connect_to_broker():
    # Setting TLS
    client.tls_set("ca.crt")  # provide path to certification
    # Authenticate
    client.username_pw_set(username='client2', password='client2password')
    # Connect to the broker.
    client.connect(broker, port)
    # Send message about conenction.
    send_info("Client connected")


def unlockCard(card):
    locked_cards.remove(card)
    print(f"{card} unlocked")


def disconnect_from_broker():
    # Send message about disconenction.
    press_card("Client disconnected")
    # Disconnet the client.
    client.disconnect()


def run_sender():
    connect_to_broker()
    mainLoop()
    disconnect_from_broker()


def mainLoop():
    while True:  # making a loop
        # run mode
        if keyboard.is_pressed('r'):
            press_card(cards[3])
            time.sleep(0.3)

        if keyboard.is_pressed('t'):
            press_card(cards[4])
            time.sleep(0.3)

        if keyboard.is_pressed('y'):
            press_card(cards[5])
            time.sleep(0.3)

        if keyboard.is_pressed('esc'):
            break


if __name__ == '__main__':
    cards = _setup.load_cards()
    run_sender()
