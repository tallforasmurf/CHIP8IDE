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

             CHIP-8 IDE Memory Window

The Memory window gives the user control over the emulator and visibility
into the emulator state. It is called by the chip8ide module at initialize()
to create the window and its contents as Qt objects. After creation, the
window objects respond to Qt events from user actions.

The window is an independent (that is, parent-less) window with the title
"CHIP-8 Emulator". It can be positioned, minimized or maximized independent
of the rest of the app. During initialization it sets its geometry from the
saved settings.

Within the window are the following widgets:

The Memory display is a table showing the 4096 bytes of emulated memory in
128 rows of 32 bytes. When the emulator is not running, the user can edit
individual bytes by double-clicking a byte and entering a new value. When the
emulator has been running and stops, the Memory display scrolls so that the
line containing the current PC address is visible.

Below the memory is a display of the call stack of subroutine return addresses.

Next lower is the Register display, showing the contents of the 20 CHIP-8
registers (v0-vF, PC, I, ST, DT). When the emulator is not running, the user
can edit the contents of these, and thus affect the execution of the program
when it resumes. (One use for this ability: because the DT and ST are not
auto-decremented during single-step operation, the user could set them to
simulate a change.)

Under the Registers, running the width of the window, is the Status line
which displays the reason the emulator stopped.

The following controls are at the bottom:

The RUN/STOP switch is a QPushbutton in one of two states. When the Emulator
is not running, the button reads RUN. When clicked, the button toggles to
read STOP, and the emulator begins free-running execution of the program in
memory, starting from the current PC. This is done in a separate thread.

Clicking STOP terminates execution and returns the button to read RUN.

The STEP button is a QPushbutton that is enabled when the emulator is not
running. Clicking it causes the emulator to execute a single instruction at
the current PC and then stop.

"Inst/tick" is a QSpinBox (numerical entry widget) that allows the user to
set the maximum number of emulated instructions that can be executed per
1/60th-second "tick" of the delay timer. The actual COSMAC VIP probably
executed around 100 instructions per tick (about 2500/sec). On modern hardware
the emulator can exceed that by orders of magnitude, and this gives the user
control over how fast an emulated program runs.

Coding note:

Because this is a module, rather than a singleton class definition, it is
necessary to code Pascal-style, defining all names before they are used.

'''

'''

Define this module's public API, which consists of

* the initialize() function, called once by chip8ide.py to create the window.
* the connect_signal() function that receives the Quit signal from the main window.

Really, that's it. initialize() opens the window and away we go.

'''
__all__ = [ 'initialize', 'connect_signal' ]


'''
Import the chip8 module for access to the memory, registers and call stack.
Import the display module just so we can call display.sound().
Import chip8util for access to the font and RSSButton class.
'''

import chip8
import display
import chip8util

'''
Import needed Qt names.
'''

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QAbstractListModel,
    QAbstractTableModel,
    QCoreApplication,
    QItemSelection,
    QItemSelectionModel,
    QMutex,
    QPoint,
    QSettings,
    QSize,
    QThread,
    QTimer,
    QWaitCondition
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QIcon,
)

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QSizePolicy,
    QSpinBox,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtTest import QTest


'''
Some widgets require a QBrush with black color for background and a
white QBrush for foreground.
'''
BLACK_BRUSH = QBrush( QColor( "Black" ) )
WHITE_BRUSH = QBrush( QColor( "White" ) )

'''
Define the RUN/STOP button. The base RSSButton class sets its visual properties
including a mono font, and sizes it to a width of 8 ems.

RUN/STOP has also the checkable property, which makes it a toggle rather than
a simple pushbutton; and the initial text of "RUN!". The on_text of "STOP" is
set by the code that handles the "toggled" signal.
'''

class RunStop( chip8util.RSSButton ) :
    def __init__( self, parent=None ) :
        super().__init__( parent )

        self.setCheckable( True )

        self.off_text = ' RUN!  '
        self.on_text =  ' STOP  '
        self.setText( self.off_text )


'''
The RUN/STOP and STEP buttons are stored as globals so that other
widgets can easily refer to them. (As opposed to being members of
some class, like the main window.)

We cannot instantiate a button until the App is created, so that has
to wait until our initialize() function (below) is called.
'''
RUN_STOP_BUTTON = None # type: RunStop
STEP_BUTTON = None # type: chip8util.RSSButton

'''
Define the Instructions/tick widget as a QSpinbox (numeric entry widget)
with a minimum of 1, max of 5000 and steps of 1. One of these
will be instantiated when we initialize().

A reference to it is stored in INST_PER_TICK for easy access.

The start value is taken from saved settings, remembered from the previous
session.
'''

class InstPerTick( QSpinBox ) :
    def __init__( self, start_value:int ) -> None :
        super().__init__( None )
        self.setMinimum( 1 )
        self.setMaximum( 100 )
        self.setValue( start_value )
        self.setSingleStep( 1 )

INST_PER_TICK = None # type: InstPerTick

'''
    MEMORY DISPLAY

The display of emulated memory is implemented using a Qt Table. In the world
of Qt MVC (model-view-controller) programming, a table has three parts:

