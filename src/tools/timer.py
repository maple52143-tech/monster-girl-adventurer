class Timer:
    def __init__(self, duration: float):
        self.duration = duration
        self.time = 0

    def update(self, delta_time):
        self.time += delta_time
        if self.time >= self.duration:
            return True
        return False


class Motion:
    def __init__(self, duration: float, obj, var_name: str, start, end, motion_func = lambda x: x):
        self.duration = duration
        self.time = 0
        self.start = start
        self.delta = end - start
        self.end = end
        self.obj = obj
        self.var_name = var_name
        self.motion_func = motion_func

    def update(self, delta_time: float):
        self.time += delta_time
        if self.time >= self.duration:
            setattr(self.obj, self.var_name, self.end)
            return True

        t = self.start + self.motion_func(self.time / self.duration) * self.delta
        setattr(self.obj, self.var_name, t)
        return False