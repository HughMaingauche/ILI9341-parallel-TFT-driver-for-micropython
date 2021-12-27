# ILI9341 parallel driver by Hugh
# Largely inspired from the MCUFriend arduino library writen in c

from machine import Timer, Pin, ADC
from random import getrandbits
from time import sleep_ms
import ILI9341, ILI9341_touch


# Pin definition
LCD_RD = 2
LCD_WR = 4
LCD_RS = 32   # RS & CS pins must be ADC and OUTPUT
LCD_CS = 33   # for touch capability -> For ESP32 only pins 32 & 33 !
LCD_RST = 22
LCD_D0 = 12
LCD_D1 = 13
LCD_D2 = 26
LCD_D3 = 25
LCD_D4 = 17
LCD_D5 = 16
LCD_D6 = 27
LCD_D7 = 14

XP = LCD_D0
YM = LCD_D1
YP = LCD_CS
XM = LCD_RS

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

# Init the LCD screen
tft=ILI9341.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7)
tft.begin()

#Initi the touchscreen
ts = ILI9341_touch.touchscreen(XP, YP, XM, YM)        


def DrawCross(x,y,size):
    ts.Pin_reset()
    tft.fillRect(x-int(size/2),y-int(size/2),size+1,size,RED)
    tft.drawFastVLine(x,y-int(size/2),size,WHITE)
    tft.drawFastHLine(x-int(size/2),y,size+1,WHITE)

def TodoCross(x,y,size):
    ts.Pin_reset()
    tft.fillRect(x-int(size/2),y-int(size/2),size+1,size,GREEN)
    tft.drawFastVLine(x,y-int(size/2),size,WHITE)
    tft.drawFastHLine(x-int(size/2),y,size+1,WHITE)

def DoneCross(x,y,size):
    ts.Pin_reset()
    tft.fillRect(x-int(size/2),y-int(size/2),size+1,size,GRAY)
    tft.drawFastVLine(x,y-int(size/2),size,BLACK)
    tft.drawFastHLine(x-int(size/2),y,size+1,BLACK)

def Calibrate():
    tft.setrotation(0)
    tft.fillscreen(BLACK)

    ts.coeff_short = 1
    ts.const_short = 0
    ts.coeff_long = 1
    ts.const_long = 0
    size=20
    list_point=[[size,size],[int(tft._width/2),size],[tft._width-size,size],
                [size,int(tft._height/2)],[int(tft._width/2),int(tft._height/2)],[tft._width-size,int(tft._height/2)],
                [size,tft._height-size],[int(tft._width/2),tft._height-size],[tft._width-size,tft._height-size]]

    lxpos=[]
    lxval=[]
    lypos=[]
    lyval=[]

    for p in list_point:
        DrawCross(p[0],p[1],size)

    tft.SetFont(2)
    tft.setTextColor(GREEN)
    tft.setTextCursor(20,60)
    tft.printh("Touchscreen calibration procedure")
    tft.setTextCursor(50,100)
    tft.printh("Touch the green crosses !")

    for p in list_point:
        TodoCross(p[0],p[1],size)
        on_read=False
        x,y=ts.Point_Listen()
#         print("x = ",x,"\tPos X = ",p[0],"\ty = ",y,"\tPos Y = ",p[1])
        lxpos.append(p[0])
        lxval.append(x)
        lypos.append(p[1])
        lyval.append(y)
        DoneCross(p[0],p[1],size)

    lxpos_ord = [x for _,x in sorted(zip(lxval,lxpos))]
    lxval.sort()
    lypos_ord = [x for _,x in sorted(zip(lyval,lypos))]
    lyval.sort()

    if (lyval[-1]==4065 or lxval[-1]==4095):
        mess="Failed: one ore more ADC value is 4095"
        cal_err=1
    else:
        mess="Calibration complete"
        cal_err=0
#     print("x;PixelX;y;PixelY")
#     for i in range(len(list_point)):
#         print(lxval[i],";",lxpos_ord[i],";",lyval[i],";",lypos[i])
    ts.const_short,ts.coeff_short=ts.estimate_coef(lxval,lxpos_ord)
    ts.const_long,ts.coeff_long=ts.estimate_coef(lyval,lypos_ord)
    
    if cal_err==0:
        tft.fillscreen(BLACK)
        tft.setTextCursor(50,10)
        tft.printh(mess)
        tft.setTextColor(WHITE)
        tft.setTextCursor(0,50)
        tft.printh("Cal. result : Pos(pixel) = a * ADC_val + b")
        tft.setTextCursor(0,70)
        tft.printh("Short direction -> a = ")
        tft.printh(str(ts.coeff_short))
        tft.setTextCursor(108,80)
        tft.printh("b = ")
        tft.printh(str(ts.const_short))
        tft.setTextCursor(0,95)
        tft.printh("Long direction  -> a = ")
        tft.printh(str(ts.coeff_long))
        tft.setTextCursor(108,105)
        tft.printh("b = ")
        tft.printh(str(ts.const_long))
        tft.SetFont(1)
        tft.setTextColor(CYAN)
        tft.setTextCursor(40,135)
        tft.printh("Touch anywhere")
        tft.setTextCursor(60,165)
        tft.printh("to test !")
        
    else:
        tft.fillRect(0,21,240,125,BLACK)
        tft.setTextCursor(20,60)
        tft.setTextColor(RED)
        tft.printh(mess)
    
    ts.Pin_reset()
    return(cal_err)



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
    tim1 = Timer(1)
    tim1.init()
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
    t1=tim1.value()
    tim1.init()
    testblue()
    t2=tim1.value()
    tim1.init()
    testgreen()
    t3=tim1.value()
    tim1.init()
    testred()
    t4=tim1.value()

def printv(mess):
    for i in mess:
        tft.drawchar(i)
        if tft.x_cursor>tft._width:
            tft.x_cursor=0
            tft.y_cursor = tft.y_cursor+tft.Char_height


# initial LCD tests
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

tft.fillRect(0,200,240,120,BLUE)
tft.setTextColor(CYAN)
tft.SetFont(1)
tft.setTextCursor(80,220)
tft.printh("Moving to")
tft.setTextCursor(30,240)
tft.printh("Calibration test")
tft.setTextCursor(60,275)
tft.printh("in:")
tft.SetFont(3)

for i in range(5,0,-1):
    tft.fillRect(100,250,40,40,RED)
    tft.setTextCursor(110,275)
    tft.setTextColor(WHITE)
    tft.printh(str(i))
    sleep_ms(1000)

# Start calibration
Calibrate()

tft.SetFont(1)
tft.setTextColor(YELLOW)

# Test X, Y position on screen
while 1:
    x,y=ts.Point_Listen()
    tft.fillRect(0,199,240,40,BLACK)
    tft.setTextCursor(60,220)
    tft.printh("x=")
    tft.printh(str(x))
    tft.printh("  y=")
    tft.printh(str(y))
#     print(x,y)
    

