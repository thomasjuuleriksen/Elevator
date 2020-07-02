class Semaphore:

    def __init__(self):
        self.go = True

    def wait(self):
        while not self.go:
            pass
        self.go = False
        return None

    def signal(self):
        self.go = True
