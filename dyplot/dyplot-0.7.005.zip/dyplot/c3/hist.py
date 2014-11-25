from dyplot.c3.bar import Bar
import math
class Hist(Bar):
    def __init__(self, x, bins=10):
        xmax = math.ceil(max(x))
        xmin = math.floor(min(x))
        xstep = (xmax-xmin)/bins
        xaxis = []
        xheight = []
        for i in range(bins):
            xaxis.append(xmin+i*xstep)
            xheight.append(0) 
        xaxis.append(xmax)
        xheight.append(0) 
        for item in x:
            for j in range(len(xaxis)):
                if item > xaxis[j] and item < xaxis[j+1]:
                    xheight[j] += 1
                    break
        Bar.__init__(self, xheight, "Frequency")
        xtick = []
        xtick.append("x")
        xtick.extend(xaxis)
        self.option["data"]["columns"].append(xtick)
        self.option["data"]["x"] = "x"
        self.option["bar"]["width"]["ratio"] = 1

