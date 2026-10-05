import time
import random
from threading import Thread
from multiprocessing import Process, SimpleQueue

from elevator_model.elevator import Elevator
from elevator_model import central_control
from elevator_model.state_logger import StateLogger

DURATION_S = 20 * 3600      # 20 hours
MEAN_INTERVAL_S = 60        # average seconds between external floor requests
LOG_FILE = 'elevator_log.csv'
MAX_FLOOR = 30


def elevator_request_process(q, duration_s, mean_interval_s):
    import time
    import random
    start = time.monotonic()
    while time.monotonic() - start < duration_s:
        interval = random.expovariate(1 / mean_interval_s)
        time.sleep(interval)
        if time.monotonic() - start < duration_s:
            q.put(random.randint(0, MAX_FLOOR))


def print_process(q):
    while True:
        print(q.get())


if __name__ == '__main__':
    print(f'Starting {DURATION_S // 3600}-hour run. Logging to {LOG_FILE}')
    logger = StateLogger(LOG_FILE)

    print_q = SimpleQueue()
    print_p = Process(target=print_process, args=(print_q,))
    print_p.start()

    requested_q = SimpleQueue()
    elevator_request_p = Process(
        target=elevator_request_process,
        args=(requested_q, DURATION_S, MEAN_INTERVAL_S),
    )
    elevator_request_p.start()

    elevators = [
        Elevator(print_q, 'A', 0.5, logger=logger),
        Elevator(print_q, 'B', 0.5, logger=logger),
        Elevator(print_q, 'C', 0.5, logger=logger),
    ]

    threads = [
        Thread(target=central_control.central_control,
               args=[elevators, requested_q, print_q, logger],
               daemon=True)
    ]
    for e in elevators:
        threads.append(Thread(target=e.elevator_movement, daemon=True))
        threads.append(Thread(target=e.elevator_control, daemon=True))
    for t in threads:
        t.start()

    elevator_request_p.join()   # wait until all requests have been issued

    # drain: wait for all elevator queues to empty before closing the log
    while any(e.queue_up or e.queue_down for e in elevators):
        time.sleep(0.5)
    time.sleep(3)               # allow last door to close and output to flush

    logger.close()
    print(f'Log written to {LOG_FILE}')
    print_p.terminate()
    print_p.join()
