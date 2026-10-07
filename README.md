# Elevator

A multi-threaded simulation of a group of elevators. Passengers call elevators from
floors and press buttons inside them; a central controller decides which elevator
answers each call, and every elevator moves, stops and opens its doors on its own.

Only the Python standard library is used (developed and tested with Python 3.11).

## Running it

From the repository folder:

```
python app.py
```

By default the simulation runs **until you press Ctrl+C**, generating random floor
calls. To run a fixed sequence of calls instead, set `FLOOR_LIST_OUTSIDE_SET = True`
in `test_settings.py`; the program then exits by itself once every elevator has
finished.

Typical output:

```
Elevator requested from floor 16 added to A, moving Direction.still. UP queue: [16]. DOWN queue: []
A requested to floor 20, moving Direction.up. UP queue: [16, 20]. DOWN queue: []
Door A open at floor 16
```

Run it from the repository folder: the modules import each other relative to it.

## Settings

All values are checked when the program starts. If anything is invalid, it stops
with a message listing every problem.

**`settings.py`** — the building and its elevators

| Setting | Default | Meaning |
|---|---|---|
| `MAX_FLOOR` | `30` | Top floor; floors run from 0 to this value |
| `NUMBER_OF_ELEVATORS` | `3` | Must match the length of the two lists below |
| `ELEVATOR_NAMES` | `['A', 'B', 'C']` | One unique name per elevator |
| `ELEVATOR_SPEEDS` | `[0.5, 0.5, 0.5]` | Seconds per floor, one per elevator |
| `DOOR_OPEN_TIME` | `(1, 2)` | Door stays open a random whole number of seconds in this range |
| `POLL_INTERVAL_S` | `0.01` | How often each elevator's controller checks for work |
| `DRAIN_POLL_S` | `0.5` | Fixed-list mode: how often to check whether elevators are done |
| `DRAIN_TIMEOUT_S` | `120` | Fixed-list mode: stop waiting after this many seconds |
| `OUTPUT_FLUSH_S` | `2` | Time allowed for the last messages to be printed |

**`test_settings.py`** — how passengers behave

| Setting | Default | Meaning |
|---|---|---|
| `FLOOR_REQUEST_INSIDE_PROBABILITY` | `30000` | Each controller check has a 1-in-N chance of a button press inside the elevator (about one every 5 minutes per elevator) |
| `FLOOR_LIST_OUTSIDE_SET` | `False` | `True`: use the floors in `FLOOR_LIST_OUTSIDE` once, in order. `False`: random floors, endlessly |
| `FLOOR_LIST_OUTSIDE` | 30 floors | Calls from floors, used when the setting above is `True` |
| `FLOOR_REQUEST_OUTSIDE_INTERVAL` | `(5, 30)` | Seconds between calls from floors: a random whole number in this range |

## How it works

```
 request process ──calls──▶ central_control ──floor_enq──▶ Elevator A, B, C ...
 (separate process)          (thread)                        each with two threads:
                                                             elevator_control, elevator_movement
                         all output ──▶ print process (separate process)
```

- **Request process** simulates people calling an elevator from a floor and sends
  each call to `central_control`.
- **`central_control`** (`elevator_model/central_control.py`) gives each call to an
  elevator, preferring one already heading towards that floor, otherwise the
  nearest idle one.
- **Each `Elevator`** (`elevator_model/elevator.py`) keeps two sorted queues of
  stops: one for the way up, one for the way down.
  - `elevator_control` simulates buttons pressed inside the elevator, removes a stop
    once it is reached, and chooses the next stop. A stop the car has already
    passed is moved to the other queue and served on the way back.
  - `elevator_movement` moves the car one floor at a time and opens the door at
    each stop.
- **Print process** prints all messages, so output from different threads doesn't
  get mixed up.

Each elevator protects its state with two locks, `floor_flag` (position, direction,
next stop) and `queue_flag` (the queues). When both are needed, `floor_flag` is always
taken first, which prevents deadlocks.

## Project layout

| Path | Contents |
|---|---|
| `app.py` | Starts everything and handles shutdown |
| `settings.py`, `test_settings.py` | Settings (see above) |
| `settings_check.py` | Startup validation of all settings |
| `elevator_model/elevator.py` | The `Elevator` class |
| `elevator_model/central_control.py` | Assigns calls from floors to elevators |
| `direction/direction.py` | The `Direction` enum: `still`, `up`, `down` |

## Known limitations

- The simulation runs in real time, so long runs take real hours.
- The choice of elevator is simple and can favour the first elevator.
- If a thread crashes unexpectedly, that elevator stops silently while the rest
  carry on.

## Feedback

Please feel free to branch this off, use it (but please mention where it comes
from!), enhance it, and send constructive feedback.

Enjoy!
