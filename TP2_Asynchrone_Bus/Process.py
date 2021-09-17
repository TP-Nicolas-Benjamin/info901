from time import sleep

from pyeventbus3.pyeventbus3 import *

from BroadcastMessage import BroadcastMessage
# from EventBus import EventBus
from Message import Message

# from geeteventbus.subscriber import subscriber
# from geeteventbus.eventbus import eventbus
# from geeteventbus.event import event

BROADCAST = "BROADCAST"


class Process(Thread):

    def __init__(self, name, cpt):
        Thread.__init__(self)

        self.setName(name)

        PyBus.Instance().register(self, self)

        self.compteur = cpt
        self.alive = True
        self.start()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def receive(self, event):
        if event.dest == self.getName():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.getName()} received message {event.msg}")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if event.src != self.getName():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.getName()} received broadcasted message {event.msg}")

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            print(f"{self.getName()} cpt : {self.compteur}")
            sleep(1)

            if self.getName() == "P1":
                # b1 = Message(self.compteur, f"Message  {loop}", "P2")
                # self.publish(b1)
                self.broadcast(BroadcastMessage(self.compteur, f"Broadcasted message  {loop}", "P1"))

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def publish(self, message):
        self.compteur += 1
        PyBus.Instance().post(Message(message.cpt + 1, message.msg, message.dest))

    def broadcast(self, message):
        self.compteur += 1
        PyBus.Instance().post(BroadcastMessage(message.cpt + 1, message.msg, message.src))
