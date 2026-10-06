MAX_FLOOR = 30

# elevators
NUMBER_OF_ELEVATORS = 3            # must match the length of ELEVATOR_NAMES and ELEVATOR_SPEEDS
ELEVATOR_NAMES = ['A', 'B', 'C']
ELEVATOR_SPEEDS = [0.5, 0.5, 0.5]  # seconds per floor, one per elevator

# timing (seconds)
DOOR_OPEN_TIME = (1, 2)            # door stays open a random whole number of seconds in this range
POLL_INTERVAL_S = 0.01             # elevator_control loop, and elevator_movement while idle
DRAIN_POLL_S = 0.5                 # list mode: how often to check whether elevators are done
DRAIN_TIMEOUT_S = 120              # list mode: give up waiting after this long
OUTPUT_FLUSH_S = 2                 # time for the print process to write its last messages
