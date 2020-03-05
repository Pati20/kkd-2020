# Author: Patrycja Paradowska, 244952
# 05.03.2020r., Lista 1 - entropia warunkowa.
import math, sys

ALPH_SIZE = 256
symbols = range(ALPH_SIZE)

def entropy(data):
    s = sum(data)
    if s == 0:
        return 0
    H = 0
    for i in data:
        P = i / s
        H += -(P * math.log2(P)) if P > 0 else 0
    return H

def conditional_entropy(data, single):
    s = sum(map(sum, data))
    s_pred = sum(single)
    if s == 0:
        return 0
    H = 0
    for i in symbols:
        for k in symbols:
            item = data[i][k]
            pred = single[i]
            Pxy = item / s
            Px = pred / s_pred
            if Pxy == 0.0 or Px == 0.0:
                continue
            H += Pxy * math.log2(Px / Pxy)
    return H

def main(file):
    single = [0 for a in symbols]
    double = [[0 for a in symbols] for b in symbols]
    with open(file, "rb") as f:
        dataset = f.read()
        previous = 0
        for j in dataset:
            single[j] += 1
            double[previous][j] += 1
            previous = j

    print("ENTROPIA: {: f}".format(entropy(single)))
    print('ENTROPIA WARUNKOWA: {: f}'.format(conditional_entropy(double, single)))
    # print('Różnica: {: f}'.format(entropy(single) - conditional_entropy(double, single)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Missing argument!')
        exit(1)
    dataset = sys.argv[1]
    main(dataset)