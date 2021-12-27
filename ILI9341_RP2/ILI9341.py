# ILI9341 parallel driver by Hugh
# Largely inspired from the MCUFriend arduino library writen in c

from machine import Pin
from time import sleep_ms, sleep_us
from micropython import const
import gc

class screen:
    #------------------------------------
    # imported method (splitting files saves memory)
#     from ILI9341_method import table8_ads
    from ILI9341_char import SetFont,setTextCursor,setTextColor,drawchar, printh, prints, defil
#     gc.collect()
    #------------------------------------
    def __init__(self,LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7):
        # Pin definition
        self.WR_value = 1 << LCD_WR
        self.CS_value = 1 << LCD_CS
        self.CD_value = 1 << LCD_RS
        self.RD_value = 1 << LCD_RD
        self.RST_value = 1 << LCD_RST
        self.WR_off = self.WR_value ^ 0xFFFFFFF
        self.CS_off = self.CS_value ^ 0xFFFFFFF
        self.CD_off = self.CD_value ^ 0xFFFFFFF
        self.RD_off = self.RD_value ^ 0xFFFFFFF
        self.RST_off = self.RST_value ^ 0xFFFFFFF
     
        self.LCD_RD = LCD_RD
        self.LCD_WR = LCD_WR
        self.LCD_RS = LCD_RS # RS & CS pins must be ADC and OUTPUT
        self.LCD_CS = LCD_CS # for touch capability -> For ESP32 only pins 32 & 33 !
        self.LCD_RST = LCD_RST
        self.LCD_D0 = LCD_D0
        self.LCD_D1 = LCD_D1
        self.LCD_D2 = LCD_D2
        self.LCD_D3 = LCD_D3
        self.LCD_D4 = LCD_D4
        self.LCD_D5 = LCD_D5
        self.LCD_D6 = LCD_D6
        self.LCD_D7 = LCD_D7

        RD_PIN = Pin(LCD_RD, Pin.OUT)
        WR_PIN = Pin(LCD_WR, Pin.OUT)
        CD_PIN = Pin(LCD_RS, Pin.OUT)
        CS_PIN = Pin(LCD_CS, Pin.OUT)
        RESET_PIN = Pin(LCD_RST, Pin.OUT)

        D0_PIN = Pin(LCD_D0, Pin.OUT)
        D1_PIN = Pin(LCD_D1, Pin.OUT)
        D2_PIN = Pin(LCD_D2, Pin.OUT)
        D3_PIN = Pin(LCD_D3, Pin.OUT)
        D4_PIN = Pin(LCD_D4, Pin.OUT)
        D5_PIN = Pin(LCD_D5, Pin.OUT)
        D6_PIN = Pin(LCD_D6, Pin.OUT)
        D7_PIN = Pin(LCD_D7, Pin.OUT)


        self.GPIO_OUT_REG = const(0xD0000010)        #GPIO 0-31 output register
        self.GPIO_IN_REG= const(0xD0000004)          #GPIO 0-31 input register

        self.done_reset=0

        self.HEIGHT  =   320
        self.WIDTH   =   240

        
        self.D_MASK=self.mapF8(0xFF)
        self.D_MASK_off = self.D_MASK ^ 0xFFFFFFF
        self._MC = 0x2A
        self._MP = 0x2B
        self._MW = 0x2C
        self._SC = 0x2A
        self._EC = 0x2A
        self._SP = 0x2B
        self._EP = 0x2B
        self._SC_hi = self.mapF8((self._SC) >> 8)
        self._SC_lo = self.mapF8(self._SC)
        self._SP_hi = self.mapF8((self._SP) >> 8)
        self._SP_lo = self.mapF8(self._SP)
        self._MW_hi = self.mapF8((self._MW) >> 8)
        self._MW_lo = self.mapF8(self._MW)
        
    @micropython.viper
    def RD_ACTIVE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr8(self.RD_off))     #RD pin mask

    @micropython.viper
    def RD_IDLE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr8(self.RD_value))       

    @micropython.viper
    def WR_ACTIVE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr8(self.WR_off))     

    @micropython.viper
    def WR_IDLE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr8(self.WR_value))

    @micropython.viper
    def CD_COMMAND(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr8(self.CD_off))     

    @micropython.viper
    def CD_DATA(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr8(self.CD_value))

    @micropython.viper
    def CS_ACTIVE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr8(self.CS_off))    

    @micropython.viper
    def CS_IDLE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr8(self.CS_value))

    @micropython.viper
    def RESET_IDLE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr8(self.RST_value))

    @micropython.viper
    def RESET_ACTIVE(self):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr8(self.RST_off))      

    @micropython.viper
    def mapF8(self,d:int)->int:
        DATA_0 = int(ptr8(self.LCD_D0))
        DATA_1 = int(ptr8(self.LCD_D1))
        DATA_2 = int(ptr8(self.LCD_D2))
        DATA_3 = int(ptr8(self.LCD_D3))
        DATA_4 = int(ptr8(self.LCD_D4))
        DATA_5 = int(ptr8(self.LCD_D5))
        DATA_6 = int(ptr8(self.LCD_D6))
        DATA_7 = int(ptr8(self.LCD_D7))
        return (
        0
        | ((d & (1 << 0)) << (DATA_0 - 0))
        | ((d & (1 << 1)) << (DATA_1 - 1))
        | ((d & (1 << 2)) << (DATA_2 - 2))
        | ((d & (1 << 3)) << (DATA_3 - 3))
        | ((d & (1 << 4)) << (DATA_4 - 4))
        | ((d & (1 << 5)) << (DATA_5 - 5))
        | ((d & (1 << 6)) << (DATA_6 - 6))
        | ((d & (1 << 7)) << (DATA_7 - 7))
        )

