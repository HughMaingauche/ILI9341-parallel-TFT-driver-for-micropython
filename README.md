# ILI9341-parallel-TFT-driver-for-micropython
For use with an 8-bit parallel TFT touchscreen using micropython


You'll find 2 different ILI9341 drivers for micropython in this repository :
ILI9341_ESP32 -> for use with standard ESP32 microcontroller 
ILI9341_RP2 -> for use with Raspberry PICO microcontroller

Both libraries have been fully tested using micropython 1.17

These libraries include 3 different fonts.

The libraries use micropython_viper decorator to improve speed and achieve reasonable graphic display speed

How to use the files in the repository :

1. After installing micropython on your device, copy the full content of the corresponding folder to the root directory (using Thonny, Rshell or wathever software you usually use)

Short description of the files :

ILI9341.py : Main LCD display library, must be imported in full in the py program in order to use all the features, from this library you can declare a "screen" class object

ILI9341_touch.py : Touchscreen library, must be imported if you need to use the touch feature of the display, from this library you can declare a "touchscreen" class object

ILI9341_char.py : Used to draw characters from the font libraries

FreeMono12pt7b.py : Big fonts
FreeMono9pt7b.py : Medium fonts
FreeSansSerif7pt7b.py : Small fonts

main.py : First example; loaded by default, a test of various routines and a mesaure of the display time
mainfull.py : The example above + touchscreen calibration
scroll.py : An example of a scrolling text (The ILI9341 parallel display has a hardware scrolling feature)
sdcard.py : Librariy to use for SD card access (The ILI9341 parallel display has an integrated micro SD card reader)
SdcardTimerTest.py
