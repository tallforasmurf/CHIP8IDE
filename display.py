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

The window is an independent (that is, parent-less) window with the title
"CHIP-8 I/O". It can be positioned, minimized or maximized independent of the
rest of the app. Within the window are the following widgets:

* The display, represented as a QLabel containing a QPixmap. It presents the
CHIP8 (32x64) or SCHIP (64x128) display as an array of square pixels.

* The keypad, represented as a grid of specialized QPushbuttons.

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
    'sound'
]

from typing import List, Tuple

'''
Import needed PyQt classes.
'''

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QSize,
    QRect,
    QTimer
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
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QToolButton,
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
    Implement scrolling. The same technique is used in all three scrolls. We
    define a rectangle the current size of the screen, except displaced in
    the opposite direction to the scroll (e.g. to the left when scrolling
    right). We use that as the argument to the QImage.copy() method, which
    returns a new QImage containing pixels from the current image where it
    falls inside the rectangle, and black pixels where the rectangle falls
    outside.

    It's just really cool that the Qt folks thought to properly support
    negative X/Y values like this.
    '''
    def displace_rect( self, rect, x_diff, y_diff ) :
        '''
        If one only calls QRect.setX(), it helpfully extends the rectangle
        to make its area larger. This function makes a new rect that is
        simply displaced, same width and height.
        '''
        return QRect( rect.x()+x_diff, rect.y()+y_diff, rect.width(), rect.height() )

    def scroll_right( self ) :
        P = self.P
        offset = P * ( 4 if self.extended_mode else 2 )
        new_rect = self.displace_rect( self.image.rect(), -offset, 0 )
        new_image = self.image.copy( new_rect )
        self.image = new_image
        self.setPixmap( QBitmap.fromImage( self.image ) )

    def DBGPRECT( self, rect, title ) :
        print( title )
        print( 'rect x={} y={} w={} h={}'.format(rect.x(),rect.y(),rect.width(),rect.height() ) )

    '''
    Implement scroll-left. Same technique as scroll-right.
    '''
    def scroll_left( self ) :
        P = self.P
        offset = P * ( 4 if self.extended_mode else 2 )
        new_rect = self.displace_rect( self.image.rect(), offset, 0 )
        new_image = self.image.copy( new_rect )
        self.image = new_image
        self.setPixmap( QBitmap.fromImage( self.image ) )

    '''
    And scroll-down.
    '''
    def scroll_down( self, rows ) :
        P = self.P
        offset = P * rows
        new_rect = self.displace_rect( self.image.rect(), 0, -offset )
        new_image = self.image.copy( new_rect )
        self.image = new_image
        self.setPixmap( QBitmap.fromImage( self.image ) )


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
            new_size = QSize(
                self.P * ( 128 if self.extended_mode else 64 ),
                self.P * ( 64 if self.extended_mode else 32 )
                )
            self.image = QImage( new_size, QImage.Format_RGB32 )
            self.clear()
        super().resizeEvent( event )

'''

Define one keypad button. It is instantiated with its numeric code 0-16.
From the code it derives is letter 0-F.

It sets its size policy so it will expand to fill all available space
in its layout.

'''

class KeyPadButton( QToolButton ) :
    def __init__( self, code:int, parent = None ) :
        super().__init__( parent )
        self.code = code
        self.letter = '{:1X}'.format( code )
        self.setText( self.letter )
        self.latched = False
        spolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        spolicy.setHorizontalStretch( 1 )
        spolicy.setVerticalStretch( 1 )
        self.setSizePolicy( spolicy )

    def mousePressEvent( self, event ) :
        self.latched = int(Qt.ShiftModifier) == int( event.modifiers() )
        super().mousePressEvent( event )

    '''
    Handle a keyboard keystroke mapped to this button.
    Set our "down" status true. This changes the background color so you
    see the button was triggered. It does not send our pressed signal, so
    generate that manually.

    Start a 50ms one-shot timer that will call key_up below.
    '''
    def keyboard_down( self ) :
        self.setDown( True )
        self.latched = False
        self.pressed.emit()
        QTimer.singleShot( 50, self.keyboard_up )
    '''
    On receipt of the timer kick, set our Down status off and emit our
    released signal.
    '''
    def keyboard_up( self ) :
        self.released.emit()
        self.setDown( False )

'''

Define the keypad as a 4x4 grid of KeyPadButtons. Capture the "pressed" and
"release" signals of each button and use them to keep track of which button
is currently down, or -1 if none of them are.

Keep a list of the 16 buttons so they can be referenced from the
DisplayWindow during a keyPressEvent.

