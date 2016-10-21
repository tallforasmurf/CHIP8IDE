__license__ = '''
 License (GPL-3.0) :
    This file is part of CHIP8IDE.

    CHIP8IDE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You can find a copy of the GNU General Public License in the file
    COPYING.TXT included in the distribution of this program, or see:
    <http://www.gnu.org/licenses/>.
'''
__version__ = "1.0.0"
__author__  = "David Cortesi"
__copyright__ = "Copyright 2016 David Cortesi"
__maintainer__ = "David Cortesi"
__email__ = "davecortesi@gmail.com"

'''

    CHIP-8 IDE Interface Window

The Interface window displays the emulated screen and emulated keypad.

The module is called by the chip8ide module at initialize() to create the
window and its contents as Qt objects. It sets its geometry from the saved
settings. After creation, the window objects respond to Qt events from user
actions.

The window is an independent (that is parent-less) window with the title
"CHIP-8 I/O". It can be positioned, minimized or maximized independent of the
rest of the app. Within the window are the following widgets:

The display, represented as a QLabel containing a QPixmap. It presents the
CHIP8 (32x64) or SCHIP (64x128) display as an array of square pixels.

The keypad, represented as a grid of specialized QPushbuttons.

A QCheckbox that shows the current mode of the display.

This window also implements the CHIP-8 sound output, emitting a continuous
tone while the sound register is nonzero.

Design/factorization note. The MasterWindow object is a container for the
Screen and the Keypad objects. Nominally, the methods to operate on one of
these, for example to set an emulated pixel or sample a key, would be methods
of the MasterWindow -- which instantiates and contains those objects.

However the API functions exported by this module all relate to direct
manipulation of the screen and keypad. To make them go through the
MasterWindow would just add another layer of name lookup and function call.

So when MasterWindow instantiates the Screen and Keypad objects, it puts
references to them in globals so their methods can be called directly from
the API functions. For example the exported draw_sprite() function can call
directly into the Screen methods.

'''

'''
Define the names that comprise the public API to this module. No other names
will be visible to code that imports this module.
'''

__all__ = [
    'initialize',
    'set_mode',
    'draw_sprite',
    'clear',
    'scroll_down',
    'scroll_left',
    'scroll_right',
    'key_test',
    'sound',
    'add_file_menu_action'
    ]

from typing import List, Tuple

'''
Import needed PyQt classes.
'''

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QSize,QRectF
    )

from PyQt5.QtGui import (
    QBitmap,
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPixmap,
    QResizeEvent
    )

from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget
    )

