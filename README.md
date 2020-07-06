# Elevator
This is a simple model of an elevator. Run 'app.py' for a demo.
It features - in principle - scores of concurrent elevators being controlled partly by their own controller, which handles requests from within the elevator,
and partly by a central control, which handles requests from a specific floor for an elevator.

In the module 'elevator_model', the 'Elevator' class is defined.
An 'Elevator' object has two central methods, 'elevator_movement' and 'elevator_control' as well as three key auxillary methods, 'floor_enq', 'floor_deq', 'floor_requested':
  - 'elevator_movement', which reads 'next_floor' and 'direction' properties, controls 'current_floor' property
    and sets 'next_floor_reached' property to True when 'next_floor' is reached. It uses 'actuator' and 'open_door' methods to mimic physical elevator actions.
  - 'elevator_control', which uses methods 'floor_enq' and 'floor_deq' to enqueue floors requested from within the elevator and dequeue a floor when it is reached by the elevator.
    It checks floors have been requested from within the elevator using the 'floor_requested' method. It controls 'next_floor' and 'direction' properties
  - 'floor_enq' enqueues a specific floor to either 'queue_up' or 'queue_down, depending on 'current_floor' and 'direction' properties. It ignores duplicates.
    It keeps 'queue_up' sorted in ascending order and 'queue_down' in desceding order. It uses a Semaphore object 'queue_flag', to ensure exclusivity on 'queue_up'/'queue_down'.
  - 'floor_deq' dequeues a floor from 'queue_up'/'queue_down, respectively, depending on 'direction' property. It uses 'queue_flag' semaphore, to ensure exclusivity
    on 'queue_up'/'queue_down'.
  - 'floor_requested' method mimics the request for a specific floor from within the elevator.
Methods 'elevator_movement' and 'elevator_control' are running as two concurrent threads per elevator

In the module 'central_control', the 'central_control' function monitors and when relevant dequeues from 'requested_q' when an elevator has been called from any specific floor.
It enqueues the floor to the elevator closest by AND moving in the appropriate direction using 'floor_enq' method of the appropriate elevator.
'central_control' function runs as a single thread in concurrence with the elevator threads.

In 'app', the 'elevator_request_process' runs as a separate process and mimics a fixed set (a rather näive way of mimicking requests for elevators from various floors).
It enqueues to 'requested_q', which is shared with the 'elevator_control' thread of each elevator. 'requested_q' is based on SimpleQueue of multiprocessing module and is supposed
to be thread and process safe. Hence no explicit sempahores around this.

Also in 'app', the 'print_process' takes care of all printing to the screen based on dequeuing from 'print_q' (also based on SimpleQueue of multiprocessing module).

Please feel free to branch this off, use it (but please mention where it comes from!), enhance it, send me constructive feedback etc.

Enjoy!
