from random import getrandbits
from time import sleep_ms,ticks_ms, ticks_diff
import ILI9341
# Pin definition
LCD_RD = 2
LCD_WR = 4
LCD_RS = 32   # RS & CS pins must be ADC and OUTPUT
LCD_CS = 33   # for touch capability -> For Rpico only pins 26, 27 & 28 !
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

#Init the LCD screen
tft=ILI9341.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7)

tft.begin()
tft.setrotation(0)
tft.fillscreen(BLACK)
tft.SetFont(2)
tft.setTextColor(WHITE)
tft.setTextCursor(0,tft.Char_height)


a="This command defines the Vertical Scrolling Area of the display.\nWhen MADCTL B4=0 The 1st & 2nd parameter TFA [15...0] describes \
the Top Fixed Area (in No. of lines from Top of the Frame Memory and Display).\nThe 3rd & 4th parameter VSA [15...0] describes the \
height of the Vertical Scrolling Area (in No. of lines of the Frame Memory [not the display] from the Vertical Scrolling Start Address)\
.\nThe first line read from Frame Memory appears immediately after the bottom most line of the Top Fixed Area.\nThe 5th & 6th parameter \
BFA [15...0] describes the Bottom Fixed Area (in No. of lines from Bottom of the Frame Memory and Display).\nTFA, VSA and BFA refer to \
the Frame Memory Line Point"

tft.prints(a*3)