* The QTableView object controls the visual features of the table.
* The table "model" stores the data for the view to display, and delivers
  that data on request, whenever the view needs to paint one cell.
* An "item delegate" is a dialog widget that is created by the view when
  the user wants to edit the value in a cell of the table.

To begin, define the Memory display as a QTableView. The table dimensions are
MEM_TABLE_COLS x MEM_TABLE_ROWS, which must equal 4096. These are stored as
globals so they can be tinkered with, but there seems little reason not to
use 32 x 128.

'''

MEM_TABLE_COLS = 32
MEM_TABLE_ROWS = int( 4096/MEM_TABLE_COLS )

class MemoryDisplay( QTableView ) :

    def __init__( self, parent=None ) :

        super().__init__( parent )
        '''
        Establish our interactive properties:
        - no "corner button" for "select-all"
        - no grid lines
        - no sort based on clicking a column header
        - no word-wrap, not that that would be an issue
        - scrolling, if needed, by whole cells not pixels
        - selection, when enabled, only one cell at a time,
            i.e. no multiple selections by drag, shift-click etc.
        '''
        self.setCornerButtonEnabled(False)
        self.setShowGrid(False)
        self.setSortingEnabled(False)
        self.setWordWrap(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        '''
        Associate the item delegate for editing (defined below)
        '''
        self.setItemDelegate( MemoryEdit() )
        '''
        Try to get Qt to give the table appropriate space, using
        manual tweaks of various properties - yechhh.
        '''
        self.setMinimumSize(
            QSize(
                chip8util.MONOFONT_METRICS.width( '00FF' * ( MEM_TABLE_COLS-1 ) ),
                chip8util.MONOFONT_METRICS.lineSpacing() * 30
                )
            )
        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
            )
        '''
        Instantiate the table model (data supplier) and connect it.
        '''
        mm = MemoryModel( self )
        self.setModel( mm )


    '''
    Define a scroll-to-PC method, taking an emulated PC value, selecting it
    and ensuring it is visible on the screen.

    This involves a trip through the MVC architecture...
    '''
    def scroll_to_PC( self, PC:int ) -> None :
        '''
        Define a range of model indexes that span the first and second bytes
        of the instruction at the PC. Rarely, this may be the last byte in
        one row and the first byte of the next row.
        '''
        start_index = self.model().createIndex(
            int( PC / MEM_TABLE_COLS ),
            int( PC % MEM_TABLE_COLS ) )
        end_index = self.model().createIndex(
            int( (PC+1) / MEM_TABLE_COLS ),
            int( (PC+1) % MEM_TABLE_COLS ) )
        '''
        Position the table so the (first) row is centered.
        '''
        self.scrollTo( start_index, QAbstractItemView.PositionAtCenter )
        '''
        Create an Item Selection covering the range of those two cells.
        '''
        sel_item = QItemSelection( start_index, end_index )
        '''
        Using our ItemSelectionModel, do the selection?
        '''
        self.selectionModel().select( sel_item, QItemSelectionModel.ClearAndSelect )

'''
Define the memory table model, the object that contains the contents of
memory and delivers them as required by the table view. For example if the
user scrolls the table up, it will call the model to get values for the cells
as they are revealed.

One object of this class is created during the View initialization, above.
'''

class MemoryModel( QAbstractTableModel ) :

    def __init__( self, parent=None ) :
        super().__init__( parent )

    '''
    The flags method tells Qt what the user can do with the table. It is
    called to check the permissions of each cell as it is created. We allow
    editing but only if the emulator is stopped.
    '''
    def flags( self, index ) :
        return Qt.ItemNeverHasChildren \
               | Qt.ItemIsSelectable \
               | Qt.ItemIsEditable \
               | Qt.ItemIsEnabled

    '''
    Return the fixed dimensions of the memory table, defined in globals.
    '''
    def rowCount( self, index ) :
        if index.isValid() : return 0
        return MEM_TABLE_ROWS

    def columnCount( self, index ) :
        if index.isValid() : return 0
        return MEM_TABLE_COLS

    '''
    The data() method returns data for one cell in various "roles":
        display: return 2 hex characters of this byte
        tooltip: return the address of the byte
        font: MONOFONT
        background: BLACK_BRUSH
        foreground: WHITE_BRUSH
    '''
    def data( self, index, role ) :
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole :
            return '{0:02X}'.format( chip8.MEMORY[ (row * MEM_TABLE_COLS) + col ] )
        elif role == Qt.ToolTipRole :
            return '{0:04X}'.format( (row * MEM_TABLE_COLS) + col )
        elif role == Qt.FontRole :
            return chip8util.MONOFONT
        elif role == Qt.ForegroundRole :
            return WHITE_BRUSH
        elif role == Qt.BackgroundRole :
            return BLACK_BRUSH
        return None

    '''
    The headerData() method returns data for the horizontal and
    vertical headers. For the horizontal (column) header, show
    the hex digits 0..F. For the vertical, show the starting address.

    As with the data cells, make the format white text on black.

    '''
    def headerData( self, section, orientation, role ) :
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return '{0:02X}'.format( section ) # ' 0', ' 1'...
            else :
                return '{0:04X}'.format( MEM_TABLE_COLS * section ) # 0000, 0010...
        elif role == Qt.FontRole :
            return chip8util.MONOFONT
        elif role == Qt.ForegroundRole :
            return BLACK_BRUSH
        elif role == Qt.BackgroundRole :
            return WHITE_BRUSH

    '''
    The setData() method stores a byte obtained by the MemoryEdit delegate.
    The delegate's input mask ensures the input is 2 uppercase hex digits. If
    this function returns False, no change is made. When the update is
    successful it returns True and the table display updates only the cell
    selected by the index row/col.
    '''
    def setData( self, index, value, role ) :
        # convert to integer from base-16 characters
        number = int( value, 16 )
        # store in memory
        row = index.row()
        col = index.column()
        chip8.MEMORY[ ( row * MEM_TABLE_COLS) + col ] = number
        return True

'''
Define an item delegate to perform editing when a byte of memory is
double-clicked. In the world of Qt MVC, a styled item delegate manages the
editing of a table item. It has to implement three methods:

