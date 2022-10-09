#!/usr/bin/env python

import atpbar
from atpbar import flush
import threading
import random
import time
import os

def task(n, name):
    for i in atpbar.atpbar(range(n), name=name):
        time.sleep(0.1)

def run_with_threading():
    nthreads = 5
    threads = [ ]
    for i in range(nthreads):
        name = 'thread {}'.format(i)
        n = random.randint(5, 100)
        t = threading.Thread(target=task, args=(n, name))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    flush()

run_with_threading()
