from datetime import datetime


def timeit(method):
    def timed(*args, **kw):
        ts = datetime.now()
        result = method(*args, **kw)
        te = datetime.now()
        delta = te - ts
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = delta.seconds
        else:
            print(f"{method.__name__}, {delta.microseconds/1000:.3f} ms")
        return result
    return timed