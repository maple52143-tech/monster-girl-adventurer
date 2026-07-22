import random

def pop_random(lst: list):
    if not lst:
        raise IndexError("巧妇难为无米之炊。")
    idx = random.randrange(len(lst))
    return lst.pop(idx)