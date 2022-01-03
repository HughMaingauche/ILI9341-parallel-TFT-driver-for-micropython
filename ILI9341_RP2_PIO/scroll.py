from time import sleep_ms,ticks_ms, ticks_diff
import ILI9341pio
# display screen 2.8" TFT 240x320 IL9341 parallel interface
# Pin definition
LCD_RD = 13
LCD_WR = 9
LCD_RS = 26   # RS & CS pins must be ADC and OUTPUT
LCD_CS = 27   # for touch capability -> For Rpico only pins 26, 27 & 28 !
LCD_RST = 14
LCD_D0 = 0


XP = LCD_D0
YM = LCD_D0 + 1 # YM is LCD_D1
YP = LCD_CS
XM = LCD_RS

#Init the LCD screen
# LCD DATA pins must be 8 consecutive pins startin at LCD_C0
tft=ILI9341pio.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0)


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