'''

class KeyPad( QWidget ) :
    def __init__(self, parent=None) :
        super().__init__( parent )
        '''
        This variable records the currently-down button value, or -1.
        This is what is polled by the key_test() function called by
        the Emulator.
        '''
        self.pressed_code = -1
        '''
        This variable records whether the button was shift-clicked to latch
        it down. If so we keep a reference to the button for use later.
        '''
        self.latched_code = False
        self.latched_button = None # type KeyPadButton
        '''
        List the 16 buttons in order so they can be called individually.
        '''
        self.buttons = []
        '''
        Set up the button layout grid. min_size ensures that the
        button-squares are at least that many pixels wide.
        '''
        grid = QGridLayout( )
        self.setLayout( grid )
        min_size = 32
        for n in range( 4 ) :
            grid.setColumnMinimumWidth( n, min_size )
            grid.setRowMinimumHeight( n, min_size )
        '''
        Create the buttons and lay them out.
        '''
        for code in range(16) :
            kp_button = KeyPadButton( code )
            self.buttons.append( kp_button )
            grid.addWidget(
                kp_button,
                code // 4,
                code % 4 )
            kp_button.pressed.connect( self.button_down )
            kp_button.released.connect( self.button_up )

    def button_down( self ) :
        '''
        This slot receives the pressed signal from any of the 16 buttons.
        Note which one, so when the emulator queries the keypad we can reply.
        Also note if it was shift-clicked to latch it, in which case we
        ignore button_up status.

        This uses the QObject.sender() method to return a reference to the
        object (which we are sure is a KeyPadButton) that initiated the
        signal.
        '''
        that_button = self.sender()
        self.pressed_code = that_button.code
        if that_button.latched :
            self.latched_code = True
            self.latched_button = that_button

    def button_up( self ) :
        '''
        This slot receives the released signal from any of the 16 buttons.
        If the key was not latched, then just set -1 as our current value.

        When the key was latched, do not clear our value, and access the
        button and set its "down" status so it stays visibly down.
        '''
        if not self.latched_code :
            self.pressed_code = -1
        else :
            self.latched_button.setDown( True )

    def clear_latch( self ) :
        '''
        Clear any latched button state -- called on a keypad read inst.
        '''
        if self.latched_code :
            self.latched_button.setDown( False )
            self.latched_code = False
            self.pressed_code = -1

    def keyboard_hit ( self, button ) :
        '''
        DisplayWindow calls here when the user hits a keyboard key that is
        mapped to a keypad button. If a key is already down (due to mouse
        action, or due to the user hitting a second key before the oneshot
        timer used by the KeyPadButton class has expired) just ignore it.
        Otherwise, pass it on to the button concerned.
        '''
        if self.pressed_code == -1 :
            self.latched_code = False
            that_button = self.buttons[ button ]
            that_button.keyboard_down()

'''
Define a custom combo-box widget which presents the user a choice of
keyboard mappings for the keypad. A mapping is a string of 16 characters
that are mapped to the keypad buttons 0-15 by the DisplayWindow keyPressEvent
handler.

A list of default maps is passed to the initializer and used to populate
the combobox. We also check the settings to see if we have saved
any user-defined key maps, and add them to the choices.