'''

Define the emulated screen as customized QLabel.

The QLabel manages the emulated video display as a QImage. Qt documents
QImage as being designed for "pixel access and manipulation".

The pixels of the CHIP-8 image are PxP rectangles, where P depends on the
size of the QImage, but is at least 2.

To actually draw a CHIP-8 pixel we use the QPainter method
fillRect(x,y,w,h,color) where color is white or black. So to draw the CHIP-8
pixel at cx, cy we use fillRect( P*cx, P*cy, P, P, color). To test the color of
the CHIP-8 pixel cx, cy we sample the QImage pixel at (P*cx+P/2, P*cy+P/2).

To display the image in the Qlabel, it has to be converted into a
QPixmap, This is done with the class method, QPixmap.fromImage().

'''
class Screen( QLabel ) :
    def __init__( self, parent=None ) :
        super().__init__( parent )
        '''
        Our minimum size should be 2x2 pixel-rectangles in SCHIP mode,
        or 128x256 plus some allowance for a frame.
        '''
        self.setMinimumWidth( 2*128 + 20 )
        self.setMinimumHeight( 2*64 + 20 )
        '''
        Set our size policy so we can grow but hopefully only in 1x2 ratio.
        '''
        sp = QSizePolicy( )
        sp.setHeightForWidth( True )
        sp.setHorizontalPolicy(  QSizePolicy.MinimumExpanding )
        sp.setVerticalPolicy( QSizePolicy.MinimumExpanding )
        self.setSizePolicy( sp )
        '''
        Style the look: Panel, sunken, rather wide frame.
        '''
        self.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.setLineWidth( 3 )
        self.setMidLineWidth( 3 )
        '''
        Set to align our pixmap in the center. For some unknown reason,
        if the scaledContents property is set, no drawing appears.
        '''
        self.setAlignment( Qt.AlignCenter )
        #self.setScaledContents( True )
        '''
        Create a place-holder QImage, which will shortly be replaced. At the
        time this __init__ runs, we have not been laid out. Soon we will come
        under control of an HBoxLayout, at which time our size will be set,
        and a resizeEvent will be delivered. Then the resizeEvent handler
        will redraw the QImage to fit the new size.

        One might think that since we only work in black and white, it would
        make sense to use QImage.Format_Monochrome or Format_Indexed8. Yeah,
        one would think that, but anything other than RGB creates weird
        anomalies and strange behavior.
        '''
        self.image = QImage( QSize( self.minimumWidth(), self.minimumHeight() ),
                             QImage.Format_RGB32 )
        self.black_color = QColor( "black" )
        self.white_color = QColor( "white" )
        self.image.fill( self.black_color )
        '''
        Set the initial emulated screen mode to standard, 32x64. Initialize
        the factor P to the current height of the image.
        '''
        self.P = int( self.minimumHeight() / 32 )
        self.extended_mode = False

    '''
    Clear the emulated screen to black and update our pixmap contents.
    '''
    def clear( self ) -> None :
        self.image.fill( self.black_color )
        self.setPixmap( QBitmap.fromImage( self.image ) )

    '''
    Get and set the screen mode, where True means SCHIP or extended mode.
    '''
    def mode( self ) -> bool :
        return self.extended_mode

    '''
    Set the mode to CHIP-8 or SCHIP. Recalculate pixel size P and clear
    the screen.
    '''
    def set_mode( self, schip=False ) -> None :
        if self.extended_mode != schip :
            '''
            Changing mode
            '''
            self.extended_mode = schip
        '''
        Regardless of a change, setting the mode recalculates the P value and
        clears the screen. P is current height divided by either 32 or 64.
        '''
        self.P = int( self.image.size().height() / 32 )
        if self.extended_mode :
            self.P >>= 1
        self.clear()

    #'''
    #Return the fact of whether the CHIP-8 pixel at cx, cy is white.
    #Test the QImage pixel that is near the center of the PxP rectangle
    #of the CHIP-8 pixel.

    #The test of a monochrome QImage pixel returns Qt.white (0x00ffffff)
    #or Qt.black (0x00000000), however with the high byte set to 0xff,
    #which is presumably the alpha-channel value.
    #'''
    #def test_pixel( self, cx:int, cy:int ) -> bool :
        #P = self.P
        #P2 = int(P/2)
        #color = self.image.pixel( cx*P + P2, cy*P + P2 )
        #return color != 0xff000000 # how "black" is reported

    #'''
    #Paint one CHIP-8 pixel white or black and return the truth of whether it
    #was previously white. Do the pixel test in-line to save a little time.
    #'''
    #def paint_pixel( self, cx:int, cy:int, white:bool=True ) -> bool :
        #P = self.P # save a few lookups
        #px = cx*P
        #py = cy*P
        #P2 = int(P/2)
        #present_color = self.image.pixel( cx*P + P2, cy*P + P2 )
        #was_white = present_color != 0xff000000
        #color = Qt.white if white else Qt.black
        #picasso = QPainter( self.image )
        #picasso.fillRect( px, py, P, P, color )
        #self.setPixmap( QBitmap.fromImage( self.image ) )
        #return was_white

    '''
    Paint a list of CHIP-8 pixels by the CHIP-8 XOR rule (if black, turn white,
    if white, turn black), and return the truth of whether any were white.
    '''
    def paint_pixel_list( self, pixels: List[Tuple[int]] ) -> bool :
        hit = False
        P = self.P
        P2 = P >> 1
        monet = QPainter( self.image )
        for cx, cy in pixels :
            px = cx * P
            py = cy * P
            was_white = 0xff000000 != self.image.pixel( px + P2, py + P2 )
            hit |= was_white
            color = Qt.black if was_white else Qt.white
            monet.fillRect( px, py, P, P, color )
        self.setPixmap( QBitmap.fromImage( self.image ) )
        return hit

    '''
    Let Layout managers know we like to be 1x2 in geometry. Note this is only
    effective when we are laid out with Qt.AlignTop! If that is not specified
    on layout, heightForWidth is never called.
    '''

    def hasHeightForWidth( self ) -> bool :
        return True

    def heightForWidth( self, width ) -> int :
        return int( round( width/2 ) )

    '''
    Receive a resize event. Per the Qt docs, "When resizeEvent() is called,
    the widget already has its new geometry. The widget will be erased and
    receive a paint event immediately after processing the resize event."

    On the very first resize, the image is a minimum-sized one. On a later
    resize, the image has whatever size we set here.

    Compare the image size to the new size of our whole widget. If the new
    size has gotten enough smaller that the image no longer fits, then
    resize. (Note that our minimum width and height keep us from getting
    stupidly small.)

    If the new size is larger by enough pixels to justify a change in P,
    resize. A change in P is justified when at least 32 pixels are added
    vertically and 64 horizontally, or twice that for SCHIP mode.

    To resize means, build a new QImage sized to a multiple of 32/64 vertical
    and 64/128 horizontal, and set a new P factor. The image is filled with
    black, so if the emulator is running, its current screen output is lost.
    '''
    def resizeEvent( self, event:QResizeEvent ) :
        old_w = self.image.size().width()
        old_h = self.image.size().height()
        new_w = event.size().width()
        new_h = event.size().height()
        do_resize = False
        if old_w > new_w or old_h > new_h :
            '''
            Any amount of interference between the image and the frame
            means we resize, which effects a downsize.
            '''
            do_resize = True
        else :
            '''
            Growing? Not necessarily! But at least, there are 0 or more
            available pixels between the current image and the frame.
            Figure out if the gap justifies a resize, which is
            true if we've added at least one screen of pixels.
            '''
            threshhold_h = 128 if self.extended_mode else 64
            threshhold_w = threshhold_h >> 1 # that  is, 64 or 32
            do_resize = (threshhold_h <= ( new_h - old_h ) \
                         and threshhold_w <= ( new_w - old_w ) )
        if do_resize :
            self.P = int( new_w / ( 128 if self.extended_mode else 64 ) )
            dbgw = self.P * ( 128 if self.extended_mode else 64 )
            dbgh = self.P * ( 64 if self.extended_mode else 32 )
            new_size = QSize(
                self.P * ( 128 if self.extended_mode else 64 ),
                self.P * ( 64 if self.extended_mode else 32 )
                )
            self.image = QImage( new_size, QImage.Format_RGB32 )
            dbg1 = self.image.size().width()
            dbg2 = self.image.size().height()
            self.clear()
        super().resizeEvent( event )

