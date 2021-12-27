# ILI9341-parallel-TFT-driver-for-micropython
For use with an 8-bit parallel TFT touchscreen using micropython. Many thanhs to the MCUFriend TFT library, written in C code and from which I derived this micropython driver.
Thank you also to Roberthh on the micropython forum for all his very instructive posts about the use of the micropython viper decorator. This helped me much !


You'll find 2 different ILI9341 drivers for micropython in this repository :
ILI9341_ESP32 -> for use with standard ESP32 microcontroller 
ILI9341_RP2 -> for use with Raspberry PICO microcontroller

Both libraries have been fully tested using micropython 1.17

These libraries are exclusively purposed for an 8bit parallel Touchscreen using the ILI9341 driver. Like the ones you find on this page : http://www.lcdwiki.com/2.8inch_Arduino_Display

![image](https://user-images.githubusercontent.com/47264131/147507578-3d2a8c01-93e7-4cd0-803f-171dec1e2802.png)
![image](https://user-images.githubusercontent.com/47264131/147507527-66f6f21a-32bc-4388-a9a0-2f678eb2a71b.png)


These libraries include 3 different fonts.

The libraries use micropython_viper decorator to improve speed and achieve reasonable graphic display speed

## How to use the files in the repository :

### 1. After installing micropython on your device:
copy the full content of the corresponding folder to the root directory (using Thonny, Rshell or wathever software you usually use)

### 2. Short description of the files :

ILI9341.py : Main LCD display library, must be imported in full in the py program in order to use all the features, from this library you can declare a "screen" class object

ILI9341_touch.py : Touchscreen library, must be imported if you need to use the touch feature of the display, from this library you can declare a "touchscreen" class object

ILI9341_char.py : Used to draw characters from the font libraries

FreeMono12pt7b.py : Big fonts
FreeMono9pt7b.py : Medium fonts
FreeSansSerif7pt7b.py : Small fonts

main.py : First example; loaded by default, a test of various routines and a mesaure of the display time

mainfull.py : The example above + touchscreen calibration

scroll.py : An example of a scrolling text (The ILI9341 parallel display has a hardware scrolling feature)

sdcard.py : Library to use for SD card access (The ILI9341 parallel display has an integrated micro SD card reader)

SdcardTimerTest.py : An example to set and display the time and print on screen the content of the SDcard

All the examples above start by setting the pins connected to the display (and if needed to the SD card pins) :

## 3. Pin definition

### 3.1 Pin definition for the LCD display
LCD_RD = 2

LCD_WR = 4

LCD_RS = 32   # RS & CS pins must be ADC and OUTPUT

LCD_CS = 33   # for touch capability -> For ESP32 only pins 32 & 33 - For PICO only pins 26,27 & 28

LCD_RST = 22

LCD_D0 = 12

LCD_D1 = 13

LCD_D2 = 26

LCD_D3 = 25

LCD_D4 = 17

LCD_D5 = 16

LCD_D6 = 27

LCD_D7 = 14

### 3.2 Pin definition for the touchscreen

XP = LCD_D0   #

YM = LCD_D1   #  Those four pins are used for the touchscreen

YP = LCD_CS   #  Please note that CS and RS are the same as for the display above

XM = LCD_RS   #

Except for the RS and CS pins, you can choose any I/O pin, but be aware that to use the SDcard you will need an available SPI, so save at least one set of SPI pins for this !

## 4. Touchsceen calibration procedure

Once you have loaded the "main_full_test_LCD_TOUCH.py" file, after a few tests you'll see on screen the calibration procédure. It is a basic set of green crosses you have to touch and when it's done calcultations are made to interpolate the x and y position with the ADC values.
Once it is complete you'll find the results giving a set of parameters:
```
Cal. result : Pos(pixel) = a * ADC_val + b

Short direction ->  a = -0.005244441
                    b = 292.7332

Long direction  ->  a = 0.006892291
                    b = -72.781

Touch anywhere to test !
```
What you have to do is copy these paramters in the ILI9341_touch.py library :

 self.coeff_short = results above for Short direction a
 self.const_short = results above for Short direction b
 self.coeff_long = results above for Long direction a
 self.const_long = results above for Long direction b
 
 and that's it !
 
 ## 5. Using the routines
 
 ### 5.1 Display routines
 
 Once you've declared your "screen" class object using ```tft=ILI9341.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7)```
 
the following commands are availabe :

tft.begin() : You have to start with this one, this initiates and resets the display
tft.fillscreen(Color : Fill the entire screen with the corresponding color (16-bit color value)
tft.setrotation(0) : 0 an 2 are portrait mode, 1 and 3 are landscape mode
tft.fillRect(start x,start y, width, height ,color) : Draw a filled rectangle
tft.drawFastVLine(start x,start y, length, color) : Draw a vertical line
tft.drawFastHLine(start x,start y, length, color) : Draw an horizontal line
tft.drawLine(start x,start y, end x, end y, color) : Draw any other type of line
tft.drawPixel(x, y, color) : Draw a Pixel
tft.drawCircle(x, y, r, color) : Draw a circle, x,y = center position, r = radius in pixels
tft.fillDisk(x, y, r, color) : Draw a completely filled disk x,y = center position, r = radius in pixels
tft.drawDisk(x, y, y, r1, r2, color) : Draw a ring x,y = center position, r1 = inner radius in pixels, r2 = outer radius in pixels

tft.SetFont(i) : i 1 or 2 or 3 at the moment since only 3 fonts are available - A font MUST BE SET in order to use the following text features
tft.setTextColor(color) : Sets the characters color (16-bit value)
tft.setTextCursor(x,y) : Position the text cursor at the desired value - This position is the lowest-left pixel to start character printing
tft.printh(String) : Print the string, add a "\n" character at the end for linefeed
tft.prints(String) : Same as printh, but with a very cool scrolling additional feature ! (see example)

### 5.2 Touch routines

Once you've declared your "screen" class object using ```ts = ILI9341_touch.touchscreen(XP, YP, XM, YM) ```
 
the following commands are availabe :