#      
    @micropython.viper
    def write8(self,x:int):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = (GPIO_OUT[0] & int(ptr32(self.D_MASK_off))) | int(self.mapF8(x))
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr32(self.WR_off))
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr32(self.WR_value))
#     
    @micropython.viper
    def WriteCmd(self,x:int):
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & int(ptr32(self.CD_off))              #CD_COMMAND
        self.write8(x>>8)
        self.write8(x)
#         sleep_us(300) # PICO could need >300 us of temporisation in the command to respond for the readID() function
        GPIO_OUT[0] = GPIO_OUT[0] | int(ptr32(self.CD_value))            #CD pin on
# 
    def WriteCmdParamN(self,cmd, C_list):
        self.CS_ACTIVE()
        self.WriteCmd(cmd)
        for com in C_list:
            self.write8(com)
        self.CS_IDLE()
#
    def init_meth(self):
#        **********************Initialization sequence for ILI9341***********************************
        #             0xF6, 3, 0x01, 0x01, 0x00,  #Interface Control needs EXTC=1 MV_EOR=0, TM=0, RIM=0
        #             0xCF, 3, 0x00, 0x81, 0x30,  #Power Control B [00 81 30]
        #             0xED, 4, 0x64, 0x03, 0x12, 0x81,    #Power On Seq [55 01 23 01]
        #             0xE8, 3, 0x85, 0x10, 0x78,  #Driver Timing A [04 11 7A]
        #             0xCB, 5, 0x39, 0x2C, 0x00, 0x34, 0x02,      #Power Control A [39 2C 00 34 02]
        #             0xF7, 1, 0x20,      #Pump Ratio [10]
        #             0xEA, 2, 0x00, 0x00,        #Driver Timing B [66 00]
        #             0xB0, 1, 0x00,      #RGB Signal [00]
        #             0xB1, 2, 0x00, 0x1B,        #Frame Control [00 1B]
                               # do not uncomment ! 0xB6, 2, 0x0A, 0xA2, 0x27, #Display Function [0A 82 27 XX]    .kbv SS=1
        #             0xB4, 1, 0x00,      #Inversion Control [02] .kbv NLA=1, NLB=1, NLC=1
        #             0xC0, 1, 0x21,      #Power Control 1 [26]
        #             0xC1, 1, 0x11,      #Power Control 2 [00]
        #             0xC5, 2, 0x3F, 0x3C,        #VCOM 1 [31 3C]
        #             0xC7, 1, 0xB5,      #VCOM 2 [C0]
        #             0x36, 1, 0x48,      #Memory Access [00]
        #             0xF2, 1, 0x00,      #Enable 3G [02]
        #             0x26, 1, 0x01,      #Gamma Set [01]
        #             0xE0, 15, 0x0f, 0x26, 0x24, 0x0b, 0x0e, 0x09, 0x54, 0xa8, 0x46, 0x0c, 0x17, 0x09, 0x0f, 0x07, 0x00,
        #             0xE1, 15, 0x00, 0x19, 0x1b, 0x04, 0x10, 0x07, 0x2a, 0x47, 0x39, 0x03, 0x06, 0x06, 0x30, 0x38, 0x0f,
        init_seq=[0xF6, 3, 0x01, 0x01, 0x00,0xCF, 3, 0x00, 0x81, 0x30,0xED, 4, 0x64, 0x03, 0x12, 0x81,0xE8, 3, 0x85, 0x10, 0x78,\
                  0xCB, 5, 0x39, 0x2C, 0x00, 0x34, 0x02,0xF7, 1, 0x20,0xEA, 2, 0x00, 0x00,0xB0, 1, 0x00,0xB1, 2, 0x00, 0x1B,0xB4,\
                  1, 0x00,0xC0, 1, 0x21,0xC1, 1, 0x11,0xC5, 2, 0x3F, 0x3C,0xC7, 1, 0xB5,0x36, 1, 0x48,\
                  0xF2, 1, 0x00,0x26, 1, 0x01,0xE0, 15, 0x0f, 0x26, 0x24, 0x0b, 0x0e, 0x09, 0x54, 0xa8, 0x46, 0x0c, 0x17, 0x09,\
                  0x0f, 0x07, 0x00,0xE1, 15, 0x00, 0x19, 0x1b, 0x04, 0x10, 0x07, 0x2a, 0x47, 0x39, 0x03, 0x06, 0x06, 0x30, 0x38, 0x0f]
        i=0
        while i < len(init_seq):
            self.CS_ACTIVE()
            self.CD_COMMAND()
            self.write8(init_seq[i])
            n1 = i+2
            n2 = n1+init_seq[i+1]
            for k in init_seq[n1:n2]:
                self.CD_DATA()
                self.write8(k)
            self.CS_IDLE()
            i=n2

