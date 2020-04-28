# Author: Patrycja Paradowska, 244952
import contextlib
import math
import sys


class ArithmeticCoder():
    def __init__(self, numbits):
        if numbits < 1:
            raise ValueError("State size out of range")
        self.num_state_bits = numbits
        self.full_range = 1 << self.num_state_bits
        self.half_range = self.full_range >> 1
        self.quarter_range = self.half_range >> 1
        self.minimum_range = self.quarter_range + 2
        self.maximum_total = self.minimum_range
        self.state_mask = self.full_range - 1
        self.low = 0
        self.high = self.state_mask

    def update(self, freqs, symbol):
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


class ArytmetyczeDekodowanie(ArithmeticCoder):
    def __init__(self, numbits, bitin):
        super(ArytmetyczeDekodowanie, self).__init__(numbits)
        self.input = bitin
        self.code = 0
        for _ in range(self.num_state_bits):
            self.code = self.code << 1 | self.read_code_bit()

    def read(self, freqs):
        if not isinstance(freqs, CheckedFrequencyTable):
            freqs = CheckedFrequencyTable(freqs)
        total = freqs.get_total()
        range = self.high - self.low + 1
        offset = self.code - self.low
        value = ((offset + 1) * total - 1) // range
        start = 0
        end = freqs.get_symbol_limit()
        while end - start > 1:
            middle = (start + end) >> 1
            if freqs.get_low(middle) > value:
                end = middle
            else:
                start = middle
        symbol = start
        self.update(freqs, symbol)
        return symbol

    def shift(self):
        self.code = ((self.code << 1) & self.state_mask) | self.read_code_bit()

    def underflow(self):
        self.code = (self.code & self.half_range) | ((self.code << 1) & (self.state_mask >> 1)) | self.read_code_bit()

    def read_code_bit(self):
        temp = self.input.read()
        if temp == -1:
            temp = 0
        return temp


class FrequencyTable():
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


class FlatFrequencyTable(FrequencyTable):
    def __init__(self, numsyms):
        if numsyms < 1:
            raise ValueError("Number of symbols must be positive")
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

    def _check_symbol(self, symbol):
        if 0 <= symbol < self.numsymbols:
            return
        else:
            raise ValueError("Symbol out of range")


class SimpleFrequencyTable(FrequencyTable):
    def __init__(self, freqs):
        if isinstance(freqs, FrequencyTable):
            numsym = freqs.get_symbol_limit()
            self.frequencies = [freqs.get(i) for i in range(numsym)]
        else:
            self.frequencies = list(freqs)
        if len(self.frequencies) < 1:
            raise ValueError("At least 1 symbol needed")
        for freq in self.frequencies:
            if freq < 0:
                raise ValueError("Negative frequency")
        self.total = sum(self.frequencies)
        self.cumulative = None

    def get_symbol_limit(self):
        return len(self.frequencies)

    def get(self, symbol):
        return self.frequencies[symbol]

    def set(self, symbol, freq):
        if freq < 0:
            raise ValueError("Negative frequency")
        temp = self.total - self.frequencies[symbol]
        assert temp >= 0
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


class CheckedFrequencyTable(FrequencyTable):
    def __init__(self, freqtab):
        self.freqtable = freqtab

    def get_symbol_limit(self):
        result = self.freqtable.get_symbol_limit()
        return result

    def get(self, symbol):
        result = self.freqtable.get(symbol)
        return result

    def get_total(self):
        result = self.freqtable.get_total()
        return result

    def get_low(self, symbol):
        if self._is_symbol_in_range(symbol):
            low = self.freqtable.get_low(symbol)
            high = self.freqtable.get_high(symbol)
            return low
        else:
            self.freqtable.get_low(symbol)
            raise AssertionError("ValueError expected")

    def get_high(self, symbol):
        if self._is_symbol_in_range(symbol):
            low = self.freqtable.get_low(symbol)
            high = self.freqtable.get_high(symbol)
            return high
        else:
            self.freqtable.get_high(symbol)
            raise AssertionError("ValueError expected")

    def set(self, symbol, freq):
        self.freqtable.set(symbol, freq)

    def increment(self, symbol):
        self.freqtable.increment(symbol)

    def _is_symbol_in_range(self, symbol):
        return 0 <= symbol < self.get_symbol_limit()


class BitInputStream():
    def __init__(self, inp):
        self.input = inp
        self.bitbuffer = 0
        self.buffersize = 0

    def read(self):
        if self.bitbuffer == -1:
            return -1
        if self.buffersize == 0:
            temp = self.input.read(1)
            if len(temp) == 0:
                self.bitbuffer = -1
                return -1
            self.bitbuffer = temp[0]
            self.buffersize = 8
        self.buffersize -= 1
        return (self.bitbuffer >> self.buffersize) & 1

    def close(self):
        self.input.close()
        self.bitbuffer = -1
        self.buffersize = 0

if __name__ == "__main__":
    with open(sys.argv[2], "wb") as output, contextlib.closing(BitInputStream(open(sys.argv[1], "rb"))) as input:
        fr = FlatFrequencyTable(257)
        frtab = SimpleFrequencyTable(fr)
        dekode = ArytmetyczeDekodowanie(32, input)
        while True:
            s = dekode.read(frtab)
            if s == 256:
                break
            output.write(bytes((s,)))
            frtab.increment(s)