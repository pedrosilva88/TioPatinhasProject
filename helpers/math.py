def round_down(num, divisor):
    if divisor > 0.00:
        return num - (num%divisor)
    else:
        return num