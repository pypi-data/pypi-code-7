#!/usr/bin/env python3

import csv
import sys
#import matplotlib.pyplot as plt

def main():
    lpos, lscore, leq, lph, lmh = list(), list(), list(), list(), list()
    for l in csv.reader(sys.stdin, delimiter="\t"):
        if l and l[0].startswith("DEBUG"):
            _, pos, score, Eq, Ph, Mh = l

            lpos.append(int(pos))
            lscore.append(int(score))
            leq.append(int(Eq))
            lph.append(int(Ph))
            lmh.append(int(Mh))
        else:
            print("\t".join(l))
    
    print("Eq")
    for Eq in leq:
        print(bin(Eq).rjust(66))
    print("Ph")
    for Ph in lph:
        print(bin(Ph).rjust(66))
    print("Mh")
    for Mh in lmh:
        print(bin(Mh).rjust(66))
    
    #x = range(len(lpos))
    #plt.plot(lpos, score)
    #plt.show()

if __name__ == "__main__":
    main()
