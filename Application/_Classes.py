import random


class Card:
    uid = []

    def __init__(self, identificator=None):
        if identificator is None:
            self.uid = [random.randint(1, 500) for _ in range(5)]
        else:
            self.uid = identificator

    def getStrId(self):
        tab = str(self.uid)
        num = 0
        for i in range(0, len(self.uid)):
            num += self.uid[i] << (i * 8)
        return tab, num

    def getCardId(self):
        num = 0
        for i in range(0, len(self.uid)):
            num += self.uid[i] << (i * 8)
        return num

    def __str__(self):
        # tup = self.getStrId()
        return str(self.uid)

    def __repr__(self):
        return str(self.uid)

    def __eq__(self, other):
        if other is not None:
            if type(other) == type(self):
                return self.uid == other.uid
            else:
                return False
        else:
            return False


class Worker:
    number = 0
    name = ""
    surname = ""
    card = 0

    def __init__(self, name, surname, number=0, cardNumber=0):
        self.name = name
        self.surname = surname
        if number == 0:
            self.createNumber()
        else:
            self.number = number
        self.card = cardNumber

    def assign_card(self, newCard):
        self.card = newCard

    def __str__(self):
        if self.card != 0:
            return f"{self.number}, {self.name} {self.surname}, card: {str(self.card)}"
        else:
            return f"{self.number}, {self.name} {self.surname}, card: {None}"

    def __repr__(self):
        # if self.card is not None:
        #     return self.name + " " + self.surname
        # else:
        return str(self.number) + ", " + self.name + " " + self.surname

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, Worker):
            return self.name == other.name and self.surname == other.surname and self.number == other.number

    def createNumber(self):
        self.number = random.randint(1_000_000, 9_999_999)
