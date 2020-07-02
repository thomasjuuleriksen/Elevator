def central_control(elevators):
    while True:
        if not(requested_queue.empty()):   # check for new requested floors and add them to floor queues
            floor = requested_queue.get()
            requested_queue.task_done()
            target_elevator = elevators[0]
            for e in elevators:
                if (e.direction in {Direction.up, Direction.still}) and (floor > e.current_floor):
                    if (target_elevator.current_floor < e.current_floor) or (target_elevator.current_floor >= floor):
                        target_elevator = e
                elif (e.direction in {Direction.down, Direction.still}) and (floor < e.current_floor):
                    if (target_elevator.current_floor > e.current_floor) or (target_elevator.current_floor <= floor):
                        target_elevator = e
            target_elevator.floor_enq(floor)
            print(f'Floor {floor} added to {target_elevator.name}')
