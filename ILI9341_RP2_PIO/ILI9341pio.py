# ILI9341 parallel driver by Hugh
# Largely inspired from the MCUFriend arduino library writen in c

from machine import Pin
from time import sleep_ms, sleep_us, ticks_ms
from rp2 import PIO, StateMachine, asm_pio
from micropython import const
import gc

class screen:
    #------------------------------------
    # imported method (splitting files saves memory)
#     from ILI9341_method import table8_ads
    from ILI9341_char import SetFont,setTextCursor,setTextColor,drawchar, printh, prints, defil
#     gc.collect()
    #------------------------------------
    def __init__(self,LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0):
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
        
        self.LCD_PIN=[]
        self.pin_reset()

        self.GPIO_OUT_REG = const(0xD0000010)        #GPIO 0-31 output register
        self.GPIO_IN_REG= const(0xD0000004)          #GPIO 0-31 input register

        self.done_reset=0

        self.HEIGHT  =   320
        self.WIDTH   =   240

        
        self._MW = 0x2C
        self._SC = 0x2A
        self._SP = 0x2B

    def pin_reset(self):
        for i in range(self.LCD_D0,self.LCD_D0+8):
            self.LCD_PIN.append(Pin(i, Pin.OUT))
        self.RD_PIN = Pin(self.LCD_RD, Pin.OUT)
        self.WR_PIN = Pin(self.LCD_WR, Pin.OUT)
        self.CD_PIN = Pin(self.LCD_RS, Pin.OUT)
        self.CS_PIN = Pin(self.LCD_CS, Pin.OUT)
        self.RESET_PIN = Pin(self.LCD_RST, Pin.OUT)


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

    
    @asm_pio(set_init=PIO.OUT_HIGH,out_init=(PIO.OUT_LOW,) * 8, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=8)
    def paral_w8():
        out(pins,8)       # unload 8 bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
#
    def write8(self,i):
        self.paral_write8 = StateMachine(0, self.paral_w8,freq=125000000, out_base=self.LCD_PIN[0],set_base=self.WR_PIN)
        self.paral_write8.active(1)
        self.paral_write8.put(i)

    @asm_pio(set_init=PIO.OUT_HIGH,out_init=(PIO.OUT_LOW,) * 8, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
    def paral_w16():
        out(x,8)          # store 8 LSB in x
        out(pins,8)       # unload 8 msb bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
        mov(osr,x)        # replace 8 LSB in osr
        out(pins,8)       # unload 8 lsb bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
#
    def write16(self,i):
        self.paral_write16 = StateMachine(0, self.paral_w16,freq=125000000, out_base=self.LCD_PIN[0],set_base=self.WR_PIN)
        self.paral_write16.active(1)
        self.paral_write16.put(i)


    @asm_pio(sideset_init=PIO.OUT_HIGH,set_init=PIO.OUT_HIGH,out_init=(PIO.OUT_HIGH,) * 8, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
    def paral_cmd8():
        pull()
        nop()          .side(0) # CD pin off
        out(pins,8)       # unload 8 MSB bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
        out(pins,8)       # unload 8 LSB bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
        nop()          .side(1) # CD pin on
        push()
#
    def WriteCmd(self,cmd):
        cmd= (cmd>>8 | cmd<<8) & 0xFFFF  # inverting hi and low 8 bit value to match with the asm_pio 'out' logic
        self.paral_WriteCmd = StateMachine(1, self.paral_cmd8,freq=125000000, out_base=self.LCD_PIN[0],set_base=self.WR_PIN,sideset_base=self.CD_PIN)
        self.paral_WriteCmd.active(1)
        self.paral_WriteCmd.put(cmd)
        self.paral_WriteCmd.get()
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
        self.write16(x1)    #data bits sent to data pins
        self.write16(x2)    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] | CS_value             #CS_IDLE
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS_ACTIVE
        self.WriteCmd(self._SP)
        self.write16(y1)    #data bits sent to data pins
        self.write16(y2)    #data bits sent to data pins
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
         self.pin_reset()
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
        d = (ptr32(self.GPIO_IN_REG))
        return (d[0] & (0xFF << DATA_0))
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
        self.wake_on()
        self.init_meth()
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
        self.balay(h*w,color) # here needs asm_pio code to refresh all lines fast
        self.pin_reset()
        self.CS_IDLE()
#
#
    @asm_pio(set_init=PIO.OUT_HIGH, out_init=(PIO.OUT_LOW,) * 8, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=24)
    def paral_prog():
        out(x,24)         # 1st pull moved to x -> 24 bit nb of pixels to be drawn
        out(isr,16)       # 2nd pull moved to y -> 16 bit color (8LSB and 8MSB inverted)
        label("xloop")
        mov(osr,isr)
        set(y,1)
        label("yloop")
        out(pins,8)       # unload 8 MSB bits osr to output pins
        set(pins,0)       # WR off
        set(pins,1)       # WR on
        jmp(y_dec,"yloop")
        jmp(x_dec,"xloop")
        push()            # push to be read by main program -> allows to block the main program if data transfer is not ended

    def balay(self,nbpix,color):
        color= (color>>8 | color<<8) & 0xFFFF  # inverting hi and low 8 bit value to match with the asm_pio 'out' logic
        self.paral_sm = StateMachine(0, self.paral_prog,freq=125000000, out_base=self.LCD_PIN[0],set_base=self.WR_PIN)
        self.paral_sm.active(1)
#         self.paral_sm.restart()
        self.paral_sm.put(nbpix-1)
        self.paral_sm.put(color)
        self.paral_sm.get()    # this wait for the ending "push" command of the parallel prog function, to make sure it is finished before moving on
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
        WR_value = 1 << int(ptr8(self.LCD_WR))
        CD_value = 1 << int(ptr8(self.LCD_RS))
        CS_value = 1 << int(ptr8(self.LCD_CS))
        SC_value = int(ptr8(self._SC))
        SP_value = int(ptr8(self._SP))
        MW_value = int(ptr8(self._MW))
        WR_off = WR_value ^ int(0xFFFFFFF)
        CD_off = CD_value ^ int(0xFFFFFFF)
        CS_off = CS_value ^ int(0xFFFFFFF)
        _SC_h = (SC_value >> 8) << DATA_0
        _SC_l = (SC_value) << DATA_0
        _SP_h = (SP_value >> 8) << DATA_0
        _SP_l = (SP_value) << DATA_0
        _MW_h = (MW_value >> 8) << DATA_0
        _MW_l = (MW_value) << DATA_0
        D_MASK= 0xFF << DATA_0
        D_MASK_off = D_MASK ^ int(0xFFFFFFF)
        x_hi= ((x>>8) & (0xFF << DATA_0))
        x_lo = (x & (0xFF << DATA_0))
        y_hi= ((y>>8) & (0xFF << DATA_0))
        y_lo =(y & (0xFF << DATA_0))
        color_hi= ((color>>8) & (0xFF << DATA_0))
        color_lo = (color & (0xFF << DATA_0))
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT[0] = GPIO_OUT[0] & CS_off              #CS active
        GPIO_OUT[0] = GPIO_OUT[0] & CD_off              #CD_COMMAND
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SC_h    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
        GPIO_OUT[0] = (GPIO_OUT[0] & D_MASK_off) | _SC_l    #data bits sent to data pins
        GPIO_OUT[0] = GPIO_OUT[0] & WR_off              #WR pin strobe (off)
        GPIO_OUT[0] = GPIO_OUT[0] | WR_value            #WR pin strobe (on)
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

