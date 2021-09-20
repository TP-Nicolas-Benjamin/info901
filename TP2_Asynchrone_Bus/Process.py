from time import sleep

from pyeventbus3.pyeventbus3 import *

from BroadcastMessage import BroadcastMessage
# from EventBus import EventBus
from Message import Message
from Synchronisation import Synchronisation
from Token import Token

# from geeteventbus.subscriber import subscriber
# from geeteventbus.eventbus import eventbus
# from geeteventbus.event import event

BROADCAST = "BROADCAST"
size = 3


class Process(Thread):
    cptSynchronize = size - 1

    def __init__(self, name, cpt, state):
        Thread.__init__(self)

        self.setName(name)

        PyBus.Instance().register(self, self)

        self.compteur = cpt
        self.alive = True
        self.state = None
        self.start()

    def get_name(self):
        return int(self.getName())

    ############################   LAMPORT + BROADCAST   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def on_broadcast(self, event):
        if event.src != self.get_name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_name()} received broadcasted message {event.msg}")

    def broadcast(self, message):
        self.compteur += 1
        PyBus.Instance().post(BroadcastMessage(message.cpt + 1, message.msg, message.src))

    ############################   LAMPORT + DEDICATED   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def on_receive(self, event):
        if event.dest == self.get_name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_name()} received message {event.msg}")

    def send_to(self, obj):
        self.compteur += 1
        PyBus.Instance().post(obj)

    ############################   TOKEN   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        if self.get_name() == event.dest and self.alive:
            sleep(1)
            print(f"found token in {self.getName()}")
            if self.state == "request":
                print("i'm on request going on SC")
                self.state = "SC"
                while self.state != "release":
                    sleep(1)
            self.send_to(Token(event.id, (event.dest + 1) % 3))
            print(f"token sent to next which is {(self.get_name() + 1) % 3}")
            self.state = None

    def request(self):
        self.state = "request"
        while self.state != "SC":
            sleep(1)

    def release(self):
        self.state = "release"

    ############################   SYNCHRONIZE   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Synchronisation)
    def onSynchronize(self, event):
        if event.src != self.get_name():
            self.cptSynchronize -= 1

    def synchronize(self):
        PyBus.Instance().post(Synchronisation(self.get_name()))
        while self.cptSynchronize > 0:
            sleep(1)

    ############################   RUN   ############################
    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            # print(f"{self.get_Name()} cpt : {self.compteur}")
            sleep(1)

            # # Creating token
            # if self.get_Name() == 0 and loop == 0:
            #     t = Token("abcdefghijklmnopqrstuvwxyz", 1)
            #     print("created token : " + str(t))
            #     self.sendTo(t)

            # if self.get_Name() == 1:
            # b1 = Message(self.compteur, f"Message  {loop}", 2)
            # self.sendTo(b1, 2)
            # self.sendTo(b1, 3)
            # self.broadcast(BroadcastMessage(self.compteur, f"Broadcasted message  {loop}", 1))

            # Requesting token
            # if loop == 2:
            #     if self.get_Name() == 1:
            #         self.request()
            #         print("token SC")
            #         sleep(2)
            #         print("releasing the beast !")
            #         self.release()

            if self.get_name() == 1 and loop == 0:
                sleep(5)
            elif self.get_name() == 2 and loop == 0:
                sleep(10)
            if loop == 6:
                self.synchronize()

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()
