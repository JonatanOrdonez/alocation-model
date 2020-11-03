import math


def gompertz(a, b, r, day):
    return a * math.exp(-b * math.exp(-r * day))


def gompertzNewCases(a, b, r, day):
    return gompertz(a, b, r, day) - gompertz(a, b, r, day-1)
