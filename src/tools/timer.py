class Timer:
    def __init__(self, duration: float):
        self.duration = duration
        self.time = 0

    def update(self, delta_time):
        self.time += delta_time
        if self.time >= self.duration:
            return True
        return False