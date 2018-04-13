#!/usr/bin/env python
import sys
import os
import binascii
import imageio
import moviepy.editor as mpy
import binascii
import base64
import argparse
from math import ceil
from Crypto.Cipher import AES
MASTER_KEY = "CorrectHorseBatteryStapleGunHead"

class SteganographyVideoException(Exception):
    pass

class StegVid():
    def __init__(self):
        pass

    def get_max_size(self, clip):
        width, height = (clip.w, clip.h)
        max_frames = clip.fps * clip.duration
        return (width * height * 3 / 8 / 1024) * max_frames


    def encrypt_val(self, text):
        secret = AES.new(MASTER_KEY)
        tag_string = (str(text) + (AES.block_size - len(str(text)) % AES.block_size) * "\0")
        cipher_text = base64.b64encode(secret.encrypt(tag_string))
        return cipher_text

    def decrypt_val(self, cipher):
        secret = AES.new(MASTER_KEY)
        decrypted = secret.decrypt(base64.b64decode(cipher))
        result = decrypted.rstrip("\0")
        return result


    def file_to_binary(self, file):
        with file as f:
            byte = f.read()
            return list(bin(int('1'+binascii.hexlify(byte), 16))[3:].zfill(8))


    def str_to_binary(self, string):
        return ''.join(format(ord(c), 'b').zfill(8) for c in string)


    def get_lsb(self, color):
        if(color % 2 == 0):
            return '0'
        else:
            return '1'


    def change_lsb(self, color, binary, index):
        if(self.get_lsb(color) != binary[index]):
            modified = list(bin(color)[2:].zfill(8))
            modified[-1] = binary[index]
            modified = int(''.join(modified), 2)
            return modified
        else:
            return color


    def compare(self, clip1, clip2):
        frames1 = []
        frames2 = []
        [frames1.append(frame) for frame in clip1.iter_frames(dtype="uint8")]
        [frames2.append(frame) for frame in clip2.iter_frames(dtype="uint8")]

        for i1, frame in enumerate(frames1):
            for i2, pixels in enumerate(frame):
                for i3, pixel in enumerate(pixels):
                    if(i3 == 100):
                        return
                    pixel1 = frames1[i1][i2][i3]
                    pixel2 = frames2[i1][i2][i3]
                    print("Original: {}, Modified: {}".format(pixel1, pixel2))


    def process_pixel(self, pixel, file_binary, index, bits_left):
        color = 0
        rgb = [pixel[0], pixel[1], pixel[2]]
        for color in range(3):
            rgb[color] = self.change_lsb(pixel[color], file_binary, index + color)
            bits_left -= 1
            if(bits_left == 0):
                break
        return (rgb[0], rgb[1], rgb[2])

    def get_header(self, string):
        results = string.split('\0', 2)
        if(len(results) != 3):
            return 0
        return results


    def analyze_header(self, clip):
        output = []
        for frame in clip.iter_frames(dtype="uint8"):
            for pixels in frame:
                for pixel in pixels:
                    for colors in pixel:
                        output.append(self.get_lsb(colors))
            first_frame = int(''.join(output), 2)
            filename, filesize, data = self.get_header(binascii.unhexlify('%x' % first_frame))
            frames_needed = ceil(float(filesize) / len(data))
            return (filename, filesize, frames_needed)


    def decode(self, clip):
        output = []
        filename, filesize, frames_needed = self.analyze_header(clip)
        print(filename, filesize, frames_needed)
        for num, frame in enumerate(clip.iter_frames(dtype="uint8")):
            print("Processing frame {} of {}...".format(num+1, frames_needed))
            for pixels in frame:
                for pixel in pixels:
                    for color in pixel:
                        output.append(self.get_lsb(color))
            if(num == frames_needed - 1):
                n = int(''.join(output), 2)
                return self.get_header(binascii.unhexlify('%x' % n))


    def show(self, file_path):
        clip = mpy.VideoFileClip(str(file_path))
        filename, filesize, data = self.decode(clip)
        with open(filename, 'wb') as f:
            f.write(data[:int(filesize)])
        with open('hide.txt', 'r') as myfile:
            msg = myfile.read().replace('\n', '')

        os.remove('hide.txt')
        return msg


    def encode(self, clip, file_binary):
        frames = []
        [frames.append(frame) for frame in clip.iter_frames(dtype="uint8")]
        bits_left = len(file_binary)
        # UMMMMM LOL THIS A TAKE LOOOOONG!!!!!
        count = 0
        for i1, frame in enumerate(frames):
            for i2, pixels in enumerate(frame):
                for i3, pixel in enumerate(pixels):
                    frames[i1][i2][i3] = self.process_pixel(pixel, file_binary, count, bits_left)
                    count += 3
                    bits_left -= 3
                    if(bits_left <= 0):
                        return frames

    def hide(self, file_path, msg):
        clip = mpy.VideoFileClip(str(file_path))

        text_file = open("hide.txt", "w")
        text_file.write(msg)
        text_file.close()

        file = open('hide.txt', 'rb')
        filesize = os.path.getsize('hide.txt')
        file_header = os.path.basename('hide.txt') + "\0" + str(filesize) + "\0"
        file_binary = self.str_to_binary(file_header) + ''.join(self.file_to_binary(file))
        # file_binary = self.str_to_binary(str(msg))

        frames = self.encode(clip, file_binary)

        output = mpy.ImageSequenceClip(frames, fps=clip.fps)
        
        if output.write_videofile("output.avi", codec="png"):
            os.remove('hide.txt')
            return "Completed"
        else:
            return "Failed"
