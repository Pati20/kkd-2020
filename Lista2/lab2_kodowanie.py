# Author: Patrycja Paradowska, 244952
import contextlib
import math
import sys


class KodowanieArytmetyczne():
    def __init__(self, nbits):
        if nbits < 1:
            raise ValueError("State size out of range")
        self.num_state_bits = nbits
        self.full_range = 1 << self.num_state_bits
        self.half_range = self.full_range >> 1
        self.quarter_range = self.half_range >> 1
        self.minimum_range = self.quarter_range + 2
        self.maximum_total = self.minimum_range
        self.state_mask = self.full_range - 1
        self.low = 0
        self.high = self.state_mask

    def updateState(self, freqs, symbol):
        low = self.low
        high = self.high
        rng = high - low + 1
        total = freqs.get_total()
        symlow = freqs.get_low(symbol)
        symhigh = freqs.get_high(symbol)

        newlow = low + symlow * rng // total
        newhigh = low + symhigh * rng // total - 1
        self.low = newlow
        self.high = newhigh
        while ((self.low ^ self.high) & self.half_range) == 0:
            self.shift()
            self.low = ((self.low << 1) & self.state_mask)
            self.high = ((self.high << 1) & self.state_mask) | 1
        while (self.low & ~self.high & self.quarter_range) != 0:
            self.underflow()
            self.low = (self.low << 1) ^ self.half_range
            self.high = ((self.high ^ self.half_range) << 1) | self.half_range | 1

    def shift(self):
        raise NotImplementedError()

    def underflow(self):
        raise NotImplementedError()


class Encoder(KodowanieArytmetyczne):
    def __init__(self, numbits, bitout):
        super(Encoder, self).__init__(numbits)
        self.output = bitout
        self.num_underflow = 0

    def write(self, freqs, symbol):
        if not isinstance(freqs, Wrapper):
            freqs = Wrapper(freqs)
        self.updateState(freqs, symbol)

    def finish(self):
        self.output.write(1)

    def shift(self):
        bit = self.low >> (self.num_state_bits - 1)
        self.output.write(bit)
        for _ in range(self.num_underflow):
            self.output.write(bit ^ 1)
        self.num_underflow = 0

    def underflow(self):
        self.num_underflow += 1


class TableCode():
    def get_symbol_limit(self):
        raise NotImplementedError()

    def get(self, symbol):
        raise NotImplementedError()

    def set(self, symbol, freq):
        raise NotImplementedError()

    def increment(self, symbol):
        raise NotImplementedError()

    def get_total(self):
        raise NotImplementedError()

    def get_low(self, symbol):
        raise NotImplementedError()

    def get_high(self, symbol):
        raise NotImplementedError()


class FlatFrequencyTable(TableCode):
    def __init__(self, numsyms):
        self.numsymbols = numsyms

    def get_symbol_limit(self):
        return self.numsymbols

    def get(self, symbol):
        return 1

    def get_total(self):
        return self.numsymbols

    def get_low(self, symbol):
        return symbol

    def get_high(self, symbol):
        return symbol + 1

    def set(self, symbol, freq):
        raise NotImplementedError()

    def increment(self, symbol):
        raise NotImplementedError()


class FrequencyTable(TableCode):
    def __init__(self, freqs):
        if isinstance(freqs, TableCode):
            numsym = freqs.get_symbol_limit()
            self.frequencies = [freqs.get(i) for i in range(numsym)]
        else:
            self.frequencies = list(freqs)
        if len(self.frequencies) < 1:
            raise ValueError("At least 1 symbol needed")
        self.total = sum(self.frequencies)
        self.cumulative = None

    def get_symbol_limit(self):
        return len(self.frequencies)

    def get(self, symbol):
        return self.frequencies[symbol]

    def set(self, symbol, freq):
        temp = self.total - self.frequencies[symbol]
        self.total = temp + freq
        self.frequencies[symbol] = freq
        self.cumulative = None

    def increment(self, symbol):
        self.total += 1
        self.frequencies[symbol] += 1
        self.cumulative = None

    def get_total(self):
        return self.total

    def get_low(self, symbol):
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol]

    def get_high(self, symbol):
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol + 1]

    def _init_cumulative(self):
        cumul = [0]
        sum = 0
        for freq in self.frequencies:
            sum += freq
            cumul.append(sum)
        assert sum == self.total
        self.cumulative = cumul

    def entropy(self):
        return sum([(x - 1) * (math.log(self.get_in_size(), 2) - math.log((x - 1), 2)) for x in self.frequencies if
                    x > 1]) / self.get_in_size()

    def get_in_size(self):
        return self.total - len(self.frequencies)


class Wrapper(TableCode):
    def __init__(self, freqtab):
        self.freqtable = freqtab

    def get_symbol_limit(self):
        result = self.freqtable.get_symbol_limit()
        return result

    def get(self, symbol):
        return self.freqtable.get(symbol)

    def get_total(self):
        result = self.freqtable.get_total()
        return result

    def get_low(self, symbol):
        low = self.freqtable.get_low(symbol)
        high = self.freqtable.get_high(symbol)
        return low

    def get_high(self, symbol):
        low = self.freqtable.get_low(symbol)
        high = self.freqtable.get_high(symbol)
        return high

    def set(self, symbol, freq):
        self.freqtable.set(symbol, freq)

    def increment(self, symbol):
        self.freqtable.increment(symbol)


class Output_bitstream():
    def __init__(self, out):
        self.output = out
        self.bitbuffer = 0
        self.buffersize = 0
        self.totalbytes = 0

    def write(self, b):
        self.bitbuffer = (self.bitbuffer << 1) | b
        self.buffersize += 1
        if self.buffersize == 8:
            towrite = bytes((self.bitbuffer,))
            self.output.write(towrite)
            self.totalbytes += 1
            self.bitbuffer = 0
            self.buffersize = 0

    def close(self):
        while self.buffersize != 0:
            self.write(0)
        self.output.close()

    def get_totalbytes(self):
        return self.totalbytes


if __name__ == "__main__":
    if len(sys.argv) == 3:
        with open(sys.argv[1], "rb") as input, contextlib.closing(Output_bitstream(open(sys.argv[2], "wb"))) as output:
            initfreqs = FlatFrequencyTable(257)
            freqs = FrequencyTable(initfreqs)
            enc = Encoder(32, output)
            sym = input.read(1)
            while sym:
                sym = sym[0]
                enc.write(freqs, sym)
                freqs.increment(sym)
                sym = input.read(1)
            enc.write(freqs, 256)
            enc.finish()
            print('Entropia kodowanych danych wynosi: ', freqs.entropy())
            print('Stopień kompresji:', freqs.get_in_size() / output.get_totalbytes())
            print('Średnia długość kodowania:', output.get_totalbytes() * 8 / freqs.get_in_size())
    else:
        print("Niewłaściwa liczba argumentów! Podaj: python lab2_kodowanie.py <plik_wejsciowy> <plik_wyjsciowy>!")