#
    @micropython.viper
    def setAddrWindow(self,x1:int,y1:int,x2:int,y2:int):
        CS_value = 1 << int(ptr8(self.LCD_CS))
        CS_off = CS_value ^ int(0xFFFFFFF)
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS active
        self.WriteCmd(self._SC)
        #write8F(x1_hi)
        self.write8(x1>>8)    #data bits sent to data pins
        #write8F(x1_lo)
        self.write8(x1)    #data bits sent to data pins
        #write8F(x2_hi)
        self.write8(x2>>8)    #data bits sent to data pins
        #write8F(x2_lo)
        self.write8(x2)    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] | CS_value             #CS_IDLE
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS_ACTIVE
        self.WriteCmd(self._SP)
        #write8F(y1_hi)
        self.write8(y1>>8)    #data bits sent to data pins
        #write8F(y1_lo)
        self.write8(y1)    #data bits sent to data pins
        #write8F(y2_hi)
        self.write8(y2>>8)    #data bits sent to data pins
        #write8F(y2_lo)
        self.write8(y2)    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] | CS_value            #CS_IDLE
# 
    def READ_8(self):
        self.RD_IDLE()
        self.RD_ACTIVE()
        #READ_DELAY2()
        dst = self.read_8()
        self.RD_IDLE()
        return dst