'''

Define the main window in which our stuff is displayed.
When instantiated, it instatiates everything else.

'''
class MasterWindow( QWidget ) :
    def __init__( self, settings ) :
        super().__init__( None )
        '''
        Save the settings for the closeEvent.
        '''
        self.settings = settings

        '''
        Set our layout to an hbox.
        '''
        hbox = QHBoxLayout()
        self.setLayout( hbox )
        '''
        Instantiate the screen. It is on the left.
        Add a bit of stretch.
        '''
        self.screen = Screen()
        hbox.addWidget( self.screen, 10  , Qt.AlignTop)#Qt.AlignLeft |
        hbox.addStretch(5)

        ##debuggery
        #self.dbg = QPushButton('meh')
        #hbox.addWidget( self.dbg )
        #self.dbg.clicked.connect( self.dodbg )
        '''
        Set the window title
        '''
        self.setWindowTitle( "CHIP-8 I/O" )

        '''
        With all widgets created, resize and position the window
        from the settings.
        '''
        self.resize( settings.value( "display_page/size", QSize(600,400) ) )
        self.move(   settings.value( "display_page/position", QPoint(100, 100) ) )

    '''
    Override the built-in closeEvent() method to save our geometry in the
    settings.
    '''
    def closeEvent( self, event ) :
        self.settings.setValue( "display_page/size", self.size() )
        self.settings.setValue( "display_page/position", self.pos() )
        super().closeEvent( event ) # pass it along

'''
Receive the settings object and save it in a global for shutdown time. Create
the Display window.
'''

from PyQt5.QtCore import QSettings

OUR_WINDOW = None # type: QWidget
SCREEN = None # type: Screen
KEYPAD = None # type: Keypad

def initialize( settings: QSettings ) -> None :
    global OUR_WINDOW, SCREEN
    '''
    Create the window and everything in it.
    Pass the settings object for its use.
    '''
    OUR_WINDOW = MasterWindow( settings )
    '''
    Set up for quick access to screen and keypad
    '''
    SCREEN = OUR_WINDOW.screen
    # KEYPAD = OUR_WINDOW.keypad
    '''
    Display our window
    '''
    OUR_WINDOW.show()

'''
Set the mode of the emulated screen to CHIP-8 (32x64) or SCHIP (64x128) mode.
The screen is also cleared by this.
'''

