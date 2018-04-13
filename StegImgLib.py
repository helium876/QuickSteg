#!/usr/bin/env python

from PIL import Image
import binascii

class SteganographyImageException(Exception):
    pass

class StegImg():
    def __init__(self):
        pass

    def rgb2hex(self, r, g, b):
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def hex2rgb(self, hexcode):
        return tuple(map(ord, hexcode[1:].decode('hex')))

    def str2bin(self, message):
        binary = bin(int(binascii.hexlify(message), 16))
        return binary[2:]

    def bin2str(self, binary):
        message = binascii.unhexlify('%x' % (int('0b'+binary,2)))
        return message

    def encode(self, hexcode, digit):
        if hexcode[-1] in ('0','1', '2', '3', '4', '5'):
            hexcode = hexcode[:-1] + digit
            return hexcode
        else:
            return None

    def decode(self, hexcode):
        if hexcode[-1] in ('0', '1'):
            return hexcode[-1]
        else:
            return None

    def hide(self, filename, message):
        img = Image.open(str(filename))
        binary = self.str2bin(message) + '1111111111111110'
        if img.mode in ('RGBA'):
            img = img.convert('RGBA')
            datas = img.getdata()
            
            newData = []
            digit = 0
            temp = ''
            for item in datas:
                if (digit < len(binary)):
                    newpix = self.encode(self.rgb2hex(item[0],item[1],item[2]),binary[digit])
                    if newpix == None:
                        newData.append(item)
                    else:
                        r, g, b = self.hex2rgb(newpix)
                        newData.append((r,g,b,255))
                        digit += 1
                else:
                    newData.append(item)    
            img.putdata(newData)
            img.save(str(filename), "PNG")
            return "Completed!"    
        return "Incorrect Image Mode, Couldn't Hide"

    def retr(self, filename):
        img = Image.open(str(filename))
        binary = ''

        if img.mode in ('RGBA'): 
            img = img.convert('RGBA')
            datas = img.getdata()
            
            for item in datas:
                digit = self.decode(self.rgb2hex(item[0],item[1],item[2]))
                if digit == None:
                    pass
                else:
                    binary = binary + digit
                    if (binary[-16:] == '1111111111111110'):
                        print "Success"
                        return self.bin2str(binary[:-16])

            return self.bin2str(binary)
        return "Incorrect Image Mode, Couldn't Retrieve"