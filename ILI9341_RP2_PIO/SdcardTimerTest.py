#
from machine import Pin,SPI
from time import sleep
import os, sdcard, utime, ILI9341pio

# Name of data file"
fn="/fc/data.csv"
# input start time of clock in format YYYY MM DD HH MM SS
time_input = ("2021 12 27 13 50 00")


#Real time clock set
#Enter time to set RTC when the pico is powered
#----------------------------------------------
dateTime = (time_input)+' 0 0'
givenTime = utime.mktime(list(map(int, tuple(dateTime.split(' ')))))
ctime=utime.localtime(givenTime)
# insert data to RTC register
setup_0 = (ctime[0] << 12) | (ctime[1] << 8) | ctime[2]
setup_1 = (ctime[3] << 16) | (ctime[4] << 8) | ctime[5]
setup_1 = setup_1 | (((ctime[6] + 1) % 7) << 24)
# register RTC address
rtc_base_mem = 0x4005c000
atomic_bitmask_set = 0x2000
machine.mem32[rtc_base_mem + 4] = setup_0
machine.mem32[rtc_base_mem + 8] = setup_1
machine.mem8[rtc_base_mem + atomic_bitmask_set + 0xc] = 0x10
#----------------------------------------------
# Print time function
# import utime ... already called above
#----------------------------------------------
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
months = ['January','February','March','April','May','June','July','August','September','October','November','December']
# end real time clock set


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
tft.begin()
# end of screen definition

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

# Initiate SD card
cs_pin = Pin(12)
sdspi = SPI(1)
sdspi.init()  # Ensure right baudrate
sd = sdcard.SDCard(sdspi, cs_pin)  # Compatible with PCB
vfs = os.VfsFat(sd)
os.mount(vfs, "/fc")
print("Filesystem check")
print(os.listdir("/fc"))
#

def read_lines(file_name):
    f=open(file_name,"r")
    l=f.readlines()
    for a in l:
        print(a)
        
def reset_datafile(file_name):
    f=open(file_name,"w")
    l=f.write("Date;Hauteur d'eau (m)\n")
    f.close()

def log_line(file_name,text):
    f=open(file_name,"a")
    l=f.write(text+"\n")
    f.close()

def print_SD_stats(path):
    totstats=os.statvfs(path)
    Max_SD_size=totstats[1]*totstats[2]
    Free_SD_size=totstats[1]*totstats[3]
    Used_SD_size=Max_SD_size-Free_SD_size
    Used_percent=round(100*(Used_SD_size/Max_SD_size),3)
    
    print("Max SD Size: "+String_stats(Max_SD_size))
    print("Used SD Size: "+String_stats(Used_SD_size))
    print("Free SD Size: "+String_stats(Free_SD_size))
    print("% occupied: "+str(Used_percent))

def String_stats(bytevalue):
    if bytevalue < 1024:
        return (str(bytevalue) + " by")
    elif bytevalue < 1048576:
        return ("%0.1f KB" % (bytevalue / 1024))
    else:
        return ("%0.1f MB" % (bytevalue / 1048576))



def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000
        sizestr = String_stats(filesize)
        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

def tft_print_SD_stats(path):
    totstats=os.statvfs(path)
    Max_SD_size=totstats[1]*totstats[2]
    Free_SD_size=totstats[1]*totstats[3]
    Used_SD_size=Max_SD_size-Free_SD_size
    Used_percent=round(100*(Used_SD_size/Max_SD_size),3)
    
    tft.printh("Max SD Size: "+String_stats(Max_SD_size)+"\n")
    tft.printh("Used SD Size: "+String_stats(Used_SD_size)+"\n")
    tft.printh("Free SD Size: "+String_stats(Free_SD_size)+"\n")
    tft.printh("% occupied: "+str(Used_percent)+"\n")

def tft_print_directory(path, tabs=0):
        for file in os.listdir(path):
            stats = os.stat(path + "/" + file)
            filesize = stats[6]
            isdir = stats[0] & 0x4000
            sizestr = String_stats(filesize)
            prettyprintname = ""
            for _ in range(tabs):
                prettyprintname += "  "
            prettyprintname += file
            if isdir:
                prettyprintname += "/"
            tft.printh(prettyprintname)
            tft.setTextCursor(tft._width-(len(sizestr)*tft.Char_width),tft.y_cursor)
            tft.printh(sizestr)
            tft.printh("\n")

            # recursively print directory contents
            if isdir:
                tft_print_directory(path + "/" + file, tabs + 1)


print("SD card statistics")
print_SD_stats("/fc")
print("Files on filesystem:")
print("====================")
print_directory("/fc")

#interrupt loop variable
Data_thread=True



def Data_thread():
    while Data_thread:
        tft.fillscreen(BLACK)
        (year,month,day,hour,minute,second,wday,yday)=utime.localtime(utime.time())
        current_time=("%s %02d-%02d-%d %02d:%02d:%02d" % (str(days[wday]), day, month, year, hour,minute,second))
        tft.setTextCursor(70,40)
        tft.setTextColor(CYAN)
        tft.SetFont(3)
        tft.printh(str(days[wday]))
        tft.setTextCursor(30,80)
        tft.setTextColor(YELLOW)
        tft.printh(str(months[month-1])+"  "+str(day))
        tft.setTextCursor(30,120)
        tft.setTextColor(RED)
        tft.printh("%02d" % hour)
        tft.setTextColor(WHITE)
        tft.printh(" : ")
        tft.setTextColor(MAGENTA)
        tft.printh("%02d" % minute)
        tft.setTextColor(WHITE)
        tft.printh(" : ")
        tft.setTextColor(GREEN)
        tft.printh("%02d" % second)
        current_time=("%s %02d-%02d-%d %02d:%02d:%02d" % (str(days[wday]), day, month, year, hour,minute,second))
        log_line(fn,current_time)
        tft.setTextCursor(0,160)
        tft.setTextColor(WHITE)
        tft.SetFont(2)
        tft.printh("Current time logged to : "+fn)
        tft.setTextCursor(0,180)
        tft.printh("SD card statistics\n")
        tft_print_SD_stats("/fc")
        tft.setTextCursor(0,250)
        tft.printh("Files on filesystem:\n")
        tft.printh("====================\n")
        tft_print_directory("/fc")
        sleep(5)

# Starting logging thread
Data_thread()

