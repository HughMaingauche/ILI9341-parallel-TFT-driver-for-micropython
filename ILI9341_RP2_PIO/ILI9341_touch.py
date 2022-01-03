# ILI9341 parallel driver by Hugh
# Largely inspired from the MCUFriend arduino library writen in c

from machine import Timer, Pin, ADC
from time import sleep_ms,ticks_ms, ticks_diff

class touchscreen:
    #------------------------------------
    def __init__(self,xp, yp, xm, ym):
        self._yp = yp
        self._xm = xm
        self._ym = ym
        self._xp = xp
        self.PYP=Pin(self._yp,Pin.OUT)
        self.PXM=Pin(self._xm,Pin.OUT)
        self.PYM=Pin(self._ym,Pin.OUT)
        self.PXP=Pin(self._xp,Pin.OUT)
        self._rxplate = 0
        self.NumSamples = 20
        self.coeff_short = -0.004810913
        self.const_short = 281.5355
        self.coeff_long = 0.006279673
        self.const_long = -40.5825
        self.lastX=None
        self.lastY=None
        self.press_threshold=15000
        
    def pressure(self):
        self.PXP=Pin(self._xp,Pin.OUT)
        self.PXP.off()
        self.PYM=Pin(self._ym,Pin.OUT)
        self.PYM.on()
        self.PXM.off()
        self.PXM=Pin(self._xm,Pin.IN)
        self.PYP.off()
        self.PYP=Pin(self._yp,Pin.IN)
        adc = ADC(Pin(self._xm))
        z1 = adc.read_u16()
        adc = ADC(Pin(self._yp))
        z2 = adc.read_u16()
#         print("pressure adc:\tz1:\t"+str(z1)+"\tz2:\t"+str(z2))
        return (65535-(z2-z1))


    def getPoint(self):
        self.PYP=Pin(self._yp,Pin.IN)
        self.PYM=Pin(self._ym,Pin.IN)
        self.PYP.off()
        self.PYM.off()
        self.PXP=Pin(self._xp,Pin.OUT)
        self.PXM=Pin(self._xm,Pin.OUT)
        self.PXP.on()
        self.PXM.off()
        adc = ADC(Pin(self._yp))
        val = [65535-adc.read_u16()]
        for i in range(1,self.NumSamples):
            adc = ADC(Pin(self._yp))
            val.append(65535-adc.read_u16())
        x0 = int(self.median(val)*self.coeff_short+self.const_short)
        self.PXP=Pin(self._xp,Pin.IN)
        self.PXM=Pin(self._xm,Pin.IN)
        self.PXP.off()
        self.PXM.off()
        self.PYP=Pin(self._yp,Pin.OUT)
        self.PYP.on()
        self.PYM=Pin(self._ym,Pin.OUT)
        self.PYM.off()
        adc = ADC(Pin(self._xm))
        val = [65535-adc.read_u16()]
        for i in range(1,self.NumSamples):
            adc = ADC(Pin(self._xm))
            val.append(65535-adc.read_u16())
        y0 = int(self.median(val)*self.coeff_long+self.const_long)
        return [x0,y0]

    def Pin_reset(self):
        self.PXP=Pin(self._xp,Pin.OUT)
        self.PXM=Pin(self._xm,Pin.OUT)
        self.PYP=Pin(self._yp,Pin.OUT)
        self.PYM=Pin(self._ym,Pin.OUT)       

    def Point_Listen(self):
        on_read=False
        on_loop = True
        while on_loop:
            P=self.getPoint()
            i=0
            if on_read:
                while (i<20):
                    if self.pressure()<self.press_threshold:
                        i+=1                
            if (self.pressure()>=self.press_threshold): on_read=True
            if ((self.pressure()<self.press_threshold) and on_read):
                on_loop=False
                self.Pin_reset()
                return P
    
    def median(self,lst):
        sortedLst = sorted(lst)
        lstLen = len(lst)
        index = (lstLen - 1) // 2
        if (lstLen % 2):
            return sortedLst[index]
        else:
            return (sortedLst[index] + sortedLst[index + 1])/2.0

    def estimate_coef(self,x, y):
        # number of observations/points
        n = len(x)
        # mean of x and y vector
        m_x = sum(x)/n
        m_y = sum(y)/n
        # calculating cross-deviation and deviation about x
        SS_xy = sum([a*b for a,b in zip(y,x)]) - n*m_y*m_x
        SS_xx = sum([a*b for a,b in zip(x,x)]) - n*m_x*m_x
        # calculating regression coefficients
        b_1 = SS_xy / SS_xx
        b_0 = m_y - b_1*m_x
        return (b_0, b_1)

# # Pin definition
# LCD_RD = 8
# LCD_WR = 9
# LCD_RS = 26   # RS & CS pins must be ADC and OUTPUT
# LCD_CS = 27   # for touch capability -> For ESP32 only pins 32 & 33 !
# LCD_RST = 10
# LCD_D0 = 0
# LCD_D1 = 1
# LCD_D2 = 2
# LCD_D3 = 3
# LCD_D4 = 4
# LCD_D5 = 5
# LCD_D6 = 6
# LCD_D7 = 7
# 
# XP = LCD_D0
# YM = LCD_D1
# YP = LCD_CS
# XM = LCD_RS
# 
# seconds=5
# #Init the touchscreen
# ts = touchscreen(XP, YP, XM, YM)
# 
# def test():
#     start = ticks_ms()
#     while 1:
#         print(ts.pressure())
#         end = ticks_ms()
#         d=ticks_diff(end,start)
# #         print("d:\t"+str(d)+"\tlimit:\t"+str(seconds*1000))
#         sleep_ms(50)
#         if d > (seconds*1000):
#             break