* createEditor() creates a widget to do the editing, in this case,
  a QLineEdit with an input mask.

* setEditorData() loads the editor widget with initial data

* setModelData() takes the edited data and stores it in the model.

With this mechanism in place it is quite easy to edit the memory view.
Double-click one byte, type 2 hex digits, hit TAB. The data is stored and the
following byte is opened for editing. Hit return or escape to stop editing.

'''
class MemoryEdit( QStyledItemDelegate ) :
    def createEditor( self, parent, style, index ):
        '''
        Create a QLineEdit which will permit the input of exactly two
        hexadecimal characters which are automatically uppercased.
        '''
        line_edit = QLineEdit( parent )
        line_edit.setInputMask( '>HH' )
        line_edit.setFont( chip8util.MONOFONT )
        return line_edit

    def setEditorData( self, line_edit, index ):
        '''
        Load the newly-created line edit with the byte value from the
        selected memory cell. The table index object has a convenient
        data() method that calls on the data() method of the table model with
        the Qt.DisplayRole. That conveniently returns two uppercase hex digits,
        just what we need. See MemoryModel.data() above.
        '''
        line_edit.setText( index.data( Qt.DisplayRole ) )

    def setModelData( self, line_edit, model, index):
        '''
        The user has hit Enter or Tab to complete editing the LineEdit
        (rather than hitting escape to cancel). Put the entered data
        into the model (and emulated memory) with model.setData.
        '''
        model.setData( index, line_edit.text(), Qt.DisplayRole )

'''
Define the register display as another QTable, complete with a View, a Model,
and an item delegate for editing. This table has only a header row and one
data row.
'''

class RegisterDisplay( QTableView ) :

    def __init__ ( self, parent=None ) :
        super().__init__( parent )
        '''
        Establish our interactive properties:
        * no corner button
        * do show a grid
        * no sorting (hardly relevant given only 1 row)
        * no word wrap (also not a real issue)
        * select only single items
        '''
        self.setCornerButtonEnabled( False )
        self.setShowGrid( True )
        self.setSelectionMode( QAbstractItemView.SingleSelection )
        '''
        Try to get Qt to give the table appropriate space, using
        manual tweaks of various properties - yechhh. Hey, if anybody
        wants to fix this so the register display sizes itself appropriately
        without these tweaks, puh-leeeze put in a pull request!
        '''
        import sys
        minw = 24 if sys.platform.startswith('win') else ( 22 if sys.platform.startswith('dar') else 20 )
        self.setMinimumWidth( chip8util.MONOFONT_METRICS.width( '00FF' * minw ) )
        self.setMaximumHeight(chip8util.MONOFONT_METRICS.lineSpacing() * 4 )

        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            )
        '''
        Instantiate the model and connect it to this view.
        '''
        self.setModel( RegisterModel( self ) )
        '''
        Allow editing
        '''
        self.setItemDelegate( RegisterEdit() )


class RegisterModel( QAbstractTableModel ) :

    def __init__ ( self, parent ) :
        super().__init__( parent )
        '''
        Define a dict relating column header text to column numbers.
        Note the column numbers should in turn match up to the values of
        the chip8.R enum.
        '''
        self.headers = {
            0: 'v0', 1: 'v1', 2: 'v2', 3: 'v3',
            4: 'v4', 5: 'v5', 6: 'v6', 7: 'v7',
            8: 'v8', 9: 'v9', 10: 'vA', 11: 'vB',
            12: 'vC', 13: 'vD', 14: 'vE', 15: 'vF',
            16: ' I', 17: 'DT', 18: 'ST', 19: 'PC'
            }

    '''
    As with the Memory display, we allow editing if the emulator is stopped,
    which the MasterWindow ensures by calling beginResetModel before the
    emulator starts.
    '''
    def flags( self, index ) :
        return Qt.ItemNeverHasChildren \
               | Qt.ItemIsSelectable \
               | Qt.ItemIsEditable \
               | Qt.ItemIsEnabled

    '''
    There is exactly 1 row and 20 columns forever.
    '''
    def rowCount( self, index ) :
        if index.isValid() : return 0
        return 1
    def columnCount( self, index ) :
        if index.isValid() : return 0
        return len( self.headers )

    '''
    The data method returns data under various roles.
        display: return 2 hex characters of this register
        tooltip: return the name of the register
        font: MONOFONT
        do not return anything for background/foreground, let it default.
    '''
    def data( self, index, role ) :
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole :
            pattern = '{0:02X}'
            if col == chip8.R.P or col == chip8.R.I :
                pattern = '{0:03X}'
            return pattern.format( chip8.REGS [ col ] )
        elif role == Qt.ToolTipRole :
            return 'register {}'.format( self.headers[ col ] )
        elif role == Qt.FontRole :
            return chip8util.MONOFONT
        return None
    '''
    Headerdata returns the names of the registers for horizontal. For
    vertical, the one row header, return "Regs" Let fonts and colors default.
    '''
    def headerData( self, section, orientation, role ) :
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return self.headers[ section ]
            else :
                return 'Regs'
        elif role == Qt.FontRole :
            return chip8util.MONOFONT
        return None
    '''
    The setData method stores a value obtained by the RegisterEdit delegate.
    The delegate's input mask ensures the input is either 2 or 3 uppercase
    hex digits. See also remarks on setData of the memory model above.
    '''
    def setData( self, index, value, role ) :
        # convert to integer from base-16 characters
        number = int( value, 16 )
        # store in the emulator register bank
        col = index.column()
        chip8.REGS[ col ] = number
        return True

'''
Define a styled item delegate for manual editing of the register display.
See comments on MemoryEdit, above.
'''
class RegisterEdit( QStyledItemDelegate ) :
    def createEditor( self, parent, style, index ):
        '''
        Create a QLineEdit which will permit the input of either
        two or three uppercase hexadecimal characters.
        '''
        col = index.column() # register number
        line_edit = QLineEdit( parent )
        line_edit.setInputMask(
            '>HHH' if (col == chip8.R.I or col == chip8.R.P) else '>HH'
        )
        line_edit.setFont( chip8util.MONOFONT )
        return line_edit

    def setEditorData( self, line_edit, index ):
        '''
        Load the newly-created line edit with the byte value from the
        selected register, using the convenient data() method of the index
        object, that calls on the data() method of the table model, which
        given Qt.DisplayRole conveniently returns two or three uppercase hex
        digits.
        '''
        line_edit.setText( index.data( Qt.DisplayRole ) )

    def setModelData( self, line_edit, model, index):
        '''
        The user did not cancel out of the edit but hit return or tab.
        Store the entered data into the model, which puts it in the
        emulated register for this column.
        '''
        model.setData( index, line_edit.text(), Qt.DisplayRole )

'''
Define the Call Stack widget. Rather than a table we use a QListView. Like a
table view, a list view is based on a data model, in this case a model based
on the emulated call stack, a list of zero to twelve return addresses
maintained by the emulator.
'''

class CallStackDisplay( QListView ) :

    def __init__  ( self, parent=None ) :
        super().__init__( parent )
        '''
        Set our properties: a horizontal list with no user interaction
        '''
        self.setFlow( QListView.LeftToRight )
        self.setSelectionMode( QAbstractItemView.NoSelection )
        self.setViewMode( QListView.ListMode )
        self.setMovement( QListView.Static )
        '''
        Try to get Qt to give the table appropriate space, using
        manual tweaks of various properties - yechhh.
        '''
        self.setMinimumWidth( chip8util.MONOFONT_METRICS.width( '00FF' * 20 ) )
        self.setMaximumHeight(chip8util.MONOFONT_METRICS.lineSpacing() * 2 )
        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Preferred, QSizePolicy.Preferred )
            )
        '''
        Create the singleton model and attach it as our model
        '''
        self.setModel( CallStackModel() )

class CallStackModel( QAbstractListModel ) :

    def __init__( self, parent=None ) :
        super().__init__( parent )

    '''
    In Qt MVC, models provide logical dimensions and data. For this list
    model there is only ever 1 column, and the Call Stack always has 12 items
    which are its "rows".
    '''
    def rowCount( self, index ) :
        if index.isValid() : return 0
        return 12
    '''
    A Model returns "flags" that let the view know what can be done with
    data items. In this case, nothing at all.
    '''
    def flags(self, index) :
        return Qt.ItemNeverHasChildren
    '''
    A Qt Model returns data under several "roles". The View uses these items
    to build the display.
    '''
    def data( self, index, role ) :
        '''
        Collect the stack position for use later. The for a Qt list, the
        desired item number is in index.row(). (I guess a list is a
        one-column table?)
        '''
        item_number = index.row()
        '''
        The emulated stack might have zero, one to twelve items. Note whether
        the requested item is in the stack or just empty.
        '''
        stack_item_exists = item_number < len( chip8.CALL_STACK )
        '''
        Respond with data to the various "roles"
        '''
        if role == Qt.DisplayRole :
            '''
            For the display role, return either an address or 4 spaces.
            '''
            if stack_item_exists :
                return '{0:04X}'.format( chip8.CALL_STACK[ item_number ] )
            else :
                return '    '
        elif role == Qt.FontRole :
            '''
            The font is always the Mono font
            '''
            return chip8util.MONOFONT
        elif role == Qt.BackgroundRole :
            '''
            The background of occupied slots is black, empty slots are white.
            '''
            if stack_item_exists :
                return BLACK_BRUSH
            else :
                return WHITE_BRUSH
        elif role == Qt.ForegroundRole:
            '''
            The foreground (text) of occupied slots is white, and since the
            empty slots are blank, we don't care what text color.
            '''
            return WHITE_BRUSH
        elif role == Qt.ToolTipRole :
            '''
            For the tooltip role return a specific or generic string.
            '''
            if stack_item_exists :
                if item_number == 0 :
                    return 'First subroutine return address'
                else :
                    return 'Nested subroutine return address'
            else :
                return 'Call stack display'
        return None

'''
Define the status line, basically a styled QLabel. The content is "rich text"
although all the messages that are displayed are plain ASCII. We make it
"rich" so we can force a bold font.

