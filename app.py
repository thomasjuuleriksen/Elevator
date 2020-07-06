import time
import random
from threading import Thread
from multiprocessing import Process, SimpleQueue

from elevator_model.elevator import Elevator
from elevator_model import central_control


def elevator_request_process(q):    # emulates a call for an elevator from a specific floor; enqueues to requested_queue
    floors = [1,3,5,7,9,20,4,16,1,18,13,2,9,10,1,0,13,9,4,7,15,10,0,2,6,5,25,12,8,4]
    for f in floors:
        time.sleep(random.randint(5,30))
        time.sleep(1.5)
        q.put(f)


def print_process(q):
    while True:
        if not q.empty():
            print(q.get())


if __name__ == '__main__':
    # spawn a separate printing process, 'print_p',  with 'print_q' as the shared buffer
    print_q = SimpleQueue()
    print_p = Process(target=print_process, args=(print_q,))
    print_p.start()

    # spawn a separate elevator_request_process with requested_q as shared buffer
    requested_q = SimpleQueue()
    elevator_request_p = Process(target=elevator_request_process, args=(requested_q,))
    elevator_request_p.start()

    # create the desired number of Elevator objects
    elevators = [Elevator(print_q, "A", 0.5), Elevator(print_q, "B", 0.5), Elevator(print_q, "C", 0.5)]
    # spawn a central elevator control thread
    threads = [Thread(target=central_control.central_control, args=[elevators, requested_q, print_q], daemon=True)]
    for e in elevators:
        threads.append(Thread(target=e.elevator_movement, daemon=True))
        threads.append(Thread(target=e.elevator_control, daemon=True))
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    requested_q.join()
    print_p.join()
    elevator_request_p.join()