'''

class KeyChoiceCombo( QComboBox ) :
    def __init__( self, map_list, settings, parent=None ) :
        super().__init__( parent )
        '''
        Save the default maps for reference during shutdown.
        '''
        self.default_maps = map_list
        '''
        Populate the choices with defaults.
        '''
        for string in map_list :
            self.addItem( string )
        '''
        Look in settings for a list of other key maps. If there are
        none, settings.beginArray returns 0.
        '''
        entries = settings.beginReadArray( 'display_page/keymap' )
        for j in range( entries ) :
            settings.setArrayIndex( j )
            new_map = settings.value( 'map' )
            self.addItem( new_map )
        settings.endArray()
        '''
        Add a separator and two special commands to the end of the list.
        This is really not good UI design, but the alternative would be
        to have a whole menu command set and blah blah.
        '''
        self.insertSeparator( 99 )
        self.addItem( 'Enter new map' )
        self.addItem( 'Delete map' )
        '''
        Possibly we recorded the last list index in the settings?
        If not, default to 0.
        '''
        self.setCurrentIndex( settings.value( 'display_page/map_index', 0 ) )
        '''
        Keep track of the last "real" index the user selected and the
        map string to which it corresponds.
        '''
        self.last_good_index = self.currentIndex()
        self.current_map = self.currentText()
        '''
        Hook up the activated (user-selected-choice) signal to our own
        method where we look for the choice of commands.
        '''
        self.activated.connect( self.new_choice )

    '''
    Upon the user actually selecting a map from the combobox, look to
    see if the choice is one of our two commands, or just a different map.
    '''
    def new_choice(self, index ) :
        if self.itemText( index ) == 'Enter new map' :
            '''
            The choice is to enter a new map. Get text from the user.
            If the user clicks Cancel or hits ESC, new_map is null.
            '''
            ( new_map, ok )  = QInputDialog.getText(
                self,
                'Map keys to keypad',
                '16 characters')
            test_set = set( new_map )
            if ( len( new_map ) == 16 ) and len( test_set ) == 16 :
                '''
                User indeed entered exactly 16 unique characters.
                Insert that into the combobox as a choice, following
                the default 4. Set the current index to it, and set it
                as our current map string.
                '''
                self.insertItem( 4, new_map )
                self.setCurrentIndex( 4 )
                self.last_good_index = 4
                self.current_map = new_map
            else:
                '''
                The user cancelled out or didn't enter 16 unique chars.
                Force the combobox back to the last good index. The
                current_map has not changed.
                '''
                self.setCurrentIndex( self.last_good_index )
        elif self.itemText( index ) == 'Delete map' :
            '''
            The choice is to delete an existing map. Get text from the
            user. If the user cancels out or enters nothing, do nothing.
            '''
            ( old_map, ok )  = QInputDialog.getText(
                self,
                'Delete which map',
                'Leading characters')
            if ok and len( old_map ) > 2 :
                '''
                Scan our current list of choices looking for matching
                leading characters. Don't scan down to the two commands
                at the end. If a match is found, delete that item and
                set the current index to 0.
                '''
                for i in range( self.count() - 2 ) :
                    if self.itemText( i ).startswith( old_map ) :
                        self.removeItem( i )
                        self.last_good_index = 0
                        self.setCurrentIndex( 0 )
                        self.current_map = self.itemText( 0 )
                        break
        else :
            '''
            The user has selected one of the map entries. Note that.
            '''
            self.last_good_index = index
            self.current_map = self.itemText( index )
    '''
    It's time to shut down. Save our current index.
    Then run through our current set of choices, and
    any that are not in the default set, write into an array in settings.
    '''
    def shutdown( self, settings ) :
        settings.setValue( 'display_page/map_index', self.currentIndex() )
        settings.beginWriteArray( 'display_page/keymap' )
        array_index = 0
        for j in range( self.count() -3 ) :
            that_map = self.itemText( j )
            if that_map not in self.default_maps :
                settings.setArrayIndex( array_index )
                settings.setValue( 'map', that_map )
                array_index += 1
        settings.endArray()

'''

Define the main window in which our stuff is displayed.
When instantiated, it instatiates everything else.

