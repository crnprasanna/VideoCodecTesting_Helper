#!/usr/bin/python

'''
    Script to convert Raw input 8bit YUV nv12 format to I420 and vice versa
    I420 yuv : https://www.fourcc.org/pixel-format/yuv-i420/
    nv12 yuv : https://www.fourcc.org/pixel-format/yuv-nv12/
'''

import numpy as np
import sys
import os


class input_yuv:
    # Initialise and create a class for handling input yuv
    def __init__(self, inpath, width, height):

        subsample = 1.5
        bpp = 8
        self.file = inpath
        self.width, self.height = width, height

        if os.path.exists(inpath) == False:
            sys.exit("Input file does not exists : " + inpath)
        self.filesize = os.path.getsize(inpath)
        self.framesize = ((((width * height) * subsample) / 8) * bpp)
        self.frames = int(self.filesize / self.framesize)


    def read_I420frame(self, frame):

        Ystart = int(self.framesize * frame)
        Y_size = self.width * self.height
        Cb_size = Cr_Size = Y_size / 4
        Yend = Ystart + Y_size

        with open(self.file, "rb") as finput:
            finput.seek(Ystart)
            Y = finput.read(Yend - Ystart)

        Cb_start = Yend
        Cb_end = Cb_start + Cb_size
        with open(self.file, "rb") as finput:
            finput.seek(Cb_start)
            Cb = finput.read((int)(Cb_end - Cb_start))

        Cr_start = Cb_end
        Cr_end = Cr_start + Cr_Size
        with open(self.file, "rb") as finput:
            finput.seek((int)(Cr_start))
            Cr = finput.read((int)(Cr_end - Cr_start))

        return Y, Cb, Cr

    def read_NV12frame(self, frame):

        Ystart = int(self.framesize * frame)
        Y_size = self.width * self.height
        Chroma_size = Y_size / 2
        Yend = Ystart + Y_size
        with open(self.file, "rb") as finput:
            finput.seek(Ystart)
            Y = finput.read(Yend - Ystart)

        Chroma_start = Yend
        Chroma_end = Chroma_start + Chroma_size
        with open(self.file, "rb") as finput:
            finput.seek(Chroma_start)
            Chroma = finput.read(int(Chroma_end - Chroma_start))

        return Y, Chroma


class output_yuv:

    def __init__(self,outpath,width,height):

        subsample = 1.5
        bpp = 8
        self.framesize = ((((width * height) * subsample) /8) * bpp)
        self.width,self.height = width,height
        self.file=open(outpath,"wb")
        self.startpos = 0

    def write_NV12frame(self,luma_arr,Cb_arr,Cr_arr,frame):

        FrameStart = int(frame * self.framesize)
        self.file.write(luma_arr)

        Cb_seek = FrameStart + (self.width * self.height)
        self.file.seek(Cb_seek)

        #self.file.write(Cb_arr)
        #self.file.seek(Cb_seek + ((self.width/2) * (self.height/2)))
        #self.file.write(Cr_arr)
        nCb = np.fromstring(Cb_arr, dtype='uint8')
        nCr = np.fromstring(Cr_arr, dtype='uint8')
        nCbCr = np.array([nCb, nCr])
        nChroma = nCbCr.reshape(-1, order='F')

        nChroma.tofile(self.file, "", format('uint8'))


    def write_I420frame(self,luma_arr,CbCr_arr,frame):

        FrameStart = int(frame * self.framesize)
        self.file.write(luma_arr)

        CbCr_seek = FrameStart + (self.width * self.height)
        size = (int)((self.width * self.height) / 4)
        self.file.seek(CbCr_seek)

        nCbCr = np.fromstring(CbCr_arr, dtype='uint8')
        nChroma = nCbCr.reshape(2,size, order='F')
        Cb = nChroma[0]
        Cr = nChroma[1]

        Cb.tofile(self.file, "", format('uint8'))
        self.file.seek((int)(CbCr_seek + size))
        Cr.tofile(self.file, "", format('uint8'))


if len(sys.argv) != 5:
   print("\nScript used to convert YUV 420 8bit I420 to NV12 and Vice versa")
   print("Usage : python convertYUV420p.py Input_YUV Width Height Mode\n")
   print("Mode: 1 - NV12 to I420, 0 - I420 to NV12\n")
   print("Ex (NV12 to I420): python convertNV12toPlanar.py tulips_176x144_420p_nv12.yuv 176 144 1\n")
   print("Ex (I420 to NV12): python convertNV12toPlanar.py tulips_176x144_420p.yuv 176 144 0\n")
   print("Your Input : {0}, nArgs : {1}" .format(sys.argv, len(sys.argv)))
   exit(-1)

fin = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])
mode = int(sys.argv[4])
out = "out_" + fin
if mode == 1:
    print("\nConversion Started : NV12 to I420\n")
    fout = out.replace(".yuv", "_toI420.yuv")
else:
    print("\nConversion Started : I420 to NV12\n")
    fout = out.replace(".yuv", "_toNV12.yuv")

# Initialise YUV class
yuv_in = input_yuv(fin,width,height)
yuv_out = output_yuv(fout,width,height)

for frame in range(yuv_in.frames):
    if frame == int(yuv_in.frames*0.25):
        print("Completed 25%....\n")
    elif frame == int(yuv_in.frames*0.50):
        print("Completed 50%....\n")
    elif frame == int(yuv_in.frames*0.75):
        print("Completed 75%....\n")

    if mode == 1:
        # Read nv12 input frame
        Y,CbCr = yuv_in.read_NV12frame(frame)

        # Convert and write to output file
        yuv_out.write_I420frame(Y,CbCr,frame)
    else:
        # Read I420 input frame
        Y, Cb, Cr = yuv_in.read_I420frame(frame)

        # Convert and write to output file
        yuv_out.write_NV12frame(Y,Cb,Cr,frame)

print("Task Completed - Output file saved at {0}\n" .format(fout))
