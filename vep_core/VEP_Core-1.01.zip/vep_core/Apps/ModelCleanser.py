import os
import argparse
import csv
import shutil
import sys
sys.path.append(os.getcwd())
from Ity import metadata_root

# Open the theta document
# Remove anything below a given threshold
# Write to a given name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script for thresholding values out of theta')
    parser.add_argument('--modelName', help='Name of the model whose theta will be clipped', required=True)
    parser.add_argument('--threshold', help='Threshold below which values are chopped out', type=float, default=.05)
    args = parser.parse_args()
    renormalize = False

    oldThetaName = os.path.join(metadata_root, args.modelName, 'TopicModel', 'fullTheta.csv')
    newThetaName = os.path.join(metadata_root, args.modelName, 'TopicModel', 'theta.csv')
    if not os.path.isfile(oldThetaName):
        shutil.copy(newThetaName, oldThetaName)
    with open(oldThetaName, 'rb') as inF:
        with open(newThetaName, 'wb') as outF:
            newWriter = csv.writer(outF)

            for line in inF:
                line = line.split(',')
                newLine = []
                for i in range(0, len(line)-1, 2):
                    if float(line[i+1]) >= args.threshold:
                        newLine += [line[i], line[i+1]]
                newWriter.writerow(newLine)