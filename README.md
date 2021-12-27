# ILI9341-parallel-TFT-driver-for-micropython
For use with an 8-bit parallel TFT touchscreen using micropython. Many thanks to prenticedavid and his [MCUFriend TFT library](https://github.com/prenticedavid/MCUFRIEND_kbv), written in C code and from which I derived this micropython driver.
Thank you also to Roberthh on the [micropython forum](https://forum.micropython.org/viewtopic.php?f=14&t=10986) for all his very instructive posts about the use of the micropython viper decorator. This helped me much !


You'll find 2 different ILI9341 drivers for micropython in this repository :<br/>
ILI9341_ESP32 -> for use with standard ESP32 microcontroller<br/>
ILI9341_RP2 -> for use with Raspberry PICO microcontroller<br/>

For the ESP32, it's working well but I sometime have memory issues, in this case use of gc.collect() might be usefull

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

ILI9341.py : Main LCD display library, must be imported in full in the py program in order to use all the features, from this library you can declare a "screen" class object<br/>
ILI9341_touch.py : Touchscreen library, must be imported if you need to use the touch feature of the display, from this library you can declare a "touchscreen" class object<br/>

ILI9341_char.py : Used to draw characters from the font libraries

FreeMono12pt7b.py : Big fonts<br/>
FreeMono9pt7b.py : Medium fonts<br/>
FreeSansSerif7pt7b.py : Small fonts<br/>

main.py : First example; loaded by default, a test of various routines and a mesaure of the display time<br/>
mainfull.py : The example above + touchscreen calibration<br/>
scroll.py : An example of a scrolling text (The ILI9341 parallel display has a hardware scrolling feature)<br/>
sdcard.py : Library to use for SD card access (The ILI9341 parallel display has an integrated micro SD card reader)<br/>
SdcardTimerTest.py : An example to set and display the time and print on screen the content of the SDcard<br/>

All the examples above start by setting the pins connected to the display (and if needed to the SD card pins)

## 3. Pin definition

### 3.1 Pin definition for the LCD display
LCD_RD = 2<br/>
LCD_WR = 4<br/>
LCD_RS = 32   # RS & CS pins must be ADC and OUTPUT<br/>
LCD_CS = 33   # for touch capability -> For ESP32 only pins 32 & 33 - For PICO only pins 26,27 & 28<br/>
LCD_RST = 22<br/>
LCD_D0 = 12<br/>
LCD_D1 = 13<br/>
LCD_D2 = 26<br/>
LCD_D3 = 25<br/>
LCD_D4 = 17<br/>
LCD_D5 = 16<br/>
LCD_D6 = 27<br/>
LCD_D7 = 14<br/>

### 3.2 Pin definition for the touchscreen

XP = LCD_D0   #<br/>
YM = LCD_D1   #  Those four pins are used for the touchscreen<br/>
YP = LCD_CS   #  Please note that CS and RS are the same as for the display above<br/>
XM = LCD_RS   #<br/>

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

 self.coeff_short = results above for Short direction a<br/>
 self.const_short = results above for Short direction b<br/>
 self.coeff_long = results above for Long direction a<br/>
 self.const_long = results above for Long direction b<br/>
 
 and that's it ! See a full video of the process :https://drive.google.com/file/d/1L7yVWag6e606RgQF5fxj9b6aB8_0982Q/view?usp=sharing
 
 ## 5. Using the routines
 
 ### 5.1 Display routines
 
 Once you've declared your "screen" class object using ```tft=ILI9341.screen(LCD_RD,LCD_WR,LCD_RS,LCD_CS,LCD_RST,LCD_D0,LCD_D1,LCD_D2,LCD_D3,LCD_D4,LCD_D5,LCD_D6,LCD_D7)```
 
the following commands are availabe :

tft.begin() : You have to start with this one, this initiates and resets the display<br/>
tft.fillscreen(Color : Fill the entire screen with the corresponding color (16-bit color value)<br/>
tft.setrotation(0) : 0 an 2 are portrait mode, 1 and 3 are landscape mode<br/>
tft.fillRect(start x,start y, width, height ,color) : Draw a filled rectangle<br/>
tft.drawFastVLine(start x,start y, length, color) : Draw a vertical line<br/>
tft.drawFastHLine(start x,start y, length, color) : Draw an horizontal line<br/>
tft.drawLine(start x,start y, end x, end y, color) : Draw any other type of line<br/>
tft.drawPixel(x, y, color) : Draw a Pixel<br/>
tft.drawCircle(x, y, r, color) : Draw a circle, x,y = center position, r = radius in pixels<br/>
tft.fillDisk(x, y, r, color) : Draw a completely filled disk x,y = center position, r = radius in pixels<br/>
tft.drawDisk(x, y, y, r1, r2, color) : Draw a ring x,y = center position, r1 = inner radius in pixels, r2 = outer radius in pixels<br/>

tft.SetFont(i) : i 1 or 2 or 3 at the moment since only 3 fonts are available - A font MUST BE SET in order to use the following text features<br/>
tft.setTextColor(color) : Sets the characters color (16-bit value)<br/>
tft.setTextCursor(x,y) : Position the text cursor at the desired value - This position is the lowest-left pixel to start character printing<br/>
tft.printh(String) : Print the string, add a "\n" character at the end for linefeed<br/>
tft.prints(String) : Same as printh, but with a very cool scrolling additional feature (only in portrait mode) ! (see example)<br/>

### 5.2 Touch routines

Once you've declared your "screen" class object using ```ts = ILI9341_touch.touchscreen(XP, YP, XM, YM) ```
 
the following commands are availabe :
ts.Pin_reset() : This is an important function. in every methods you want to implement, you have to do this reset before every call to a tft (display) routine (remember: CS and RS Pins are shared between the LCD display and the touchscreen interface, if the pins are not reset the screen functions will not work).<br/>
ts.pressure() : Return a value corresponding to the pressing strength - Mostly used to detect a touch <br/>
ts.getPoint() : Return the (x,y) position of the touch (provided the touchscreen has been correctly calibrated, see #4) <br/>
ts.Point_Listen() : Use with care, this loop returns the (x,y) touch value after the user has stopped touching (when removing the pencil). Used in the calibration function if you want to see it working.<br/>