# 
    def read16bits(self):
        sleep_us(1)    #1us should be adequate
        ret=self.READ_8()
#         print("READ_8 ret val:"+str(hex(ret)))
        #all MIPI_DCS_REV1 style params are 8-bit
        sleep_us(1)    #1us should be adequate
        lo=self.READ_8()
#         print("READ_8 lo val:"+str(hex(lo)))
        return (ret << 8) | lo
# 
    def readReg(self,reg,index):
         if not self.done_reset:
            self.reset()
         self.CS_ACTIVE()
         self.WriteCmd(reg)
         sleep_us(1)        #1us should be adequate
         while index >= 0:
             ret=self.read16bits()
#              print("index=",index,"\tread16=",hex(ret))
             index-=1
         self.RD_IDLE()
         self.CS_IDLE()
         return ret
# 
    def readReg32(self,reg):
        h = self.readReg(reg, 0)
#         print(hex(h))
        l = self.readReg(reg, 1)
#         print(hex(l))
#         return l
        return (h << 16) | (l)
#         return readReg(reg, 1)
# 
    @micropython.viper
    def read_8(self)->int:
        DATA_0 = int(ptr8(self.LCD_D0))
        DATA_1 = int(ptr8(self.LCD_D1))
        DATA_2 = int(ptr8(self.LCD_D2))
        DATA_3 = int(ptr8(self.LCD_D3))
        DATA_4 = int(ptr8(self.LCD_D4))
        DATA_5 = int(ptr8(self.LCD_D5))
        DATA_6 = int(ptr8(self.LCD_D6))
        DATA_7 = int(ptr8(self.LCD_D7))
        d = (ptr32(self.GPIO_IN_REG))
        return (
            0
            | ((d[0] & (1 << DATA_0)) >> (DATA_0 - 0))
            | ((d[0] & (1 << DATA_1)) >> (DATA_1 - 1))
            | ((d[0] & (1 << DATA_2)) >> (DATA_2 - 2))
            | ((d[0] & (1 << DATA_3)) >> (DATA_3 - 3))
            | ((d[0] & (1 << DATA_4)) >> (DATA_4 - 4))
            | ((d[0] & (1 << DATA_5)) >> (DATA_5 - 5))
            | ((d[0] & (1 << DATA_6)) >> (DATA_6 - 6))
            | ((d[0] & (1 << DATA_7)) >> (DATA_7 - 7))
        )
# 
    def readID(self):
        ret = self.readReg32(0xD3)      #for ILI9488, 9486, 9340, 9341
#         print(hex(ret))
        if (ret == 0x9341):
            return hex(ret)
        else:
            return 0
# 
    def begin(self):
        self.reset()
        self.reset_off()
        self.init_meth()
        self.wake_on()
        self.setrotation(0)
        self.invertDisplay(False)
        sleep_ms(50) # wait for full initialisation

    def reset(self):
        self.CS_IDLE()
        self.RD_IDLE()
        self.WR_IDLE()
        self.RESET_IDLE()
        self.RESET_ACTIVE()
        self.RESET_IDLE()
        self.done_reset=True

    def reset_off(self):
        self.CS_ACTIVE()
        self.CD_COMMAND()
        self.write8(0x01)
        self.CS_IDLE()
        self.CS_ACTIVE()
        self.CD_COMMAND()
        self.write8(0x28)
        self.CS_IDLE()
        self.CS_ACTIVE()
        self.CD_COMMAND()
        self.write8(0x3A)
        self.CD_DATA()
        self.write8(0x55)
        self.CS_IDLE()

    def wake_on(self):
        self.CS_ACTIVE()
        self.CD_COMMAND()
        self.write8(0x11)
        self.CS_IDLE()
        self.CS_ACTIVE()
        self.CD_COMMAND()
        self.write8(0x29)
        self.CS_IDLE()
