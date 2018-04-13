import wave
import numpy as np
import pyaudio
import binascii
import sys
import os
import shutil
from time import sleep

class SteganographyAudioException(Exception):
    pass

class StegAud():
	def __init__(self):
		pass

	def text2bin(self, text):
	    binary = ''.join(format(ord(x), 'b').zfill(8) for x in text)
	    return binary

	#turn binary to ASCII text
	def bin2text(self, bin):
	    a = int(bin, 2)
	    hex_string = '%x' % a
	    n = len(hex_string)
	    z = binascii.unhexlify(hex_string.zfill(n + (n & 1)))
	    text=z.decode('ascii')
	    return text

	def encode(self, audioFile, message):
	    wr = wave.open(str(audioFile), 'r')
	    # Set the parameters for the output file.
	    par = list(wr.getparams())
	    par[3] = 0  # The number of samples will be set by writeframes.
	    par = tuple(par)
	    newFilename = str(audioFile)[:-4] + "_encoded.wav"
	    ww = wave.open(newFilename, 'w')
	    ww.setparams(par)

	    fr = 20
	    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
	    # A larger number for fr means less reverb.
	    c = int(wr.getnframes()/sz)  # count of the whole file

	    binMessage = self.text2bin(str(message))

	    binLength = self.text2bin(str(len(binMessage)))

	    count = 0

	    #Check if audio file is long enough to encode message
	    if(c < len(binMessage) + 32):
	        print("Audio file not large enough for message")
	        exit()

	    #Encoding 0's to fill in the rest of the 32 bits that are for length
	    for i in range(32 - len(binLength)):
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        b = self.text2bin(str(da[0]))
	        b = b[:len(b) -1] + '0'
	        B = self.bin2text(b)
	        da[0] = int(B)
	        ww.writeframes(da.tostring())

	    #Encoding the length
	    for i in binLength:
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        b = self.text2bin(str(da[0]))
	        b = b[:len(b) -1] + i
	        B = self.bin2text(b)
	        da[0] = int(B)
	        ww.writeframes(da.tostring())

	    #Encoding the message
	    for i in binMessage:
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        b = self.text2bin(str(da[0]))
	        b = b[:len(b) -1] + i
	        B = self.bin2text(b)
	        da[0] = int(B)
	        ww.writeframes(da.tostring())
	    #Finishing the rest of the audio file
	    for i in range(c - 32 - len(binMessage)):
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        ww.writeframes(da.tostring())

	    wr.close()
	    ww.close()
	    filename = str(os.path.basename(str(audioFile)))
	    os.remove(str(audioFile))
	    shutil.move(newFilename, str(audioFile))

	def decode(self, audioFile):
	    wr = wave.open(str(audioFile), 'r')

	    fr = 20
	    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
	    c = int(wr.getnframes()/sz)  # count of the whole file

	    length = ""

	    #Get the length of the message
	    for i in range(32):
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        b = self.text2bin(str(da[0]))
	        length += b[-1:]

	    length = int(self.bin2text(length))

	    #Decode the message
	    message = ""
	    for i in range(length):
	        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
	        b = self.text2bin(str(da[0]))
	        message += b[-1:]

	    #Change message from binary to text
	    message = self.bin2text(message)
	    
	    wr.close()

	    return message;