Note that we do NOT set the chip8util.MONOFONT. On MacOS, the default system
mono font does not have a bold variant. However, the default proportional
font does have bold on all platforms, and is appropriate for general message
text.
'''

class StatusLine( QLabel ):
    def __init__( self, parent=None ) :
        super().__init__( parent )
        self.setLineWidth( 2 )
        self.setMidLineWidth( 1 )
        self.setFrameStyle( QFrame.Box | QFrame.Sunken )
        self.setMinimumWidth(chip8util.MONOFONT_METRICS.width( 'F') * 80 )
        self.setMaximumHeight(chip8util.MONOFONT_METRICS.lineSpacing() * 2 )
        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
            )
    '''
    Override setText() to add bold markup.
    '''
    def setText( self, msg_text ) :
        super().setText( '<b>'+msg_text+'</b>' )

STATUS_LINE = None # type: StatusLine

'''
Here we create the entire Memory window. It is a QWidget with no parent,
hence an independent window.

The various widgets declared above are all instantiated during the
initialization code of this object. Note that the chip8 module should have
been initialized before this module so that the memory and register displays
can have data to populate their views.

The window also defines a Qt "signal" which it emits whenever the emulator
comes to a stop (after running free, or after a single step) when the
emulated program counter is different from before. The source window connects
to this signal so that it can jump the source program to a new line at that
time.

