import math


def milliseconds_to_hhmmss(time):
    hundredths = str(math.floor(time % 1000)).zfill(3)
    time /= 1000
    seconds = str(math.floor(time % 60)).zfill(2)
    minutes = str(math.floor((time / 60) % 60)).zfill(2)
    hours = str(math.floor((time / 60 / 60) % 60)).zfill(2)

    return hours + ":" + minutes + ":" + seconds + "." + hundredths


def hhmmss_to_milliseconds(hh, mm, ss, hundredths):
    val = (int(ss) + int(mm) * 60 + int(hh) * 60 * 60) * 1000
    if hundredths:
        val += int(hundredths)
    return val
