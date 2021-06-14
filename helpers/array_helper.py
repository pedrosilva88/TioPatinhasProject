from itertools import zip_longest

class Helpers(object):
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return list(zip_longest(*args, fillvalue=fillvalue))
