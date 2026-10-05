import csv
import time
from threading import Lock


class StateLogger:
    def __init__(self, path):
        self._start = time.monotonic()
        self._lock = Lock()
        self._f = open(path, 'w', newline='')
        self._writer = csv.writer(self._f)
        self._writer.writerow(['t', 'elevator', 'floor', 'direction', 'event'])
        self._count = 0

    def log(self, elevator, floor, direction, event):
        t = round(time.monotonic() - self._start, 3)
        with self._lock:
            self._writer.writerow([t, elevator, floor, direction, event])
            self._count += 1
            if self._count % 1000 == 0:
                self._f.flush()

    def close(self):
        with self._lock:
            self._f.flush()
            self._f.close()
