import sys
import time
import random
from threading import Thread
from multiprocessing import Process, SimpleQueue

from direction.direction import Direction
from elevator_model.elevator import Elevator
from elevator_model import central_control
from settings import (MAX_FLOOR, NUMBER_OF_ELEVATORS, ELEVATOR_NAMES, ELEVATOR_SPEEDS,
                      DOOR_OPEN_TIME, POLL_INTERVAL_S, DRAIN_POLL_S, DRAIN_TIMEOUT_S, OUTPUT_FLUSH_S)
from test_settings import (FLOOR_REQUEST_INSIDE_PROBABILITY, FLOOR_LIST_OUTSIDE_SET, FLOOR_LIST_OUTSIDE,
                           FLOOR_REQUEST_OUTSIDE_INTERVAL)


def is_whole(x):    # True for 3, False for 3.0, 0.5 and True (bool counts as int in Python)
    return isinstance(x, int) and not isinstance(x, bool)


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def check_range(name, value):    # (low, high) of whole seconds; random.randint rejects fractions
    if not (isinstance(value, (tuple, list)) and len(value) == 2 and all(is_whole(v) for v in value)):
        return [f'{name} must be two whole numbers, e.g. (1, 2); got {value!r}']
    low, high = value
    if not 0 <= low <= high:
        return [f'{name} must satisfy 0 <= low <= high; got {value!r}']
    return []


def check_settings():
    errors = []
    if not (is_whole(MAX_FLOOR) and MAX_FLOOR >= 1):
        errors.append(f'MAX_FLOOR must be a whole number >= 1; got {MAX_FLOOR!r}')
    if not (is_whole(NUMBER_OF_ELEVATORS) and NUMBER_OF_ELEVATORS >= 1):
        errors.append(f'NUMBER_OF_ELEVATORS must be a whole number >= 1; got {NUMBER_OF_ELEVATORS!r}')
    if not (NUMBER_OF_ELEVATORS == len(ELEVATOR_NAMES) == len(ELEVATOR_SPEEDS)):
        errors.append(f'NUMBER_OF_ELEVATORS is {NUMBER_OF_ELEVATORS}, but there are {len(ELEVATOR_NAMES)} '
                      f'ELEVATOR_NAMES and {len(ELEVATOR_SPEEDS)} ELEVATOR_SPEEDS')
    duplicates = sorted({n for n in ELEVATOR_NAMES if ELEVATOR_NAMES.count(n) > 1})
    if duplicates:
        errors.append(f'ELEVATOR_NAMES must be unique; repeated: {duplicates}')
    bad_speeds = [s for s in ELEVATOR_SPEEDS if not (is_number(s) and s > 0)]
    if bad_speeds:
        errors.append(f'ELEVATOR_SPEEDS must all be numbers > 0; invalid: {bad_speeds}')
    errors += check_range('DOOR_OPEN_TIME', DOOR_OPEN_TIME)
    errors += check_range('FLOOR_REQUEST_OUTSIDE_INTERVAL', FLOOR_REQUEST_OUTSIDE_INTERVAL)
    if not (is_whole(FLOOR_REQUEST_INSIDE_PROBABILITY) and FLOOR_REQUEST_INSIDE_PROBABILITY >= 1):
        errors.append(f'FLOOR_REQUEST_INSIDE_PROBABILITY must be a whole number >= 1; '
                      f'got {FLOOR_REQUEST_INSIDE_PROBABILITY!r}')
    for name, value in (('POLL_INTERVAL_S', POLL_INTERVAL_S), ('DRAIN_POLL_S', DRAIN_POLL_S)):
        if not (is_number(value) and value > 0):
            errors.append(f'{name} must be a number > 0; got {value!r}')
    for name, value in (('DRAIN_TIMEOUT_S', DRAIN_TIMEOUT_S), ('OUTPUT_FLUSH_S', OUTPUT_FLUSH_S)):
        if not (is_number(value) and value >= 0):
            errors.append(f'{name} must be a number >= 0; got {value!r}')
    if FLOOR_LIST_OUTSIDE_SET and is_whole(MAX_FLOOR):
        bad_floors = [f for f in FLOOR_LIST_OUTSIDE if not (is_whole(f) and 0 <= f <= MAX_FLOOR)]
        if bad_floors:
            errors.append(f'FLOOR_LIST_OUTSIDE must contain whole numbers 0..{MAX_FLOOR}; invalid: {bad_floors}')
    return errors


def random_floors():
    while True:
        yield random.randint(0, MAX_FLOOR)


def elevator_request_process(q):    # emulates calls for an elevator from specific floors; enqueues to requested_q
    floors = FLOOR_LIST_OUTSIDE if FLOOR_LIST_OUTSIDE_SET else random_floors()
    try:
        for f in floors:
            time.sleep(random.randint(*FLOOR_REQUEST_OUTSIDE_INTERVAL))
            q.put(f)
    except KeyboardInterrupt:
        pass    # Ctrl+C: exit quietly, main handles shutdown


def print_process(q):
    try:
        while True:
            print(q.get())
    except KeyboardInterrupt:
        pass


def wait_for_elevators(elevators):
    deadline = time.monotonic() + DRAIN_TIMEOUT_S
    while True:
        time.sleep(DRAIN_POLL_S)    # first sleep also lets central_control hand over the last request
        if not any(e.queue_up or e.queue_down or e.direction != Direction.still for e in elevators):
            return
        if time.monotonic() > deadline:
            print(f'Warning: elevators still busy after {DRAIN_TIMEOUT_S} s; shutting down anyway', file=sys.stderr)
            return


if __name__ == '__main__':
    errors = check_settings()
    if errors:
        sys.exit('Settings error:\n' + '\n'.join(errors))

    # spawn a separate printing process, 'print_p',  with 'print_q' as the shared buffer
    print_q = SimpleQueue()
    print_p = Process(target=print_process, args=(print_q,))
    print_p.start()

    # spawn a separate elevator_request_process with requested_q as shared buffer
    requested_q = SimpleQueue()
    elevator_request_p = Process(target=elevator_request_process, args=(requested_q,))
    elevator_request_p.start()

    elevators = [Elevator(print_q, name, speed) for name, speed in zip(ELEVATOR_NAMES, ELEVATOR_SPEEDS)]
    # spawn a central elevator control thread
    threads = [Thread(target=central_control.central_control, args=[elevators, requested_q, print_q], daemon=True)]
    for e in elevators:
        threads.append(Thread(target=e.elevator_movement, daemon=True))
        threads.append(Thread(target=e.elevator_control, daemon=True))
    for t in threads:
        t.start()

    try:
        while elevator_request_p.is_alive():    # list mode: ends after the last request; endless: until Ctrl+C
            elevator_request_p.join(0.5)        # short timeout so Ctrl+C is noticed on Windows
        wait_for_elevators(elevators)
        time.sleep(OUTPUT_FLUSH_S)
    except KeyboardInterrupt:
        print('Stopped by user')
    finally:
        elevator_request_p.terminate()
        print_p.terminate()
        elevator_request_p.join()
        print_p.join()
