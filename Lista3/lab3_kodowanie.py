# Author: Patrycja Paradowska, 244952
import sys
from collections import Counter
from math import log2, ceil

import bitarray

def read_file_by_bytes(file):
    chars = []
    with open(file, "rb") as f:
        while True:
            byte = f.read(1)
            if not byte: break
            chars.append(byte)
    return chars


def write_to_file_chars(file, code):
    with open(file, 'w') as f:
        f.write(code)


def write_to_file_bytes_string(file, data, is_omega=False):
    ba = bitarray.bitarray()
    ba.extend(''.join(data))

    if is_omega:
        while len(ba) % 8 != 0:
            ba.append(True)

    pad = len(ba) * 8

    with open(file, 'wb') as f:
        ba.tofile(f)

    return ba.tobytes()


def write_to_file_bytes(file, code):
    with open(file, 'wb') as f:
        f.write(code)

def elias_delta(N):
    outcome = ''
    if N > 0:
        x = int(log2(N))
        y = int(log2(x + 1))
        outcome = '0' * y
        outcome += '{0:b}'.format(x + 1)
        outcome += '{0:b}'.format(N)[1:]
    return outcome

def elias_gamma(N):
    outcome = ''
    if N > 0:
        x = int(log2(N))
        outcome = '0' * x
        outcome += '{0:b}'.format(N)
    return outcome

def elias_omega(N):
    outcome = ['0']
    while N > 1:
        curr = '{0:b}'.format(N)
        outcome.append(curr)
        N = len(curr) - 1
    return ''.join(reversed(outcome))

def fib_memory(f):
    mem = {}
    mem_v = {}
    def interial(n, purpose):
        i = 0
        if n not in mem:
            mem[n] = f(n, purpose)[0]
            mem_v[mem[n]] = n
        if purpose:
            for val in sorted(mem.values(), reverse=True):
                if i == 0 and val < purpose:
                    break
                if val <= purpose:
                    return val, True, mem_v[val]
                i += 1
        return mem[n], False, 0
    return interial


@fib_memory
def fib_num(N, purpose):
    if N < 1:
        return 0, (False if purpose and purpose > 0 else True), 0
    if N == 1:
        return 1, (False if purpose and purpose > 1 else True), 0
    f1 = fib_num(N - 1, purpose)
    f2 = fib_num(N - 2, purpose)
    if f1[1]:
        return f1
    if f2[1]:
        return f2
    return f1[0] + f2[0], False, 0


def fibbonacci(N):
    outcome = []
    while N > 0:
        for i in range(N + 2):
            score = fib_num(i, N)
            if score[1]:
                break
        N -= score[0]
        if len(outcome) == 0:
            outcome = ['0' for _ in range(score[2] - 2)] + ['1', '1']
        else:
            outcome[score[2] - 2] = '1'
    return ''.join(outcome)


def entropy(frequency, size):
    return -sum([(v / size) * (log2(v) - log2(size))
                 for v in frequency if v > 0])

def lzw_encode(data, dict):
    cnt = len(dict) + 1
    c = data[0]
    outer = []
    for s in data[1:]:
        if c + s in dict:
            c += s
        else:
            outer.append(dict[c])
            dict[c + s] = cnt
            cnt += 1
            c = s
    outer.append(dict[c])
    return outer

def compress(data, method_of_coding):
    dictionary = {i.to_bytes(1, 'big'): i + 1 for i in range(2 ** 8)}
    code = ''.join([method_of_coding(i) for i in lzw_encode(data, dictionary)])
    length_of_inputing_text = len(data)
    length_of_received_code = ceil(len(code) / 8)
    compression_rate = length_of_inputing_text / length_of_received_code
    entropy_of_inputing_text = entropy(Counter(data).values(), length_of_inputing_text)
    encoded_map = {i.to_bytes(1, 'big'): 0 for i in range(2 ** 8)}
    for i in range(0, len(code), 8):
        encoded_map[int(code[i:i + 8], 2).to_bytes(1, 'big')] += 1

    frequency = Counter(encoded_map).values()
    c_entropy = entropy(frequency, length_of_received_code)
    return code, (length_of_inputing_text, length_of_received_code, compression_rate), (entropy_of_inputing_text, c_entropy)

if __name__ == '__main__':
    is_omega = True
    if len(sys.argv) == 4:
        if sys.argv[3] == '-gamma':
            is_omega = False
            option_of_coding = elias_gamma
        elif sys.argv[3] == '-delta':
            is_omega = False
            option_of_coding = elias_delta
        elif sys.argv[3] == '-fibb':
            is_omega = False
            option_of_coding = fibbonacci
        elif sys.argv[3] == '-omega':
            option_of_coding = elias_omega
        text = read_file_by_bytes(sys.argv[1])
        code, compression, entropy = compress(text, option_of_coding)
        write_to_file_bytes_string(sys.argv[2], code, is_omega)
        print(f'Długość kodowanego pliku: {compression[0]} bytes')
        print(f'Długość uzyskanego kodu: {compression[1]} bytes')
        print(f'Stopień kompresji: {compression[2]}')
        print(f'Entropia kodowanego tekstu: {entropy[0]}')
        print(f'Entropia uzyskanego kodu: {entropy[1]}')
    elif len(sys.argv) == 3:
        option_of_coding = elias_omega
        text = read_file_by_bytes(sys.argv[1])
        code, compression, entropy = compress(text, option_of_coding)
        write_to_file_chars(sys.argv[2], code)
        print(f'Długość kodowanego pliku: {compression[0]} bytes')
        print(f'Długość uzyskanego kodu: {compression[1]} bytes')
        print(f'Stopień kompresji: {compression[2]}')
        print(f'Entropia kodowanego tekstu: {entropy[0]}')
        print(f'Entropia uzyskanego kodu: {entropy[1]}')
    else:
        print("Niewłaściwa liczba argumentów!")
# sudo apt-get install -y python-bitarray