# 
    def vertScroll(self,top, scrollines, offset):
        bfa = self.HEIGHT - top - scrollines #bottom fixed area
        sea = top
        if (offset <= -scrollines or offset >= scrollines):     #valid scroll
           offset = 0
        vsp = top + offset  #vertical start position
        if (offset < 0):
            vsp += scrollines       #keep in unsigned range
        sea = top + scrollines - 1
        d0 = top >> 8         #TFA
        d1 = top
        d2 = scrollines >> 8  #VSA
        d3 = scrollines
        d4 = bfa >> 8         #BFA
        d5 = bfa
        self.WriteCmdParamN(0x33, [d0,d1,d2,d3,d4,d5])
        d0 = vsp >> 8         #VSP
        d1 = vsp
        self.WriteCmdParamN(0x37, [d0,d1])
        if (offset == 0):
            self.WriteCmdParamN(0x13, [])   #NORMAL i.e. disable scroll

    def setrotation(self,r):
        #global _width, _height
        rotation = r & 3
        if (rotation==0 or rotation==2):
            self._width=self.WIDTH
            self._height=self.HEIGHT
        else:
            self._width=self.HEIGHT
            self._height=self.WIDTH
        if (r==0):          #PORTRAIT:
            val=0x48        #MY=0, MX=1, MV=0, ML=0, BGR=1
        elif (r==1):        #LANDSCAPE: 90 degrees
            val=0x28        #MY=0, MX=0, MV=1, ML=0, BGR=1
        elif (r==2):        #PORTRAIT_REV: 180 degrees
            val=0x98        #MY=1, MX=0, MV=0, ML=1, BGR=1
        elif (r==3):        #LANDSCAPE_REV: 270 degrees
            val=0xF8        #MY=1, MX=1, MV=1, ML=1, BGR=1
        else:
            val=0x48
        self.RD_IDLE()
        self.WriteCmdParamN(0x36, [val])
    #     print("Width:",_width,"   Height:",_height)
        self.setAddrWindow(0, 0, self._width - 1, self._height - 1)
        self.vertScroll(0, self.HEIGHT, 0)   #reset scrolling after a rotation
# 
    def invertDisplay(self,i):
        if i :
            self.WriteCmdParamN(0x21, [])
        else :
            self.WriteCmdParamN(0x20, [])
# 
# 
    def fillscreen(self,color):
        self.fillRect(0, 0, self._width, self._height, color)

    def fillRect(self,x, y, w, h, color):
        if (w < 0):
            w = -w
            x -= w
        end = x + w
        if (x < 0):x=0
        if (end > self._width):end = self._width
        w = end - x
        if (h < 0):
            h = -h
            y -= h
        end = y + h
        if (y < 0):y = 0
        if (end > self._height):end = self._height
        h = end - y
        self.setAddrWindow(x, y, x + w - 1, y + h - 1)
        self.CS_ACTIVE()
        self.WriteCmd(self._MW)
        if (h > w):
            end = h
            h = w
            w = end
        self.balayage(h,end,w,color) # here needs viper code to refresh all lines fast
        self.CS_IDLE()
# 
    @micropython.viper
    def balayage(self,h:int,end:int,w:int,color:int):
        WR_value = int(ptr8(self.WR_value))
        WR_off = int(ptr8(self.WR_off))
        D_MASK_off = int(ptr8(self.D_MASK_off))
        color_hi= int(self.mapF8(color>>8))
        color_lo= int(self.mapF8(color))
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        while (h>0):
            end = w
            while(end!=0):
                GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | color_hi    #data bits sent to data pins
                GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
                GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
                GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | color_lo    #data bits sent to data pins
                GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
                GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
                end-=1
            h-=1
