# Author: Patrycja Paradowska, 244952

import sys
from math import log2
from typing import List

TGA_IMAGE_FOOTER: int = 26

class Pixel:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
    def __str__(self):
        return "(r " + str(self.r) + ", g " + str(self.g) + ", b " + str(self.b) + ")"

class ImageStats:
    def __init__(self, width: int, height: int):
        self.width = width
        self.pixel_arr = [[Pixel(0, 0, 0) for _ in range(height)] for _ in range(width)]
        self.rgb_arr = [[0 for _ in range(256)] for _ in range(3)]
        self.rgb_occur = [0, 0, 0]
        self.signArray = [0 for _ in range(256)]
        self.idx = 0
        self.idy = 0

    def clear_arrays(self):
        self.rgb_arr = [[0 for _ in range(256)] for _ in range(3)]
        self.rgb_occur = [0, 0, 0]
        self.signArray = [0 for _ in range(256)]

    def add_pixel(self, r: int, g: int, b: int):
        x = self.idx % self.width
        self.pixel_arr[x][self.idy] = Pixel(r, g, b)
        if self.idx == self.width - 1:
            self.idy = self.idy + 1
        self.idx = x + 1

    def get_adjacent_pixels(self, i: int, j: int):
        return self.pixel_arr[i][j] if 0 <= i < len(self.pixel_arr) and 0 <= j <= len(
            self.pixel_arr[0]) else Pixel(0, 0, 0)

    def increase_rgb_occurrences(self, r: int, g: int, b: int):
        self.rgb_occur[0] += 1
        self.rgb_arr[0][r] += 1
        self.rgb_occur[1] += 1
        self.rgb_arr[1][g] += 1
        self.rgb_occur[2] += 1
        self.rgb_arr[2][b] += 1

    def increase_sign_occurrences(self, r: int, g: int, b: int):
        self.signArray[r] += 1
        self.signArray[g] += 1
        self.signArray[b] += 1

    def get_all_sign_occurrences(self) -> int:
        return self.rgb_occur[0] + self.rgb_occur[1] + self.rgb_occur[2]

class ByteDataCollector:
    def __init__(self, byte_array):
        self.byte_array = byte_array
        self.offset = 0
    def read(self) -> int:
        reader = self.byte_array[self.offset]
        self.offset = self.offset + 1
        return reader

def get_bytes_from_file(filename: str):
    return bytearray(open(filename, "rb").read())

def entropy(frequency, size):
    return -sum([(v / size) * (log2(v) - log2(size))
                 for v in frequency if v > 0])

def define_predicates():
    func = [lambda x, y, z: x, lambda x, y, z: y, lambda x, y, z: z, lambda x, y, z: (x + y - z),
            lambda x, y, z: (x + (y - z) / 2), lambda x, y, z: (y + (x - z) / 2), lambda x, y, z: ((x + y) / 2),
            lambda x, y, z: new_standard(x, y, z)]
    return func

def new_standard(x, y, z):
    maximum = max(y, z)
    if x > maximum:
        return maximum
    minimum = min(y, z)
    return minimum if x <= minimum else (z + y - x)

def mod256(x: int):
    value: int = x % 256
    return value & 0xFF if value < 0 else value

def predictions(image_stats: ImageStats):
    predicates = define_predicates()
    best_entropy = [sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize]
    best_func = [sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize]

    for i in range(0, len(predicates)):
        image_stats.clear_arrays()
        for j in range(0, len(image_stats.pixel_arr)):
            for k in range(0, len(image_stats.pixel_arr[j])):
                pixel_x = image_stats.pixel_arr[j][k]
                pixel_a = image_stats.get_adjacent_pixels(j, k - 1)
                pixel_b = image_stats.get_adjacent_pixels(j - 1, k)
                pixel_c = image_stats.get_adjacent_pixels(j - 1, k - 1)

                predicted_red = mod256(pixel_x.r - int(predicates[i](pixel_c.r, pixel_b.r, pixel_a.r)))
                predicted_green = mod256(pixel_x.g - int(predicates[i](pixel_c.g, pixel_b.g, pixel_a.g)))
                predicted_blue = mod256(pixel_x.b - int(predicates[i](pixel_c.b, pixel_b.b, pixel_a.b)))

                image_stats.increase_rgb_occurrences(predicted_red, predicted_green, predicted_blue)
                image_stats.increase_sign_occurrences(predicted_red, predicted_green, predicted_blue)

        curr_entropy = [entropy(image_stats.rgb_arr[0], image_stats.rgb_occur[0]),  # R
                        entropy(image_stats.rgb_arr[1], image_stats.rgb_occur[1]),  # G
                        entropy(image_stats.rgb_arr[2], image_stats.rgb_occur[2]),  # B
                        entropy(image_stats.signArray, image_stats.get_all_sign_occurrences())]
        update_best_stats(i, curr_entropy, best_entropy, best_func)

    print_best_results(best_entropy, best_func)

def update_best_stats(func_idx: int, current_entropy: List, best_entropy: List, best_func):
    for i in range(0, len(best_entropy)):
        if current_entropy[i] < best_entropy[i]:
            best_entropy[i] = current_entropy[i]
            best_func[i] = func_idx

def file_stats(image_stats: ImageStats):
    print("File entropy : ", entropy(image_stats.signArray, image_stats.get_all_sign_occurrences()))
    print("Red entropy : ", entropy(image_stats.rgb_arr[0], image_stats.rgb_occur[0]))
    print("Green entropy : ", entropy(image_stats.rgb_arr[1], image_stats.rgb_occur[1]))
    print("Blue entropy : ", entropy(image_stats.rgb_arr[2], image_stats.rgb_occur[2]))


def print_best_results(best_results: List, best_func: List):
    print("Numeracja funkcji jest taka : ")
    print("0. A\n1. B\n2. C\n3. A+B-C\n4. A+(B-C)/2\n5. B+(A-C)/2\n6. (A+B)/2\n7. New standard")
    print("Best file  [", best_func[3], "] : ", best_results[3])
    print("Best red   [", best_func[0], "] : ", best_results[0])
    print("Best green [", best_func[1], "] : ", best_results[1])
    print("Best blue  [", best_func[2], "] : ", best_results[2])


def main(file_name: str):
    byte_collector = ByteDataCollector(get_bytes_from_file(file_name))
    for i in range(0, 12):
        byte_collector.read()

    width = byte_collector.read() + ((byte_collector.read()) << 8)
    height = byte_collector.read() + ((byte_collector.read()) << 8)
    byte_collector.read()
    byte_collector.read()

    image_stats = ImageStats(width, height)
    n: int = width * height - TGA_IMAGE_FOOTER
    if n < 0:
        raise ValueError('Image file size is to small')

    is_uncompressed = byte_collector.byte_array[2] == 0x02
    if is_uncompressed and byte_collector.byte_array[16] == 0x20:
        raise ValueError('Image has RGBA color definition!')
    elif is_uncompressed and byte_collector.byte_array[16] == 0x18:
        while n > 0:
            b = int(byte_collector.read())
            g = int(byte_collector.read())
            r = int(byte_collector.read())
            image_stats.add_pixel(r, g, b)
            image_stats.increase_rgb_occurrences(r, g, b)
            image_stats.increase_sign_occurrences(r, g, b)
            n = n - 1
    else:
        raise ValueError('Image is compressed!')
    file_stats(image_stats)
    predictions(image_stats)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Niepoprawna liczba argumentów! Wpisz: python lab4.py nazwapliku.tga")
        exit(1)
    main(sys.argv[1])