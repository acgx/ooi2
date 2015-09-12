def to_int(s, default=0):
    try:
        n = int(s)
    except (TypeError, ValueError):
        n = default
    return n


def to_str(x, default=''):
    if x is None:
        s = default
    elif type(x) is bytes:
        s = x.decode('utf-8')
    else:
        s = str(x)
    return s
