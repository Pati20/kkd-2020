#Author: Patrycja Paradowska, 244952

import sys
import math
from typing import List

TGA_IMAGE_HEADER_SIZE = 18
TGA_IMAGE_FOOTER_SIZE = 25

class Pixel:

    def __init__(self, blue: float, green: float, red: float):
        self.blue = blue
        self.green = green
        self.red = red

    @staticmethod
    def create_pixel_array(size: int, buff: bytes) -> List:
        return [Pixel(buff[i * 3], buff[i * 3 + 1], buff[i * 3 + 2]) for i in range(0, size)]

    def get_distance_to_pixel(self, pixel: 'Pixel') -> float:
        return math.pow(self.blue - pixel.blue, 2) + math.pow(self.green - pixel.green, 2) + math.pow(
            self.red - pixel.red, 2)

    def get_scaled_vector(self, epsilon: float) -> 'Pixel':
        return Pixel(self.blue * epsilon, self.green * epsilon, self.red * epsilon)

    def flor_vectors(self) -> 'Pixel':
        self.blue = math.floor(self.blue)
        self.green = math.floor(self.green)
        self.red = math.floor(self.red)
        return self

    def get_squared_length_of_vector(self):
        return math.pow(self.blue, 2) + math.pow(self.green, 2) + math.pow(
            self.red, 2)


class CodeWord:

    def __init__(self, pixel: Pixel):
        self.nearest_members: List[Pixel] = []
        self.main_word: Pixel = pixel

    def remove_all_members(self):
        self.nearest_members = []

    def add_new_pixel(self, pixel: Pixel):
        self.nearest_members.append(pixel)

    def update_code_word(self, new_state: Pixel):
        self.main_word = new_state

    def __str__(self) -> str:
        return "[(" + str(self.main_word.blue) + "," + str(self.main_word.green) + "," + str(
            self.main_word.blue) + ")]  -> " + str(
            len(self.nearest_members))


class Vectorization:

    def __init__(self):
        self.code_words: List[CodeWord] = []
        self.epsilon: float = 0.00_001
        self.pixels: List[Pixel] = []

    def create_codebook(self, pixels: List, size_codebook: int):
        code_word = CodeWord(self.get_middle_vector_from_set(pixels))
        self.code_words.append(code_word)
        self.pixels = pixels
        avg_dist = Vectorization.get_avg_distance_from_main_codeword(code_word, pixels)

        while len(self.code_words) < size_codebook:
            self.enlarge_collection()
            avg_dist = self.LBG_algorithm(avg_dist)

        return self.code_words

    def enlarge_collection(self):
        code_words: List[CodeWord] = []
        for cw in self.code_words:
            word1 = CodeWord(cw.main_word.get_scaled_vector(1 + self.epsilon))
            code_words.append(word1)
            word2 = CodeWord(cw.main_word.get_scaled_vector(1 - self.epsilon))
            code_words.append(word2)
        self.code_words = code_words

    def LBG_algorithm(self, init_avg_distance: float) -> float:
        avg_distance = 0.0
        err = 1.0 + self.epsilon

        while err > self.epsilon:
            for cw in self.code_words: cw.remove_all_members()
            self.clusterization()
            self.generate_centroid()
            before_distance = avg_distance if avg_distance > 0 else init_avg_distance
            avg_distance: float = self.quantization_error()
            err = (before_distance - avg_distance) / before_distance
        return avg_distance

    def clusterization(self):
        reset = math.pow(2, 24)
        for pixel in self.pixels:
            shortest = reset
            idx = 0
            for i, cw in enumerate(self.code_words):
                distance = pixel.get_distance_to_pixel(cw.main_word)
                if distance < shortest:
                    shortest = distance
                    idx = i
            self.code_words[idx].add_new_pixel(pixel)

    def generate_centroid(self):
        for cw in self.code_words:
            if len(cw.nearest_members) > 0:
                new_matched_cw = Vectorization.get_middle_vector_from_set(cw.nearest_members)
                cw.update_code_word(new_matched_cw)

    @staticmethod
    def get_middle_vector_from_set(pixels: List[Pixel]) -> Pixel:
        size: int = len(pixels)
        colors = [0, 0, 0]  # bgr
        for p in pixels:
            colors[0] += p.blue
            colors[1] += p.green
            colors[2] += p.red
        return Pixel(colors[0] / size, colors[1] / size, colors[2] / size)

    @staticmethod
    def get_avg_distance_from_main_codeword(code_word: CodeWord, pixels: List[Pixel]) -> float:
        sum = 0.0
        for p in pixels:
            sum += p.get_distance_to_pixel(code_word.main_word) / len(pixels)
        return sum

    def quantization_error(self) -> float:
        err: float = 0.0
        for cw in self.code_words:
            for pixel in cw.nearest_members:
                err += (cw.main_word.get_distance_to_pixel(pixel) / len(self.pixels))
        return err