# 
# 
    def drawFastVLine(self,x, y, h, color):
        if (x < 0 or y < 0 or x >= self._width or y >= self._height):
            return
        self.fillRect(x, y, 1, h, color)

    def drawFastHLine(self,x, y, w, color):
        if (x < 0 or y < 0 or x >= self._width or y >= self._height):
            return
        self.fillRect(x, y, w, 1, color)

    def drawLine(self,x1, y1, x2, y2, color):
        if (x1 < 0 or y1 < 0 or x1 >= self._width or y1 >= self._height or x2 < 0 or y2 < 0 or x2 >= self._width or y2 >= self._height):
            return
        if (x1>x2):
            x1,x2=x2,x1
            y1,y2=y2,y1
        if (x1==x2 and y1==y2):
            self.drawPixel(x1,x2,color)
        if (x1==x2):
            self.drawFastVLine(x1,y1,y2-y1,color)
        if (y1==y2):
            self.drawFastHLine(x1,y1,x2-x1,color)
        else:
            a=(y2-y1)/(x2-x1)
            for i in range(x1,x2,1):
                self.drawPixel(i, int(a*i)+y1, color)
        self.CS_IDLE()

    @micropython.viper
    def drawCircle(self,x:int, y:int, r:int , color:int):
        Wlimit = int(ptr16(self._width))
        Hlimit = int(ptr16(self._height))
        if (x < 0 or y < 0 or x >= Wlimit or y >= Hlimit):
            return
        # Bresenham algorithm
        x_pos = 0-r
        y_pos = 0
        err = 2 - 2 * r
        while 1:
            self.drawPixel(x-x_pos, y+y_pos,color)
            self.drawPixel(x-x_pos, y-y_pos,color)
            self.drawPixel(x+x_pos, y+y_pos,color)
            self.drawPixel(x+x_pos, y-y_pos,color)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if((0-x_pos) == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break
        self.CS_IDLE()


    @micropython.viper
    def drawDisk(self,x:int, y:int, r1:int ,r2:int, color:int):
        Wlimit = int(ptr16(self._width))
        Hlimit = int(ptr16(self._height))
        if (x < 0 or y < 0 or x >= Wlimit or y >= Hlimit):
            return
        for r in range(r1,r2):
            # Bresenham algorithm
            x_pos = 0-r
            y_pos = 0
            err = 2 - 2 * r
            while 1:
                self.drawPixel(x-x_pos, y+y_pos, color)
                self.drawPixel(x+x_pos, y+y_pos, color)
                self.drawPixel(x+x_pos, y-y_pos, color)
                self.drawPixel(x-x_pos, y-y_pos, color)
                e2 = err
                if (e2 <= y_pos):
                    y_pos += 1
                    err += y_pos * 2 + 1
                    if(0-x_pos == y_pos and e2 <= x_pos):
                        e2 = 0
                if (e2 > x_pos):
                    x_pos += 1
                    err += x_pos * 2 + 1
                if x_pos > 0:
                    break
        self.CS_IDLE()

    @micropython.viper
    def fillDisk(self,x:int, y:int, r:int, color:int):
        Wlimit = int(ptr16(self._width))
        Hlimit = int(ptr16(self._height))
        xmin = (x - r)
        xmax = (x + r)
        ymin = (y - r)
        ymax = (y + r)
        if (xmin < 0): xmin = 0
        if (xmax >= Wlimit): xmax = Wlimit - 1
        if (ymin < 0): ymin = 0
        if (ymax >= Hlimit): ymax = Hlimit - 1
        r2 = r * r
        for j in range(ymin,ymax,1):
            dy2 = (y - j) * (y - j)
            for i in range(xmin,xmax,1):
                dx2 = (x - i) * (x - i)
                if (dx2 + dy2 <= r2):
                    self.drawPixel(i,j,color)

    @micropython.viper
    def Print_Binary_Values(num:int): 
        # base condition
        if(num > 1):
            Print_Binary_Values(num // 2)
        print(str(num % 2)+"   ", end="")
        
    @micropython.viper
    def Display_Pin_State(gpio:int):
        gpio = gpio | 0x10000000
        print("28  CS  CD  25  24  23  22  21  20  19  18  17  16  15  14  13  12  11 RST  WR  RD  D7  D6  D5  D4  D3  D2  D1  D0\n")
        Print_Binary_Values(gpio)
        print("\n")
        
    @micropython.viper
    def drawPixel(self,x:int,y:int,color:int):
        DATA_0 = int(ptr8(self.LCD_D0))
        DATA_1 = int(ptr8(self.LCD_D1))
        DATA_2 = int(ptr8(self.LCD_D2))
        DATA_3 = int(ptr8(self.LCD_D3))
        DATA_4 = int(ptr8(self.LCD_D4))
        DATA_5 = int(ptr8(self.LCD_D5))
        DATA_6 = int(ptr8(self.LCD_D6))
        DATA_7 = int(ptr8(self.LCD_D7))
        WR_value = 1 << int(ptr8(self.LCD_WR))
        CD_value = 1 << int(ptr8(self.LCD_RS))
        CS_value = 1 << int(ptr8(self.LCD_CS))
        WR_off = WR_value ^ int(0xFFFFFFF)
        CD_off = CD_value ^ int(0xFFFFFFF)
        CS_off = CS_value ^ int(0xFFFFFFF)
        _SC_h = int(ptr32(self._SC_hi))
        _SC_l = int(ptr32(self._SC_lo))
        _SP_h = int(ptr32(self._SP_hi))
        _SP_l = int(ptr32(self._SP_lo))
        _MW_h = int(ptr32(self._MW_hi))
        _MW_l = int(ptr32(self._MW_lo))
        D_MASK=(
            0
            | (((0xFF) & (1 << 0)) << (DATA_0 - 0))
            | (((0xFF) & (1 << 1)) << (DATA_1 - 1))
            | (((0xFF) & (1 << 2)) << (DATA_2 - 2))
            | (((0xFF) & (1 << 3)) << (DATA_3 - 3))
            | (((0xFF) & (1 << 4)) << (DATA_4 - 4))
            | (((0xFF) & (1 << 5)) << (DATA_5 - 5))
            | (((0xFF) & (1 << 6)) << (DATA_6 - 6))
            | (((0xFF) & (1 << 7)) << (DATA_7 - 7))
        )
        D_MASK_off = D_MASK ^ int(0xFFFFFFF)
        x_hi= (
            0
            | (((x>>8) & (1 << 0)) << (DATA_0 - 0))
            | (((x>>8) & (1 << 1)) << (DATA_1 - 1))
            | (((x>>8) & (1 << 2)) << (DATA_2 - 2))
            | (((x>>8) & (1 << 3)) << (DATA_3 - 3))
            | (((x>>8) & (1 << 4)) << (DATA_4 - 4))
            | (((x>>8) & (1 << 5)) << (DATA_5 - 5))
            | (((x>>8) & (1 << 6)) << (DATA_6 - 6))
            | (((x>>8) & (1 << 7)) << (DATA_7 - 7))
        )
        x_lo = (
            0
            | ((x & (1 << 0)) << (DATA_0 - 0))
            | ((x & (1 << 1)) << (DATA_1 - 1))
            | ((x & (1 << 2)) << (DATA_2 - 2))
            | ((x & (1 << 3)) << (DATA_3 - 3))
            | ((x & (1 << 4)) << (DATA_4 - 4))
            | ((x & (1 << 5)) << (DATA_5 - 5))
            | ((x & (1 << 6)) << (DATA_6 - 6))
            | ((x & (1 << 7)) << (DATA_7 - 7))
        )
        y_hi= (
            0
            | (((y>>8) & (1 << 0)) << (DATA_0 - 0))
            | (((y>>8) & (1 << 1)) << (DATA_1 - 1))
            | (((y>>8) & (1 << 2)) << (DATA_2 - 2))
            | (((y>>8) & (1 << 3)) << (DATA_3 - 3))
            | (((y>>8) & (1 << 4)) << (DATA_4 - 4))
            | (((y>>8) & (1 << 5)) << (DATA_5 - 5))
            | (((y>>8) & (1 << 6)) << (DATA_6 - 6))
            | (((y>>8) & (1 << 7)) << (DATA_7 - 7))
        )
        y_lo = (
            0
            | ((y & (1 << 0)) << (DATA_0 - 0))
            | ((y & (1 << 1)) << (DATA_1 - 1))
            | ((y & (1 << 2)) << (DATA_2 - 2))
            | ((y & (1 << 3)) << (DATA_3 - 3))
            | ((y & (1 << 4)) << (DATA_4 - 4))
            | ((y & (1 << 5)) << (DATA_5 - 5))
            | ((y & (1 << 6)) << (DATA_6 - 6))
            | ((y & (1 << 7)) << (DATA_7 - 7))
        )
        color_hi= (
            0
            | (((color>>8) & (1 << 0)) << (DATA_0 - 0))
            | (((color>>8) & (1 << 1)) << (DATA_1 - 1))
            | (((color>>8) & (1 << 2)) << (DATA_2 - 2))
            | (((color>>8) & (1 << 3)) << (DATA_3 - 3))
            | (((color>>8) & (1 << 4)) << (DATA_4 - 4))
            | (((color>>8) & (1 << 5)) << (DATA_5 - 5))
            | (((color>>8) & (1 << 6)) << (DATA_6 - 6))
            | (((color>>8) & (1 << 7)) << (DATA_7 - 7))
        )
        color_lo = (
            0
            | ((color & (1 << 0)) << (DATA_0 - 0))
            | ((color & (1 << 1)) << (DATA_1 - 1))
            | ((color & (1 << 2)) << (DATA_2 - 2))
            | ((color & (1 << 3)) << (DATA_3 - 3))
            | ((color & (1 << 4)) << (DATA_4 - 4))
            | ((color & (1 << 5)) << (DATA_5 - 5))
            | ((color & (1 << 6)) << (DATA_6 - 6))
            | ((color & (1 << 7)) << (DATA_7 - 7))
        )
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS active
        #CD _COMMAND
        GPIO_OUT[0] = GPIO_OUT[0] & CD_off              #CD_COMMAND
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SC_h    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SC_l    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        #CD_DATA
        GPIO_OUT[0] = GPIO_OUT[0] | CD_value            #CD pin on
        #write8F(x_hi)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | x_hi    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(x_lo)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | x_lo    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(x_hi)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | x_hi    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(x_lo)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | x_lo    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = GPIO_OUT[0] | CS_value            #CS_IDLE
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS_ACTIVE
        #CD _COMMAND
        GPIO_OUT[0] = GPIO_OUT[0] & CD_off              #CD_COMMAND

        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SP_h    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SP_l    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        #CD_DATA
        GPIO_OUT[0] = GPIO_OUT[0] | CD_value            #CD pin on
        #write8F(y_hi)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | y_hi    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(y_lo)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | y_lo    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(y_hi)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | y_hi    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(y_lo)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | y_lo    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = GPIO_OUT[0] | CS_value            #CS_IDLE
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS_ACTIVE
        #CD _COMMAND
        GPIO_OUT[0] = GPIO_OUT[0] & CD_off              #CD_COMMAND

        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _MW_h    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _MW_l    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)


        #CD_DATA
        GPIO_OUT[0] = GPIO_OUT[0] | CD_value            #CD pin on
        #write8F(color_hi)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | color_hi    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        #write8F(color_lo)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | color_lo    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)

        GPIO_OUT[0] = GPIO_OUT[0] | CS_value            #CS_IDLE
