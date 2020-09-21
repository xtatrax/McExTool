# -*- coding: utf-8 -*-

import traceback

class xorshift():
    def __init__(self):
        self.seedX = 123456789
        self.seedY = 362436069
        self.seedZ = 521288629
        self.seedW = 88675123
        return
    
    def setSeed(self, x=None,y=None,z=None,w=None):
        if x != None:
            self.seedX = x
        if y != None:
            self.seedY = y
        if z != None:
            self.seedZ = z
        if w != None:
            self.seedW = w
    
    def xor32(self):
        self.seedY = self.seedY ^ (self.seedY << 13 & 0xFFFFFFFF)
        self.seedY = self.seedY ^ (self.seedY >> 17 & 0xFFFFFFFF)
        self.seedY = self.seedY ^ (self.seedY << 5 & 0xFFFFFFFF)
        return self.seedY & 0xFFFFFFFF

    def xor128(self):
        t = self.seedX ^ (self.seedX << 11) & 0xFFFFFFFF
        self.seedX = self.seedY
        self.seedY = self.seedZ
        self.seedZ = self.seedW
        self.seedW = (self.seedW ^ (self.seedW >> 19)) ^ (t ^ (t >> 8)) & 0xFFFFFFFF
        return self.seedW
    
    # num = 32 or 128 / begin = 開始番号 / end = 終了番号
    def uniform(self, num=32, begin=0, end=1):
        try:
            if num == 32:
                rand = self.xor32
            elif num == 64:
                rand = self.xor128
            else:
                raise Exception
        except:
            traceback.print_exc()
        return begin+(rand())/(int(0xFFFFFFFF)/(end-begin))
