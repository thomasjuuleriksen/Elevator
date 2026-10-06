import settings as s
import test_settings as t


def is_whole(x):    # True for 3, False for 3.0, 0.5 and True (bool counts as int in Python)
    return isinstance(x, int) and not isinstance(x, bool)


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_list(x):
    return isinstance(x, (list, tuple))


def check_range(name, value):    # (low, high) of whole seconds; random.randint rejects fractions
    if not (is_list(value) and len(value) == 2 and all(is_whole(v) for v in value)):
        return [f'{name} must be two whole numbers, e.g. (1, 2); got {value!r}']
    low, high = value
    if not 0 <= low <= high:
        return [f'{name} must satisfy 0 <= low <= high; got {value!r}']
    return []


def check_elevators():
    errors = []
    if not (is_whole(s.NUMBER_OF_ELEVATORS) and s.NUMBER_OF_ELEVATORS >= 1):
        errors.append(f'NUMBER_OF_ELEVATORS must be a whole number >= 1; got {s.NUMBER_OF_ELEVATORS!r}')
    names_ok = is_list(s.ELEVATOR_NAMES) and all(isinstance(n, str) and n for n in s.ELEVATOR_NAMES)
    if not names_ok:
        errors.append(f"ELEVATOR_NAMES must be a list of names, e.g. ['A', 'B']; got {s.ELEVATOR_NAMES!r}")
    else:
        duplicates = sorted({n for n in s.ELEVATOR_NAMES if s.ELEVATOR_NAMES.count(n) > 1})
        if duplicates:
            errors.append(f'ELEVATOR_NAMES must be unique; repeated: {duplicates}')
    speeds_ok = is_list(s.ELEVATOR_SPEEDS)
    if not speeds_ok:
        errors.append(f'ELEVATOR_SPEEDS must be a list of numbers, e.g. [0.5, 0.5]; got {s.ELEVATOR_SPEEDS!r}')
    else:
        bad_speeds = [v for v in s.ELEVATOR_SPEEDS if not (is_number(v) and v > 0)]
        if bad_speeds:
            errors.append(f'ELEVATOR_SPEEDS must all be numbers > 0; invalid: {bad_speeds}')
    if names_ok and speeds_ok and not (s.NUMBER_OF_ELEVATORS == len(s.ELEVATOR_NAMES) == len(s.ELEVATOR_SPEEDS)):
        errors.append(f'NUMBER_OF_ELEVATORS is {s.NUMBER_OF_ELEVATORS}, but there are {len(s.ELEVATOR_NAMES)} '
                      f'ELEVATOR_NAMES and {len(s.ELEVATOR_SPEEDS)} ELEVATOR_SPEEDS')
    return errors


def check_timing():
    errors = check_range('DOOR_OPEN_TIME', s.DOOR_OPEN_TIME)
    for name in ('POLL_INTERVAL_S', 'DRAIN_POLL_S'):
        value = getattr(s, name)
        if not (is_number(value) and value > 0):
            errors.append(f'{name} must be a number > 0; got {value!r}')
    for name in ('DRAIN_TIMEOUT_S', 'OUTPUT_FLUSH_S'):
        value = getattr(s, name)
        if not (is_number(value) and value >= 0):
            errors.append(f'{name} must be a number >= 0; got {value!r}')
    return errors


def check_requests():
    errors = check_range('FLOOR_REQUEST_OUTSIDE_INTERVAL', t.FLOOR_REQUEST_OUTSIDE_INTERVAL)
    if not (is_whole(t.FLOOR_REQUEST_INSIDE_PROBABILITY) and t.FLOOR_REQUEST_INSIDE_PROBABILITY >= 1):
        errors.append(f'FLOOR_REQUEST_INSIDE_PROBABILITY must be a whole number >= 1; '
                      f'got {t.FLOOR_REQUEST_INSIDE_PROBABILITY!r}')
    if not isinstance(t.FLOOR_LIST_OUTSIDE_SET, bool):
        errors.append(f'FLOOR_LIST_OUTSIDE_SET must be True or False; got {t.FLOOR_LIST_OUTSIDE_SET!r}')
    elif t.FLOOR_LIST_OUTSIDE_SET:
        if not is_list(t.FLOOR_LIST_OUTSIDE):
            errors.append(f'FLOOR_LIST_OUTSIDE must be a list of floors; got {t.FLOOR_LIST_OUTSIDE!r}')
        elif not t.FLOOR_LIST_OUTSIDE:
            errors.append('FLOOR_LIST_OUTSIDE is empty, but FLOOR_LIST_OUTSIDE_SET is True')
        elif is_whole(s.MAX_FLOOR):
            bad_floors = [f for f in t.FLOOR_LIST_OUTSIDE if not (is_whole(f) and 0 <= f <= s.MAX_FLOOR)]
            if bad_floors:
                errors.append(f'FLOOR_LIST_OUTSIDE must contain whole numbers 0..{s.MAX_FLOOR}; '
                              f'invalid: {bad_floors}')
    return errors


def check_settings():    # returns a list of problems; empty when all settings are valid
    errors = []
    if not (is_whole(s.MAX_FLOOR) and s.MAX_FLOOR >= 1):
        errors.append(f'MAX_FLOOR must be a whole number >= 1; got {s.MAX_FLOOR!r}')
    return errors + check_elevators() + check_timing() + check_requests()
