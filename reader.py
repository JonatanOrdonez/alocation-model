import csv
import numpy as np


def readCSV(filename):
    rows = []
    with open(filename) as file:
        reader = csv.reader(file, delimiter=',')
        next(reader, None)

        for row in reader:
            cleanRow = np.array(row).astype(np.float)
            rows.append(cleanRow)

    return np.array(rows)
