# ILI9341 parallel driver by vincent
# Largely inspired by the MCUFriend arduino library writen in c

from random import getrandbits
from time import sleep_ms,ticks_ms, ticks_diff
import ILI9341

# Pin definition
LCD_RD = 13
LCD_WR = 9
LCD_RS = 26   # RS & CS pins must be ADC and OUTPUT
LCD_CS = 27   # for touch capability -> For Rpico only pins 26, 27 & 28 !
LCD_RST = 14
LCD_D0 = 0
LCD_D1 = 1
LCD_D2 = 2
LCD_D3 = 3
LCD_D4 = 4
LCD_D5 = 5
LCD_D6 = 6
LCD_D7 = 7

XP = LCD_D0
YM = LCD_D1
YP = LCD_CS
XM = LCD_RS

#Init the LCD screen
tft=ILI9341.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7)



#Assign human-readable names to some common 16-bit color values:
BLACK       =   0x0000
BLUE        =   0x001F
RED         =   0xF800
GREEN       =   0x07E0
CYAN        =   0x07FF
MAGENTA     =   0xF81F
YELLOW      =   0xFFE0
WHITE       =   0xFFFF
GRAY        =   0x8410



def testgreen():
    test(32,10,64)

def testblue():
    test(0,10,1)


def testred():
    test(2048,11,2048)

def test(colini,step,coladd):
    col=colini
    for i in range(0,319,step):
        #print("i= ",i,"\t color=",col)
        tft.fillRect(i,0,step,319,col)
        col=col+coladd      

def testinit():
    global t1,t2,t3,t4
    start = ticks_ms()
    tft.fillscreen(getrandbits(16))
    tft.fillRect(10,10,80,80,getrandbits(16))
    tft.fillRect(230,10,80,80,getrandbits(16))
    tft.fillRect(10,150,80,80,getrandbits(16))
    tft.fillRect(230,150,80,80,getrandbits(16))
    tft.drawLine(0,0,319,239,getrandbits(16))
    tft.drawLine(0,239,319,0,getrandbits(16))
    color=getrandbits(16)
    tft.fillRect(155,90,10,60,color)
    tft.fillRect(130,115,60,10,color)
    tft.drawCircle(160,120,100,getrandbits(16))
    tft.drawDisk(160,120,50,60,getrandbits(16))
    end = ticks_ms()
    t1=ticks_diff(end,start)
    start = ticks_ms()
    testblue()
    end = ticks_ms()
    t2=ticks_diff(end,start)
    start = ticks_ms()
    testgreen()
    end = ticks_ms()
    t3=ticks_diff(end,start)
    start = ticks_ms()
    testred()
    end = ticks_ms()
    t4=ticks_diff(end,start)

def printv(mess):
    for i in mess:
        tft.drawchar(i)
        if tft.x_cursor>tft._width:
            tft.x_cursor=0
            tft.y_cursor = tft.y_cursor+tft.Char_height
# initial tests to see if everything's fine
tft.begin()
tft.setrotation(0)
tft.fillscreen(BLACK)
tft.setTextCursor(0,20)
tft.setTextColor(CYAN)
tft.SetFont(1)
tft.printh("      TFT 8-bit")
tft.setTextCursor(0,40)
tft.printh("  parallel interface")
tft.setTextCursor(0,80)
tft.setTextColor(GREEN)
tft.SetFont(3)
tft.printh("   by Hugh")
tft.setTextCursor(0,180)
tft.setTextColor(RED)
tft.printh("   for device:")
tft.SetFont(3)
tft.setTextCursor(70,250)
tft.setTextColor(YELLOW)
tft.printh(str(tft.readID()))
sleep_ms(1000)

tft.setrotation(3)
testinit()

tft.setrotation(0)
tft.fillscreen(WHITE)
tft.SetFont(2)
tft.setTextColor(BLACK)
tft.setTextCursor(70,10)
tft.printh("TFT 8-bit parallel")
tft.setTextCursor(60,30)
tft.printh("Micropython driver")
tft.setTextCursor(0,60)
tft.printh("Figures Drawn in ")
tft.printh(str(t1))
tft.printh(" ms")
tft.setTextCursor(0,80)
tft.printh("Faded blue screen in ")
tft.printh(str(t2))
tft.printh(" ms")
tft.setTextCursor(0,100)
tft.printh("Faded green screen in ")
tft.printh(str(t3))
tft.printh(" ms")
tft.setTextCursor(0,120)
tft.printh("Faded red screen in ")
tft.printh(str(t4))
tft.printh(" ms")