'''

class MasterWindow( QWidget ) :
    '''
    Define a Qt signal to emit upon the emulator stopping. Its argument is
    the new PC value.
    '''
    EmulatorStopped = pyqtSignal(int)

    def __init__( self, settings ) :
        global RUN_STOP_BUTTON, STEP_BUTTON, INST_PER_TICK, SETTINGS, STATUS_LINE
        super().__init__( None )
        '''
        Create a vertical box layout and make it this widget's layout.
        '''
        vbox = QVBoxLayout()
        self.setLayout( vbox )
        '''
        Filling the box from the top down, instantiate and add:
        * The Memory display,
        '''
        self.memory_display = MemoryDisplay()
        vbox.addWidget( self.memory_display, 10, Qt.AlignTop | Qt.AlignHCenter )
        '''
        * The register table,
        '''
        self.register_display = RegisterDisplay()
        vbox.addWidget( self.register_display, 5, Qt.AlignHCenter )
        '''
           resize the columns to minimize the tables
        '''
        self.memory_display.resizeColumnsToContents()
        self.register_display.resizeColumnsToContents()
        '''
        * The call stack, in an hbox with a label.
        '''
        self.call_stack_display = CallStackDisplay()
        hbox = QHBoxLayout()
        hbox.addSpacing( 40 )
        hbox.addWidget( QLabel( "Call Stack:" ) )
        hbox.addWidget( self.call_stack_display )
        hbox.addStretch( 5 )
        vbox.addLayout( hbox )
        '''
        * The status line, styled as a "box sunken line-width 1", in an
          hbox with a label.
        '''
        STATUS_LINE = StatusLine()
        hbox = QHBoxLayout()
        hbox.addSpacing( 50 )
        hbox.addWidget( QLabel( 'Status:' ), 1, Qt.AlignLeft )
        hbox.addWidget( STATUS_LINE, 5, Qt.AlignLeft )
        hbox.addStretch( 10 )
        vbox.addLayout( hbox )
        '''
        * A horizontal layout for the buttons, with stretch defined so that
        the buttons sit together to the left with the spinner to the right.
        '''
        hbox = QHBoxLayout()
        hbox.addStretch( 5 )
        vbox.addLayout( hbox )
        '''
        * The run/stop button, set to the un-checked "Run" state,
        '''
        RUN_STOP_BUTTON = RunStop()
        RUN_STOP_BUTTON.setChecked( False )
        hbox.addWidget( RUN_STOP_BUTTON )
        hbox.addStretch( 1 )
        '''
        * The Step button
        '''
        STEP_BUTTON = chip8util.RSSButton()
        STEP_BUTTON.setText( ' STEP  ' )
        hbox.addWidget( STEP_BUTTON )
        hbox.addStretch( 20 )
        '''
        * The instructions/tick spinner, initialized to its saved
          previous value.
        '''
        set_value = int( SETTINGS.value( "memory_page/spinner", 10 ) )
        INST_PER_TICK = InstPerTick( set_value )
        hbox.addWidget( INST_PER_TICK )
        hbox.addStretch( 10 )
        '''
        Connect the clicked signal of the STEP switch to our step_click() method.
        '''
        STEP_BUTTON.clicked.connect( self.step_clicked )
        '''
            Connect the clicked signal of the RUN/STOP switch to run_stop_click().
            '''
        RUN_STOP_BUTTON.clicked.connect( self.run_stop_click )
        '''
        Register callback functions with the emulator so we will be notified
        when the emulator will reset and when it has. Those methods below.
        '''
        chip8.reset_anticipation( self.reset_coming )
        chip8.reset_notify( self.reset_display )
        '''
        Set the window's focus policy to click-to-focus. Don't want tabbing
        between the top level windows.
        '''
        self.setFocusPolicy( Qt.ClickFocus )
        '''
        With all widgets created, resize and position the window
        from the settings.
        '''
        self.resize( settings.value( "memory_page/size", QSize(600,400) ) )
        self.move(   settings.value( "memory_page/position", QPoint(100, 100) ) )
        '''
        Set the window title.
        '''
        self.setWindowTitle( "CHIP-8 Emulator" )
        '''
        If the emulated PC is nonzero, make it visible in the memory display.
        '''
        if chip8.REGS[ chip8.R.P ]:
            self.memory_display.scroll_to_PC( chip8.REGS[ chip8.R.P ] )
        '''
        That's the end of initializing
        '''

    '''
    Define a "slot" to receive the clicked( checked:bool ) signal from the
    STEP button. Just invoke the step() function. The checked value is
    irrelevant since that button is not a toggle.
    '''
    def step_clicked( self, checked:bool ) -> None :
        '''
        Tell the three main displays their models will change.
        '''
        self.begin_resets()
        '''
        Invoke the step function. Since that always executes in
        very little time, we can do it from the signal slot -- unlike
        the run function which has to be a thread.
        '''
        step()
        '''
        Tell the various displays to update their contents.
        '''
        self.end_resets()

    '''
    Define a "slot" to receive the clicked(checked:bool) signal from the
    Run/Stop button. Change the button text to match its current state.

    If the button has toggled to 'active' kick off the run thread. If it has
    toggled to 'inactive' update the status line with the thread's result and
    refresh the display.
    '''
    def run_stop_click( self, checked:bool ) -> None :
        if checked :
            '''
            The button has gone from unchecked to checked.
            * Make it read STOP
            * Disable the various display tables
            * Wake up the run() thread.
            '''
            RUN_STOP_BUTTON.setText( RUN_STOP_BUTTON.on_text )
            self.begin_resets()
            STATUS_LINE.clear()
            OUR_THREAD.wake_up()

        else :
            '''
            The button has gone from checked to unchecked, i.e. STOP clicked.
            The run thread will soon notice the button state and enter its
            wait state, at which time it releases the shared mutex. Wait for
            that to happen.
            '''
            THREAD_MUTEX.lock()
            '''
            With the thread in the stopped state,
            * Make the button read RUN again
            * Put the emulator status in the status line
            * Re-enable and update the various tables.
            * Release the mutex
            '''
            RUN_STOP_BUTTON.setText( RUN_STOP_BUTTON.off_text )
            STATUS_LINE.setText( OUR_THREAD.message_text )
            self.end_resets()
            THREAD_MUTEX.unlock()

    '''
    When the vm is going to reset, #1, STOP THE EMULATOR.
    '''
    def reset_coming( self ) :
        if RUN_STOP_BUTTON.isChecked() :
            '''
            The button is in the checked state, meaning the emulator is
            running. Simulate a user click to force it to unchecked state,
            which will emit the signal that will call run_stop_click() above.
            It in turn will call end_resets() to update displays.
            '''
            RUN_STOP_BUTTON.click()
            '''
            Now kill a little time to make sure that all happens.
            '''
            QTest.qWait(5)

    '''
    The emulated machine gets a full reset when a new program is loaded, as
    well as various times in unit tests. When the VM has completed resetting,
    make all the tables update. Also, clear the status line.
    '''
    def reset_display( self ) :
        global MEMORY_UPDATE_NEEDED
        MEMORY_UPDATE_NEEDED = True # we do want the memory table updated
        self.begin_resets()
        self.end_resets()
        STATUS_LINE.clear()

    '''
    Tell our attached display widgets that their underlying data will
    be changing. There is little time penalty to resetting the call stack and
    register tables, but don't reset the memory table unless we have to.
    '''
    def begin_resets( self ) :
        self.call_stack_display.model().beginResetModel()
        self.register_display.model().beginResetModel()

    '''
    Update all the display widgets to reflect the new(?) machine state.

    Make the memory display show the PC row.
    Make the tables resize columns to contents.
    '''
    def end_resets( self ) :
        global MEMORY_UPDATE_NEEDED
        '''
        The call stack and register displays have already begun-reset,
        so finish them.
        '''
        self.call_stack_display.model().endResetModel()
        self.register_display.model().endResetModel()
        self.register_display.resizeColumnsToContents()
        '''
        We didn't initiate the reset on memory because it is so expensive
        it makes STEP slow to respond. And usually isn't needed. Was it
        needed?
        '''
        if MEMORY_UPDATE_NEEDED :
            self.memory_display.model().beginResetModel()
            self.memory_display.model().endResetModel()
            self.memory_display.resizeColumnsToContents()
            MEMORY_UPDATE_NEEDED = False

        self.memory_display.scroll_to_PC( chip8.REGS[ chip8.R.P ] )
        self.EmulatorStopped.emit( chip8.REGS[ chip8.R.P ] )

    '''
    Override the built-in closeEvent() method to save our geometry and
    the inst/tick spinbox in the settings. Ignore the event unless the
    Quit menu action has been triggered.
    '''
    def closeEvent( self, event ) :
        global SETTINGS, ACTUALLY_QUITTING
        if ACTUALLY_QUITTING :
            '''
            When the window closes, write our geometry and spinbox value
            into the settings.
            '''
            SETTINGS.setValue( "memory_page/size", self.size() )
            SETTINGS.setValue( "memory_page/position", self.pos() )
            SETTINGS.setValue( "memory_page/spinner", INST_PER_TICK.value() )
            super().closeEvent( event ) # pass it along
        else :
            event.ignore()

'''
Receive the signal from the Quit menu action that we are actually
shutting down and note that in a global. The signal is connected
from the Source module.
'''
ACTUALLY_QUITTING = False

def quit_signal_slot( ) -> None :
    global ACTUALLY_QUITTING
    ACTUALLY_QUITTING = True

'''

