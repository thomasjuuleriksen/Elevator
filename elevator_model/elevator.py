import time
import random

from direction.direction import Direction
from semaphore.semaphore import Semaphore

MAX_FLOOR = 30


class Elevator:
    def __init__(self, print_q, name, speed: float, current_floor: int = 0, next_floor: int = 0):
        self.q = print_q
        self.name = name
        self.direction = Direction.still
        self.speed = speed
        self.current_floor = current_floor
        self.next_floor = next_floor
        self.next_floor_reached = False
        self.queue_up = []
        self.queue_down = []
        self.floor_flag = Semaphore()
        self.queue_flag = Semaphore()

    def actuator(self):
        time.sleep(self.speed)
        return None

    def open_door(self):
        time.sleep(random.randint(1, 2))
        return None

    def elevator_movement(self):
        while True:
            self.floor_flag.wait()
            if self.next_floor > self.current_floor:
                self.current_floor += 1
                self.floor_flag.signal()
                self.actuator()
            elif self.next_floor < self.current_floor:
                self.current_floor -= 1
                self.floor_flag.signal()
                self.actuator()
            else:
                if self.direction != Direction.still:
                    self.next_floor_reached = True
                    self.floor_flag.signal()
                    self.q.put(f'Door {self.name} open at floor {self.current_floor}')
                    self.open_door()
                else:
                    self.floor_flag.signal()

    def floor_requested(self):    # Emulates floor requests made inside a specific elevator
        if random.randint(1,200000) % 131313 == 0:
            floor = random.randint(0, MAX_FLOOR)
        else:
            floor = -1
        return floor

    def floor_enq(self, floor):  # inserts a floor in queue_up or queue_down based on current floor and direction
        if not (floor in self.queue_up or floor in self.queue_down):
            self.queue_flag.wait()
            if (floor > self.current_floor) or \
                    ((floor == self.current_floor) and (self.direction == Direction.down)):
                # to be taken on the way up; add to queue_up
                self.queue_up.append(floor)
                self.queue_up.sort()
            elif (floor < self.current_floor) or \
                    ((floor == self.current_floor) and (self.direction == Direction.up)):
                # to be taken on the way down; add to queue_down
                self.queue_down.append(floor)
                self.queue_down.sort(reverse=True)
            else:
                pass  # Ignore request for current floor when elevator is standing still
            self.queue_flag.signal()
        else:
            pass  # Avoid duplicates in queues
        return None

    def floor_deq(self, direction, floor):
        self.queue_flag.wait()
        if direction == Direction.up:
            self.queue_up.remove(floor)
        else:
            self.queue_down.remove(floor)
        self.queue_flag.signal()
        return None

    def elevator_control(self):   # manages self.queue_up/_down and controls self.next_floor for the elevator
        while True:
            req_floor = self.floor_requested()   # check if a specific floor has been requested within the elevator
            if req_floor > 0:
                self.floor_enq(req_floor)
                self.q.put(f'{self.name} requested to floor {req_floor}, moving {self.direction}. '
                    f'UP queue: {self.queue_up}. DOWN queue: {self.queue_down}')
            self.floor_flag.wait()
            if self.next_floor_reached:    # dequeue the floor when reached
                self.floor_deq(self.direction, self.next_floor)
                self.next_floor_reached = False
            if self.direction in {Direction.up, Direction.still}:  # set next_floor
                if len(self.queue_up) > 0:
                    self.next_floor = self.queue_up[0]
                    self.direction = Direction.up
                elif len(self.queue_down) > 0:
                    self.next_floor = self.queue_down[0]
                    self.direction = Direction.down
                else:
                    self.direction = Direction.still
            else:           # direction is down
                if len(self.queue_down) > 0:
                    self.next_floor = self.queue_down[0]
                    self.direction = Direction.down
                elif len(self.queue_up) > 0:
                    self.next_floor = self.queue_up[0]
                    self.direction = Direction.up
                else:
                    self.direction = Direction.still
            self.floor_flag.signal()
