# ILI9341 parallel driver by Hugh
# Largely inspired from the MCUFriend arduino library writen in c

from machine import Timer, Pin, ADC
from time import sleep_ms


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
        self.coeff_short = -0.07215071
        self.const_short = 276.7274
        self.coeff_long = 0.09638807
        self.const_long = -42.45778
        self.lastX=None
        self.lastY=None
        
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
        adc.atten(ADC.ATTN_11DB)
        z1 = adc.read()
        adc = ADC(Pin(self._yp))
        adc.atten(ADC.ATTN_11DB)
        z2 = adc.read()
        return (4095-(z2-z1))


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
        adc.atten(ADC.ATTN_11DB)
        val = [4095-adc.read()]
        for i in range(1,self.NumSamples):
            adc = ADC(Pin(self._yp))
            adc.atten(ADC.ATTN_11DB)
            val.append(4095-adc.read())
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
        adc.atten(ADC.ATTN_11DB)
        val = [4095-adc.read()]
        for i in range(1,self.NumSamples):
            adc = ADC(Pin(self._xm))
            adc.atten(ADC.ATTN_11DB)
            val.append(4095-adc.read())
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
                    if self.pressure()==0:
                        i+=1                
            if (self.pressure()>0): on_read=True
            if ((self.pressure()==0) and on_read):
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

            