'''
class DisplayWindow( QWidget ) :
    def __init__( self, settings ) :
        super().__init__( None )
        '''
        Save the settings for the closeEvent.
        '''
        self.settings = settings

        '''
        Set our layout to a vbox.
        '''
        vbox = QVBoxLayout()
        self.setLayout( vbox )
        '''
        Instantiate the screen.
        '''
        self.screen = Screen()
        vbox.addWidget( self.screen, 10 )#, Qt.AlignTop | Qt.AlignLeft

        '''
        Instantiate the keypad.
        '''
        self.keypad = KeyPad()
        vbox.addWidget( self.keypad, 9 )#, Qt.AlignTop | Qt.AlignRight

        '''
        Define the default key_maps. A key map is a string of 16
        unique characters which are mapped to the 16 keypad keys.
        The following four maps are always present, but if the user
        defined others, they are saved in settings and restored.
        '''
        self.key_maps = [
            '1234qwerasdfzxcv', # left side, right or left hand
            '7890uiopjkl;m,.?', # right side, left hand
            '4567ertysdfgzxcv', # middle, right hand
            '0123456789abcdef'  # literal
            ]

        '''
        Instantiate the key-mapping combobox, a very clever combobox
        it is, too. Pass it the list of default key maps and the settings
        so it can recover any custom maps.
        '''
        self.key_mapper = KeyChoiceCombo( self.key_maps, settings )
        hbox = QHBoxLayout( )
        hbox.addStretch()
        hbox.addWidget( self.key_mapper )
        vbox.addLayout( hbox )
        '''
        Set the window title
        '''
        self.setWindowTitle( "CHIP-8 I/O" )
        '''
        Set the window's focus policy to click-to-focus. Don't want tabbing
        between the top level windows.
        '''
        self.setFocusPolicy( Qt.ClickFocus )

        '''
        With all widgets created, resize and position the window
        from the settings.
        '''
        self.resize( settings.value( "display_page/size", QSize(600,400) ) )
        self.move(   settings.value( "display_page/position", QPoint(100, 100) ) )

    '''

    Implement a keyPressEvent handler in order to direct keyboard keys to the
    keypad buttons. Get the actual character (not an integer Qt enum) from the
    event.text(). Test that against the current key map maintained in the
    key_mapper. If it is there, we have a hit and its index is the keypad
    button to activate. Call KeyPad.keyboard_hit( keynumber )
    to tell it to act. What happens then is not our business...

    '''
    def keyPressEvent(self, event):
        key = event.text()
        index = self.key_mapper.current_map.find( key )
        if index != -1 :
            event.accept() # yes, we handle this event
            self.keypad.keyboard_hit( index )


    '''
    Override the built-in closeEvent() method to save our geometry and key
    map in the settings.
    '''
    def closeEvent( self, event ) :
        self.settings.setValue( "display_page/size", self.size() )
        self.settings.setValue( "display_page/position", self.pos() )
        self.key_mapper.shutdown( self.settings )
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
    global OUR_WINDOW, SCREEN, KEYPAD
    '''
    Create the window and everything in it.
    Pass the settings object for its use.
    '''
    OUR_WINDOW = DisplayWindow( settings )
    '''
    Set up for quick access to screen and keypad
    '''
    SCREEN = OUR_WINDOW.screen
    KEYPAD = OUR_WINDOW.keypad
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
    pixel_list = []
    '''
    Set bit masks for x and y based on the screen resolution.
    '''
    y_mask = 0x003F if get_mode() else 0x001F
    x_mask = 0x007F if get_mode() else 0x003F

    bit_mask = 0x0080
    sprite = sprite_bytes
    if 32 == len(sprite) :
        '''
        To reduce the special-casing, convert an SCHIP 16x16 sprite from
        a list of 32, 8-bit ints, to a list of 16, 16-bit ints, adjusting
        the bit_mask accordingly.
        '''
        bit_mask = 0x8000
        sprite = []
        for i in range(0, 32, 2) :
            sprite.append( ( sprite_bytes[i] << 8) | sprite_bytes[i+1] )
    '''
    Keep the x- and y-coordinates in range, wrapping at the limit, by
    masking them after each increment.
    '''
    y_coord = y & y_mask
    for word in sprite :
        '''
        Sweep the bit_cursor across the current byte (or word),
        incrementing the x-coordinate at each bit.
        '''
        x_coord = x & x_mask
        bit_cursor = bit_mask
        while bit_cursor : # is not zero,
            if word & bit_cursor :
                pixel_list.append( ( x_coord, y_coord ) )
            bit_cursor >>= 1
            x_coord = (x_coord + 1) & x_mask
        '''
        Increment the y-coordinate for each byte/word.
        '''
        y_coord = (y_coord + 1) & y_mask

    '''
    Paint the white pixels we found and exit.
    '''
    hit = SCREEN.paint_pixel_list( pixel_list )
    QTest.qWait(10)
    return hit

'''
Clear the emulated screen to all-black.
'''

def clear( ) -> None :
    SCREEN.clear()

'''
Scroll the emulated screen down N lines.
? what if mode is now CHIP-8? force SCHIP? or ignore?
Decision: just do it. Because most likely, any existing program
that uses this, has already executed a HIGH to enter SCHIP mode.
'''

def scroll_down( n:int ) -> None :
    SCREEN.scroll_down( n )

'''
Scroll the emulated screen 2 or 4 columns left, depending on mode.
'''

def scroll_left( ) -> None :
    SCREEN.scroll_left()

'''
Scroll the emulated screen 2 or 4 columns right, depending on mode.
'''

def scroll_right( ) -> None :
    SCREEN.scroll_right()

'''
Turn the emulated beeper/tone on or off.
'''

def sound( on : bool ) -> None :
    pass

'''
Return the value of a key that is currently pressed, if any; else return
-1. This method is called for the key-testing instructions, SKE and SKNE.
It does not clear a latched key status.
'''

def key_test(  ) -> int :
    return KEYPAD.pressed_code

'''
Return the value of a key that is currently pressed, if any; else return
-1. this method is called for the LD Vt, K instruction and it does clear
a latched value if there is one.
'''

def key_read( ) -> int :
    key_code = KEYPAD.pressed_code
    KEYPAD.clear_latch()
    return key_code

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#
# Enter the wonderful world of unit test...
#

if __name__ == '__main__' :
    from PyQt5.QtWidgets import QApplication
    args = []
    the_app = QApplication( args )
    settings = QSettings()
    #settings.clear()
    initialize(settings)
    OUR_WINDOW.show()
    sprite = [0x20,0x70,0x70,0xF8,0xD8,0x88] # rocket ship
    draw_sprite( 16, 8, sprite )

    key_read()
    the_app.exec_()
