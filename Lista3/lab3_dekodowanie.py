#Author: Patrycja Paradowska, 244952
import sys
import bitarray


def read_file_by_bytes_to_bits(file):
    ba = bitarray.bitarray()
    with open(file, 'rb') as f:
        bytes_ = f.read()
        ba.frombytes(bytes_)
        bits = ba.to01()
    return bits

def write_to_file_bytes(file, code):
    with open(file, 'wb') as f:
        f.write(code)

def elias_delta_dec(data):
    outcome = []
    while data:
        try:
            L = data.index('1')
        except ValueError:
            break
        data = data[L:]
        N = int(data[:L + 1], 2) - 1
        data = data[L + 1:]
        outcome.append(int('1' + data[:N], 2))
        data = data[N:]
    return outcome

def elias_gamma_dec(data):
    outcome = []
    while data:
        try:
            i = data.index('1')
        except ValueError:
            break
        data = data[i:]
        outcome.append(int(data[:i + 1], 2))
        data = data[i + 1:]
    return outcome

def elias_omega_dec(data):
    outcome = []
    N = 1
    while data:
        if data[0] == '0':
            data = data[1:]
            outcome.append(N)
            N = 1
        else:
            curr = data[:N + 1]
            data = data[N + 1:]
            N = int(curr, 2)
    return outcome

def fib_memory(f):
    mem = {}
    mem_v = {}

    def internal(n, purpose):
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
    return internal


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

def fibbonacci_dec(data):
    outcome = []
    words = map(lambda x: x + '1', data.split('11')[:-1])
    for s in words:
        curr = 0
        for i in range(len(s), 0, -1):
            if s[i - 1] == '1':
                curr += fib_num(i + 1, None)[0]
        outcome.append(curr)
    return outcome

def lzw_decode(data, dict):
    cnt = len(dict) + 1
    pk = data.pop(0)
    outer = dict[pk]
    for k in data:
        pc = dict[pk]
        if k in dict:
            string = dict[k]
            dict[cnt] = pc + string[:1]
            outer += string
        else:
            b_string = pc + pc[:1]
            dict[cnt] = b_string
            outer += b_string
        pk = k
        cnt += 1
    return outer

def decompress(code, decoding_method):
    codes = decoding_method(code)
    dictionary = {i + 1: i.to_bytes(1, 'big') for i in range(2 ** 8)}
    return lzw_decode(codes, dictionary)


if __name__ == '__main__':
        if len(sys.argv) == 4:
            option_of_decoding = elias_omega_dec
            if sys.argv[3] == '-gamma':
                is_omega = False
                option_of_decoding = elias_gamma_dec
            elif sys.argv[3] == '-omega':
                option_of_decoding = elias_omega_dec
            elif sys.argv[3] == '-delta':
                is_omega = False
                option_of_decoding = elias_delta_dec
            elif sys.argv[3] == '-fibb':
                is_omega = False
                option_of_decoding = fibbonacci_dec
            code = read_file_by_bytes_to_bits(sys.argv[1])
            decoded = decompress(code, option_of_decoding)
            write_to_file_bytes(sys.argv[2], decoded)
        else:
            print("Niewłaściwa liczba argumentów!")

# sudo apt-get install -y python-bitarray