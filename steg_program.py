import sys
import argparse
from os import path
from PIL import Image
import numpy as np


#
class LSBprog():
    def __init__(self, cover_object):
        self.cover = Image.open(cover_object,'r')
        self.width, self.height = self.cover.size
        self.channels = self.get_channels()
        self.array = np.array(list(self.cover.getdata()))
        self.capacity = self.channels * self.height * self.width

    def change_last_bit(self,byte):
        return byte ^ 1

    def get_channels(self):
        if self.cover.mode == 'RGB':
            return 3         
        elif self.cover.mode == 'RGBA':
            return 4
        elif self.cover.mode == ('P' or 'L' or 'PA' or 'LA'):
            print("Cover is an indexed image with a color palette\n Do you wish to convert it to RGB?\n")
            if input("y/n: ").lower() == 'y':
                self.cover=self.cover.convert("RGB")
                return 3
            else:
                exit()
        else:
            print("Unsupported image type")
            exit()
    def get_capacity(self):
        msg = f"""
            You can hide up to {self.capacity} bits in the cover object\n
            B ~ {self.capacity/8}
            KB ~ {self.capacity/(8*1024)}
            MB ~ {self.capacity/(8*1024*1024)}
            """
        return msg
    
    def get_ext_code(self,ext,reverse=False):
        ext_dict = {
            'jpg':'0000',
            'png':'0001',
            'msg':'0010',
            'mp3':'0100',
            'pdf':'0101'
            
        }
        if not reverse:
            return ext_dict[ext]
        else:
            for key,value in ext_dict.items():
                if value == ext:
                    return key

    def convert_to_bytestring(self,data):

        hidden_data = bytes([int(data[i:i+8], 2) for i in range(0, len(data), 8)])
        return hidden_data
        

    def decode(self):
        hidden_obj_header = ""
        hidden_obj = ""
        bit_length = -1
        i = 0
        write_obj = False
        for pixel in self.array:
            for channel in pixel:
                if i == 32: 
                    file_format = self.get_ext_code(hidden_obj_header[:4],True)
                    bit_length = int(hidden_obj_header[4:32],2)
                    write_obj = True

                if not write_obj: # ak spracovavame header
                    hidden_obj_header += bin(channel%2)[2:]
                
                if write_obj: # ak uz spracovavame tajnu spravu
                    if i == 32 + bit_length:
                        hidden_data = self.convert_to_bytestring(hidden_obj)
                        if file_format == 'msg': # skryté správy sa vypíšu do konzoly
                            print(f"the hidden message is: {hidden_data.decode('utf-8')}")
                        else:
                            
                            uncovered_obj = open(f"uncovered.{file_format}","wb")
                            uncovered_obj.write(hidden_data)
                            print("the hidden file was recovered\n")
                            return
                    hidden_obj += bin(channel%2)[2:]

                
                
                i += 1
                
            
     
        



    def encode(self,data, data_type):
        
        if data_type == 'msg':
            hidden_obj = data.encode('utf8')        # encode the message
            ext_code = self.get_ext_code('msg')     # there is no extension in a message, but we need to define a virtual one

        elif data_type == 'img':
            f_type = data.split(".")[1]             # get the extension
            ext_code = self.get_ext_code(f_type)    # get the extension code
            hidden_obj = open(data,'rb').read()     # open the image as a binary string
        size = len(hidden_obj)*8
        if size > self.capacity:
            print("File does not fit into the capacity of the cover object")
            return
        if len(bin(size)) - 2 > 28:
            print("File is too large for the header. Maximum of 32mb images are supported")
            return


        hidden_obj_metadata = ext_code +  ('{0:028b}'.format(len(hidden_obj)*8)) #build the header, first 1 bit (message,image), 3 bit (extension), 28 bit (number of bits hidden)
        object_bits = ''.join(format(byte, '08b') for byte in hidden_obj)
        object_bits = hidden_obj_metadata + object_bits
        
        
        i = 0
        for pixel in self.array:
            for j in range(0,self.channels):
                try:
                    if pixel[j]%2 != int(object_bits[i]):
                        pixel[j]=self.change_last_bit(pixel[j])
                    i+=1
                except IndexError: #pls dont kill me
                    self.array=self.array.reshape(self.height, self.width, self.channels)
                    enc_img = Image.fromarray(self.array.astype('uint8'), self.cover.mode)
                    enc_img.save("stego_object.png")
                    print("The hidden data was inserted into the cover object to file: stego_object.png")



                    return

                

        
    
        



def args_verify(args):


    # verify that the cover object does exist and what format it is saved in
    if not path.isfile(args.cover):
        print(f"Cover object {args.cover} does not exist")
        exit()
    else:
        cover_name,cover_ext =args.cover.split(".")
        if cover_ext.lower() not in ['png','tiff','bmp']:
            print("Cover file extension is not a lossless format. The output file will have the extension '.PNG'")
    
    if args.file != None:
        if not path.isfile(args.file):
            print(f"File {args.cover} does not exist")
            exit()


    





if __name__ == '__main__':
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(
                    description="A simple program to hide and unhide secret message/file in a lossless cover object",
                    epilog="Pavol Krajkovic, FIIT STU in Bratislava, Forensic Analysis of Computer Systems")
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-c","--cover", type=str, help="the cover object inside which we hide the hidden message\n",required=True)
    group.add_argument("--capacity",action="store_true", help="show the available space in the cover object that can be used to hide the file")
    group.add_argument("--decode", action="store_true",help="option if we want to decode a stego object")
    group.add_argument("-f","--file", type=str, help="the secret image, that is to be hidden in the cover file\n")
    group.add_argument("-m","--message",type=str,help="message we want to hide inside the cover object\n")
    args = parser.parse_args()


 

    src = LSBprog(args.cover)
    if args.decode:
        src.decode()

    if args.message: 

        src.encode(args.message,'msg')
    if args.file:
        src.encode(args.file,'img')
    if args.capacity == True:
        print(src.get_capacity())



    
   



        