When the RUN! button is clicked, we want to go into a loop calling the
chip8.step() function as fast as possible. This loop could continue for
an indefinite time, seconds to minutes, even to hours. For this reason the
operation needs to be in a separate thread.

The QThread is passed a mutex that it shares with the MasterWindow. It saves
that. Further initialization has to wait until the thread is started. Then it
initializes a 1/60th second timer and a QWaitCondition.

In operation the thread executes in its run() method, which waits on the
WaitCondition, then runs the emulator until the emulator returns an error or
the Run/Stop switch changes state, whichever comes first.

'''

class RunThread( QThread ) :

    def __init__( self, mutex, parent=None ) :
        '''
        Minimal object initialization, because this __init__() is executed by
        the calling thread, i.e. the main one running MainWindow. The timer
        used in the thread needs to be created in that thread, which means,
        created from within the run() method. Hence the real __init__() is
        post_init() below.
        '''
        super().__init__( parent )
        self.mutex = mutex # mutexes are thread-safe.
        self.message_text = None # type: str

    def post_init( self ) :
        '''
        Create a one-shot timer with an interval of 1/60th second, or just a
        skosh less, which should not be a problem. For one thing, we probably
        blow one millisecond just getting it restarted.

        The timer is (re)started with when the run() method wakes up from a
        wait. As long as the timer isActive() the interval has not expired.
        '''
        self.timer = QTimer()
        self.timer.setInterval( 17 ) # juuuust over 1/60th
        self.timer.setSingleShot( True )
        '''
        Create a QWaitCondition, upon which the run() method can wait
        for a signal. The signal will come when the MasterWindow
        calls our wake_up method, indicating that RUN has been clicked.
        '''
        self.wait_for_click = QWaitCondition()

    def wake_up( self ) :
        '''
        When the MasterWindow is told that the RUN/STOP switch has been
        toggled to the active state, it calls this (hence this method
        actually runs in the master thread). The only reason for this method
        is that I don't want to expose the waitCondition to the MasterWindow
        code.
        '''
        self.wait_for_click.wakeOne()

    def run( self ) :
        '''
        Finish initializing, but from our own thread.
        '''
        self.post_init()
        '''
        Acquire ownership of the mutex.
        '''
        self.mutex.lock()
        '''
        Execute the following endless loop.
        '''
        while True :
            '''
            Wait to be awakened. Part of the wait() is that the mutex lock
            is released. The MasterWindow can acquire the mutex as a way of
            knowing that this thread has entered the wait.
            '''
            self.wait_for_click.wait( self.mutex )
            '''
            Yawn. Stretch. OK, set up to enter the loop.
            Tell the Screen module that a new thread will be calling it.
            If the emulated sound is supposed to be going, restart it.
            Initialize a counter. Start the timer going.
            '''
            display.change_of_thread( True )
            if chip8.REGS[ chip8.R.S ] :
                display.sound( on=True )
            tick_limit = INST_PER_TICK.value()
            inst_count = 0
            burn_count = 0 # DBG
            self.timer.start()
            '''
            Enter a loop that only ends when STOP is clicked or the emulator
            returns some kind of error.
            '''
            while RUN_STOP_BUTTON.isChecked() :
                '''
                If the timer has popped,
                '''
                if not self.timer.isActive() :
                    '''
                    * notify the emulator of one tick passing
                    * clear the inst_count
                    * refresh the tick_limit (so the user can change it while
                      the emulator is running, for experimentation)
                    * start a new timer

                    Also keeps two debugging values that could be logged or displayed:

                    shortfall is the number of instructions requested by the
                    inst-per-tick that are not executed -- when >0, you have
                    asked for more insts than the emulator can do in 17ms.

                    burn_count is the number of idle cycles we took to kill
                    time waiting for the end of 17ms -- when >0, we could
                    have done more emulated instructions than requested.
                    '''
                    chip8.tick()
                    shortfall = inst_count - INST_PER_TICK.value()
                    inst_count = 0
                    tick_limit = INST_PER_TICK.value()
                    burn_count = 0
                    self.timer.start()
                '''
                If we have not reached the inst/tick limit, execute an instruction:
                '''
                if inst_count <= tick_limit :
                    '''
                    * call the emulator, save its result
                    * count the instruction
                    * break the inner loop if any error
                    '''
                    self.message_text = chip8.step()
                    inst_count += 1
                    if self.message_text is not None :
                        break
                else :
                    '''
                    Else we have done as many emulated instructions in this tick
                    as required, so just pass the time in a constructive way.
                    '''
                    QCoreApplication.processEvents( )
                    burn_count += 1 #DBG
            '''
            Either the RUN/STOP switch was clicked, or the emulator returned
            an error. If the emulated tone is sounding, stop it.
            '''
            display.sound( on=False )
            if self.message_text is None :
                '''
                We stopped because the Run/Stop button changed state.
                '''
                self.message_text = 'Stopped'
            else :
                '''
                We stopped because the emulator cannot continue.
                Toggle the Run/Stop switch directly, if it needs it.
                '''
                if RUN_STOP_BUTTON.isChecked():
                    RUN_STOP_BUTTON.click()
            '''
            Tell display that another thread (possibly) will be calling it.
            '''
            display.change_of_thread( False )
            '''
            Start over from the wait.
            '''

'''

