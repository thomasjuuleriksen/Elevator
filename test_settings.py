# Inside requests: each control-loop check has a 1-in-N chance of a floor button press.
# Average gap per elevator = N x POLL_INTERVAL_S (30000 x 0.01 s = 5 minutes).
FLOOR_REQUEST_INSIDE_PROBABILITY = 30000

# If True, the floors in FLOOR_LIST_OUTSIDE are used (in order, once).
# If False, the list of floors will be random and endless.
FLOOR_LIST_OUTSIDE_SET = False
FLOOR_LIST_OUTSIDE = [1, 3, 5, 7, 9, 20, 4, 16, 1, 18, 13, 2, 9, 10, 1, 0, 13, 9, 4, 7, 15, 10, 0, 2, 6, 5, 25, 12, 8, 4]

# Seconds between outside requests: a random whole number in this range (inclusive)
FLOOR_REQUEST_OUTSIDE_INTERVAL = (5, 30)
