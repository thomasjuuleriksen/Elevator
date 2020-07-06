from direction.direction import Direction


def central_control(elevators, floor_q, print_q):    # dequeues from requested_queue and enqueues to a specific elevator's queue_up/_down
    while True:
        if not(floor_q.empty()):   # check for new requested floors and add them to floor queues
            floor = floor_q.get()
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
            print_q.put(f'Elevator requested from floor {floor} added to {target_elevator.name}, moving {target_elevator.direction}. '
                  f'UP queue: {target_elevator.queue_up}. DOWN queue: {target_elevator.queue_down}')