def set_mode( schip : bool ) -> None :
    SCREEN.set_mode( schip )

'''
Return the mode of the emulated screen. The emulator needs to know which
type of character font it should use.
'''

def get_mode( ) -> bool :
    return SCREEN.mode()

'''
Draw a CHIP8 sprite on the emulated screen. The sprite is passed as a list of
ints: 1 to 15 for a standard sprite, or 32 for an SCHIP 16x16 sprite.

We analyze the bytes and select out the 1-bits. For each 1-bit we make a
screen coordinate tuple. The list of tuples is passed to the paint_pixel_list()
method for drawing.

This means that "black" pixels are not painted. This is in accord with the
original COSMAC manual (and the BYTE article) which both say that "after a
pattern is shown on the screen it can be erased by showing the same pattern
again with the same X and Y coordinates" which is referred to as
"Exclusive-OR" logic. Consider the XOR truth table:

             Screen
XOR          0     1
          |-----|-----|
Sprite  0 |  0  |  1  |
          |-----|-----|
        1 |  1  |  0  |
          |-----|-----|

In short, if the sprite bit is 0, the screen bit is unchanged (0^0=0, 0^1=1).
While if the sprite bit is 1, the screen bit always changes. Ergo, we only
need to paint the pixels where the sprite bits are 1.

The given coordinates need to be wrapped at the screen boundaries.

'''
from PyQt5.QtTest import QTest

def draw_sprite( x: int, y:int, sprite_bytes: List[int] ) -> bool :
    '''
    To reduce the special-casing, convert an SCHIP 16x16 sprite from
    a list of 32, 8-bit ints, to a list of 16, 16-bit ints.
    '''
    pixel_list = []
    '''
    Set bit masks for x and y based on the screen resolution.
    '''
    y_mask = 0x003F if get_mode() else 0x001F
    x_mask = 0x007F if get_mode() else 0x003F

    bit_mask = 0x0080
    sprite = sprite_bytes
    if 32 == len(sprite) :
        bit_mask = 0x8000
        sprite = []
        for i in range(0, 32, 2) :
            sprite.append( ( sprite_bytes[i] << 8) | sprite_bytes[i+1] )
    y_coord = y & y_mask
    for word in sprite :
        x_coord = x & x_mask
        bit_cursor = bit_mask
        while bit_cursor : # is not zero,
            if word & bit_cursor :
                pixel_list.append( ( x_coord, y_coord ) )
            bit_cursor >>= 1
            x_coord = (x_coord + 1) & x_mask
        y_coord = (y_coord + 1) & y_mask

    hit = SCREEN.paint_pixel_list( pixel_list )
    QTest.qWait(10)
    return hit

'''
Clear the emulated screen to all-black.
'''

def clear( ) -> None :
    pass

'''
Scroll the emulated screen down N lines.
TODO: what if mode is now CHIP-8? force SCHIP? or ignore?
'''

def scroll_down( n:int ) -> None :
    pass

'''
Scroll the emulated screen 2 or 4 columns left.
'''

def scroll_left( ) -> None :
    pass

'''
Scroll the emulated screen 2 or 4 columns right.
'''

def scroll_right( ) -> None :
    pass

'''
Turn the emulated beeper/tone on or off.
'''

def sound( on : bool ) -> None :
    pass

'''
Return the value of a key that is depressed, if any; else return -1.
'''

def key_test(  ) -> int :
    # TODO: process events and possibly do a wait
    return -1

'''
Add an action to the File menu. This is called from the Source module, where
File>Load and File>Save are actually implemented. This module initializes the
File menu with only the Quit action, then Source adds its actions.
'''

from PyQt5.QtWidgets import QAction

def add_file_menu_action( action: QAction ) -> None :
    pass

'''
Define the Display window.

DisplayWindow is a QMainWindow, thus it owns the menu bar, and has the
responsibility for instantiating the File menu and populating it with actions.

'''

from PyQt5.QtWidgets import QMainWindow

class DisplayWindow( QMainWindow ) :
    pass


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#
# Enter the wonderful world of unit test...
#

if __name__ == '__main__' :
    from PyQt5.QtWidgets import QApplication
    args = []
    the_app = QApplication( args )
    initialize(QSettings())
    OUR_WINDOW.show()
    sprite = [0x20,0x70,0x70,0xF8,0xD8,0x88] # rocket ship
    draw_sprite( 4, 4, sprite )
    the_app.exec_()
