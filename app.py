import time
import random
import queue
from threading import Thread

from direction.direction import Direction
from elevator_model.elevator import Elevator

requested_queue = queue.Queue()


def elevator_requested():    # emulates a call for an elevator from a specific floor; enqueues to requested_queue
    floors = [1,3,5,7,9,20,4,16,1,18,13,2,9,10,1,0,13,9,4,7,15,10,0,2,6,5,25,12,8,4]
    for f in floors:
        time.sleep(random.randint(4,5))
        time.sleep(1.5)
        requested_queue.put(f)


def central_control(elevators):    # dequeues from requested_queue and enqueues to a specific elevator's queue_up/_down
    while True:
        if not(requested_queue.empty()):   # check for new requested floors and add them to floor queues
            floor = requested_queue.get()
            requested_queue.task_done()
            target_elevator = elevators[0]
            for e in elevators:
                if (e.direction == Direction.up) and (floor > e.current_floor):
                    if (target_elevator.current_floor < e.current_floor) or (target_elevator.current_floor >= floor):
                        target_elevator = e
                elif (e.direction == Direction.down) and (floor < e.current_floor):
                    if (target_elevator.current_floor > e.current_floor) or (target_elevator.current_floor <= floor):
                        target_elevator = e
                elif e.direction == Direction.still:
                    if (target_elevator.current_floor > floor) and (target_elevator.direction == Direction.up):
                        target_elevator = e
                    elif (target_elevator.current_floor < floor) and (target_elevator.direction == Direction.down):
                        target_elevator = e
                    elif abs(target_elevator.current_floor - floor) > abs(e.current_floor - floor):
                        target_elevator = e
            target_elevator.floor_enq(floor)
            print(f'Requested from floor {floor} added to {target_elevator.name}, direction: {target_elevator.direction}. '
                  f'UP: {target_elevator.queue_up}. DOWN: {target_elevator.queue_down}')


elevators = [Elevator("A", 0.5), Elevator("B", 0.5), Elevator("C", 0.5)]
threads = [Thread(target=elevator_requested, daemon=True),
           Thread(target=central_control, args=[elevators], daemon=True)]
for e in elevators:
    threads.append(Thread(target=e.elevator_movement, daemon=True))
    threads.append(Thread(target=e.elevator_control, daemon=True))

for t in threads:
    t.start()

for t in threads:
    t.join()

requested_queue.join()