def quantify(pixel_arr: List[Pixel], code_words: List[CodeWord]) -> List[Pixel]:
    new_bitmap = []
    for cw in code_words:
        cw.main_word.flor_vectors()

    for pixel in pixel_arr:
        diffs = [pixel.get_distance_to_pixel(cw.main_word) for cw in code_words]
        new_bitmap.append(code_words[diffs.index(min(diffs))].main_word)

    return new_bitmap


def pixels_to_bytes(pixel_arr: List[Pixel]):
    payload = []
    for p in pixel_arr:
        payload.append(int(p.blue))
        payload.append(int(p.green))
        payload.append(int(p.red))

    return bytes(payload)

def mse_rate(pixel_arr: List[Pixel], new_arr: List[Pixel]) -> float:
    return (1 / len(pixel_arr)) * sum(
        [(pixel_arr[i].get_distance_to_pixel(new_arr[i])) ** 2 for i in range(len(pixel_arr))]
    )

def snr_rate(pixel_arr: List[Pixel], ms_rate: float) -> float:
    return ((1 / len(pixel_arr)) * sum([pixel_arr[i].get_squared_length_of_vector() for i in range(len(pixel_arr))
                                        ])) / ms_rate


def get_tga_image_width(buffer: bytes) -> int:
    return buffer[12] + (buffer[13] << 8)


def get_tga_image_height(buffer: bytes) -> int:
    return buffer[14] + (buffer[15] << 8)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        raise ValueError('Niepoprawne uruchomienie. Użyj: python lista5.py <obraz_wejsciowy> <obraz_wyjsciowy> <liczba_kolorow>')
    with open(sys.argv[1], 'rb') as f:
        tga_buffer_image: bytes = f.read()
        tga_header = tga_buffer_image[:TGA_IMAGE_HEADER_SIZE]
        tga_footer = tga_buffer_image[len(tga_buffer_image) - TGA_IMAGE_FOOTER_SIZE:]
        tga_width: int = get_tga_image_width(tga_buffer_image)
        tga_height: int = get_tga_image_height(tga_buffer_image)

        pixel_arr = Pixel.create_pixel_array(tga_width * tga_height,
                                             tga_buffer_image[
                                             TGA_IMAGE_HEADER_SIZE:len(tga_buffer_image) - TGA_IMAGE_FOOTER_SIZE])

        code_words: List[CodeWord] = Vectorization().create_codebook(pixel_arr, 2 ** int(sys.argv[3]))
        new_pixel_arr = quantify(pixel_arr, code_words)
        pixels_as_byte = pixels_to_bytes(new_pixel_arr)

        mse = mse_rate(pixel_arr, new_pixel_arr)
        snratio = snr_rate(pixel_arr, mse)
        print("MSE:", mse)
        print("SNR:", snratio)

        with open(sys.argv[2], "wb") as output:
            quantized = tga_header + pixels_as_byte + tga_footer
            output.write(quantized)
