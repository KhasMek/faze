#!/usr/bin/env python3
from threading import Thread


class FazeWorker(Thread):
    """
    Generic Threading class for Faze.
    """
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            cmd = self.queue.get()
            cmd()
            self.queue.task_done()