The step() function is called when the MasterWindow gets a clicked signal
from the Step pushbutton. Operate the emulator for one instruction.

'''

def step():
    global STATUS_LINE

    STATUS_LINE.clear()
    '''
    If the sound should be on, turn it on.
    '''
    if chip8.REGS[ chip8.R.S ] :
        display.sound( on=True )
        QTest.qWait(5)
    '''
    Execute one instruction
    '''
    result = chip8.step()
    '''
    Turn the sound off in case it was on or was turned on.
    '''
    display.sound( on=False )
    '''
    If chip8 returned some error status, show it.
    '''
    if result is not None :
        STATUS_LINE.setText( result )


'''

Initialize, called from the chip8ide module. Create the window and all widgets
and initialize them from saved settings.

'''

from PyQt5.QtCore import QSettings

SETTINGS = None # type: QSettings

OUR_WINDOW = None # type: MasterWindow

OUR_THREAD = None # type: QThread

THREAD_MUTEX = None # type: QMutex

MEMORY_UPDATE_NEEDED = False

def memory_updated( ) :
    global MEMORY_UPDATE_NEEDED
    MEMORY_UPDATE_NEEDED = True

def initialize( settings: QSettings ) -> None :
    global OUR_WINDOW, SETTINGS, OUR_THREAD, THREAD_MUTEX
    '''
    Save the settings for shutdown time
    '''
    SETTINGS = settings
    '''
    Initialize the font
    '''
    chip8util.initialize_mono_font()
    '''
    Create the window and all widgets in it
    '''
    OUR_WINDOW = MasterWindow( settings )
    '''
    Create the run() thread and start it going.
    '''
    THREAD_MUTEX = QMutex()
    OUR_THREAD = RunThread( THREAD_MUTEX )
    OUR_THREAD.start()

    chip8.memory_notify( memory_updated )

    '''
    Display our window
    '''
    OUR_WINDOW.show()

'''
connect_signal(), a request from some other module (actually, source) to please
connect their callable to our signal EmulatorStopped.

this can only be done after initialize() has run, because the MasterWindow
is created then.
'''
from typing import Callable

def connect_signal( slot: Callable ) :
    OUR_WINDOW.EmulatorStopped.connect( slot )
    # you may kiss the bride...

if __name__ == '__main__' :

    from binasm import binasm

    from PyQt5.QtWidgets import QApplication
    args = [] # type: List[str]
    the_app = QApplication( args )
    chip8.reset_vm( binasm( '6955 6AAA 89A1 89A2 89A3 00FD' ) )
    #chip8.CALL_STACK = [516,532,564]
    initialize(QSettings())
    quit_signal_slot() # otherwise the unit test cannot be ended!
    STATUS_LINE.setText('now in unit test')
    OUR_WINDOW.show()
    the_app.exec_()

