# ILI9341 char drawing methods

def SetFont(self,i):
    if i==1:
        import FreeMono9pt7b
        #FreeMono9pt7bBitmaps
        self.fontbitmaps= FreeMono9pt7b.FreeMono9pt7bBitmaps
        self.Glyphs = FreeMono9pt7b.FreeMono9pt7bGlyphs
        self.Char_height=13
        self.Char_width=13
        self.Line_Spacing=2
        #Used for line scrolling
        self.scroll_count=0
        self.top=0
        self.ht = self.Char_height+self.Line_Spacing
        self.lines = self.HEIGHT//(self.Char_height+self.Line_Spacing)
        self.scrolling=False
    elif i==2:
        #FreeSansSerif7pt7b
        import FreeSansSerif7pt7b
        self.fontbitmaps= FreeSansSerif7pt7b.FreeSansSerif7pt7bBitmaps
        self.Glyphs = FreeSansSerif7pt7b.FreeSansSerif7pt7bGlyphs
        self.Char_height=8
        self.Char_width=7
        self.Line_Spacing=2
        #Used for line scrolling
        self.scroll_count=0
        self.top=0
        self.ht = self.Char_height+self.Line_Spacing
        self.lines = self.HEIGHT//(self.Char_height+self.Line_Spacing)
        self.scrolling=False
    elif i==3:
        #FreeMono12pt7b
        import FreeMono12pt7b
        self.fontbitmaps= FreeMono12pt7b.FreeMono12pt7bBitmaps
        self.Glyphs = FreeMono12pt7b.FreeMono12pt7bGlyphs
        self.Char_height=19
        self.Char_width=19
        self.Line_Spacing=2
        #Used for line scrolling
        self.scroll_count=0
        self.top=0
        self.ht = self.Char_height+self.Line_Spacing
        self.lines = self.HEIGHT//(self.Char_height+self.Line_Spacing)
        self.scrolling=False
        
def setTextCursor(self,x,y):
    self.x_cursor = x
    self.y_cursor = y

def setTextColor(self,color):
    self.text_color = color

def printh(self,mess):
    for i in mess:
        if i=="\n":
            self.x_cursor=0
            self.y_cursor = self.y_cursor+self.Char_height+self.Line_Spacing
        else:
            self.drawchar(i)
            if self.x_cursor>(self._width-1):
                self.x_cursor=0
                self.y_cursor = self.y_cursor+self.Char_height+self.Line_Spacing

# Print function in hardware scrolling mode (to be used only in portrait mode (setrotation=0))
def prints(self,mess):
    for i in mess:
        if (self.y_cursor>(self.HEIGHT-self.ht)):
            self.scrolling=True
        if i=="\n":
            if (self.scrolling and self.y_cursor>((self.scroll_count-1)*self.ht)):
                self.defil()
            else :
                self.x_cursor=0
                self.y_cursor = self.y_cursor+self.Char_height+self.Line_Spacing
        else:
            self.drawchar(i)
            if self.x_cursor>(self._width-1):
                self.x_cursor=0
                self.y_cursor = self.y_cursor+self.Char_height+self.Line_Spacing
                if (self.scrolling and self.y_cursor>((self.scroll_count-1)*self.ht)):
                    self.defil()



def defil(self):
    self.scroll_count+=1
    if self.scroll_count>=self.lines+1:
        self.scroll_count=0
    self.vertScroll(self.top,self.HEIGHT,self.scroll_count*self.ht)
    self.fillRect(0,(self.scroll_count-1)*self.ht,self._width,self.ht,0x0000)
    self.setTextCursor(0,(self.scroll_count-1)*self.ht+self.Char_height)

def drawchar(self,char):
    Glyph=self.Glyphs[ord(char)-0x20]
    index = Glyph[0]
    W = Glyph[1]
    H = Glyph[2]
    xAdv = Glyph[3]
    dX = Glyph[4]
    dY = Glyph[5]
    n_bytes=int(W*H/8)+1
    byte_list=self.fontbitmaps[index:(index+n_bytes)]
    pos=1
    x=self.x_cursor+dX
    y=self.y_cursor+dY
    for a in byte_list:
        for i in range(7,-1,-1):
            if (y-self.y_cursor-dY)==H:
                break
            if (a & (1<<i)) :
                self.drawPixel(x,y,self.text_color)
            pos+=1
            #print("pos=",pos,"\tx=",x,"\ty=",y)        
            x+=1
            if (pos>W):           
                x=self.x_cursor+dX
                y+=1
                pos=1
    self.x_cursor=self.x_cursor+xAdv

