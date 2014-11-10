from time import mktime, strftime, localtime, strptime


def gen_comparing_time(hour, minute, second):
    lt = localtime()
    st = "%s %s %s %d:%d:%d" %(
        strftime("%d", lt),
        strftime("%m", lt),
        strftime("%Y", lt),
        hour,
        minute,
        second)

    t = strptime(st, "%d %m %Y %H:%M:%S")

    return mktime(t)
