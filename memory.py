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

The window is an independent (that is parent-less) window with the title
"CHIP-8 Emulator". It can be positioned, minimized or maximized independent
of the rest of the app. During initialization it sets its geometry from the
saved settings.

Within the window are the following widgets:

The Memory display is a table showing the 4096 bytes of emulated memory in
128 rows of 32 bytes. When the emulator has been running and stops, the
Memory display scrolls so that the line containing the current PC address is
visible. When the emulator is not running, the user can edit individual bytes
by double-clicking a byte and entering a new value.

Below the memory is a display of the call stack of subroutine return addresses.

The Register display shows the 20 CHIP-8 registers (v0-vF, PC, I, ST, DT).
When the emulator is not running, the user can edit the contents of these,
and thus affect the execution of the program when it resumes. (One use for
this ability: because the DT and ST are not decremented during single-step
operation, the user could set them to simulate a change.)

The RUN/STOP switch is a QPushbutton in one of two states. When the Emulator
is not running, the button reads RUN. When clicked, the button toggles to
read STOP and the emulator begins execution of the current program.

The STEP button is a QPushbutton that is enabled when the emulator is not
running. Clicking it causes the emulator to execute a single instruction.

"Inst/tick" is a QSpinBox (numerical entry widget) that allows the user to
set the maximum number of emulated instructions that can be executed per
1/60th-second "tick" of the delay timer. The actual COSMAC VIP probably
executed around 100 instructions per tick (about 2500/sec). On modern hardware
the emulator can exceed that by orders of magnitude, and this gives the user
control over how fast an emulated program runs.

The status line shows the reason the emulator stopped executing.

Because this is a module (rather than a singleton class definition) it is
necessary to code Pascal-style, defining all names before they are used.

'''

'''
Define this module's API:
   initialize()
   MONOFONT and MONOFONT_METRICS
   the RSSButton class
Really, that's it. It opens the window and away we go.
'''
__all__ = [ 'initialize', 'MONOFONT', 'MONOFONT_METRICS', 'RSSButton' ]


'''
Import the memory, registers and call stack from the display module.
'''

import chip8

from chip8 import R, reset_vm, MEMORY_CHANGED

'''
Import needed Qt names.
'''

from PyQt5.QtCore import (
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
    QFont,
    QFontInfo,
    QFontDatabase,
    QFontMetrics,
    QIcon,
)

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget
)


'''
Use Qt facilities to get a monospaced font to use in all widgets.
Store it in MONOFONT for use from various other modules.
'''

MONOFONT = None # type QFont
MONOFONT_METRICS = None # type QFontMetrics

def initialize_mono_font( ) :
    global MONOFONT, MONOFONT_METRICS
    '''
    Ask the QFontDatabase for the family of the recommended fixed-pitch font.
    It returns a QFont with a default point size, which we store in the global.
    '''
    MONOFONT = QFontDatabase.systemFont( QFontDatabase.FixedFont )
    MONOFONT_METRICS = QFontMetrics( MONOFONT )

'''
Some widgets require a QBrush with black color for background and a
white QBrush for foreground.
'''
BLACK_BRUSH = QBrush( QColor( "Black" ) )
WHITE_BRUSH = QBrush( QColor( "White" ) )

'''
Define the "look" of the Run/Stop and Step buttons. They both use a
scaled-up version of MONOFONT and have a minimum size based on the
font metrics of that font.
'''
class RSSButton( QPushButton ) :

    def __init__( self, parent=None ) :
        super().__init__( parent )
        font = QFont( MONOFONT )
        font.setPointSize( 12 )
        font.setBold( True )
        self.setFont( font )

        metrics = QFontMetrics( self.font() )
        self.setMinimumSize(
            QSize(
                8 + metrics.width( 'MMMMMMMM' ),
                8 + metrics.lineSpacing()
                )
            )

'''
Define the RUN/STOP button as a QPushButton. It has:
 * the checkable property, making it a toggle
 * initial text of "RUN!" -- it is set to "STOP" by the code
   that handles the "toggled" signal.
'''
class RunStop( RSSButton ) :
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
RUN_STOP_BUTTON = None # type RunStop
STEP_BUTTON = None # type RSSButton

'''
Define the Instructions/tick widget as a QSpinbox (numeric entry widget)
with a minimum of 10, max of 1000 and steps of 10. One of these
will be instantiated when we initialize().

A reference to it is stored in INST_PER_TICK for easy access.

The start value is taken from saved settings.

'''

class InstPerTick( QSpinBox ) :
    def __init__( self, start_value:int ) :
        super().__init__( None )
        self.setMinimum( 10 )
        self.setMaximum( 1000 )
        self.setValue( start_value )
        self.setSingleStep( 10 )

INST_PER_TICK = None # type InstPerTick

'''

Define an item delegate to perform editing when a byte of memory is
double-clicked. In the world of Qt MVC, a styled item delegate manages the
editing of a table item. It has to implement three methods:

* createEditor() creates a widget to do the editing, in this case,
  a QLineEdit with a validator.

* setEditorData() loads the editor widget with initial data

* setModelData() takes the edited data and stores it in the model.

With this mechanism in place it is quite easy to edit the memory view.
Double-click one byte -- type 2 hex digits -- hit TAB and the data is stored
and the following byte is opened for editing. Hit return or escape to stop
editing.

'''
class MemoryEdit( QStyledItemDelegate ) :
    def createEditor( self, parent, style, index ):
        '''
        Create a QLineEdit which will permit the input of exactly two
        hexadecimal characters which are automatically uppercased.
        '''
        line_edit = QLineEdit( parent )
        line_edit.setInputMask( '>HH' )
        line_edit.setFont( MONOFONT )
        return line_edit

    def setEditorData( self, line_edit, index ):
        '''
        Load the newly-created line edit with the byte value from the
        selected memory cell. NB: the table index object has a convenient
        data method that calls on the data() method of the table model, which
        given Qt.DisplayRole conveniently returns two uppercase hex digits --
        see MemoryModel.data() below.
        '''
        line_edit.setText( index.data( Qt.DisplayRole ) )

    def setModelData( self, line_edit, model, index):
        model.setData( index, line_edit.text(), Qt.DisplayRole )


    '''
Define the Memory display as a QTableView based on a QAbstractTableModel
that delivers the contents of the emulated memory.

The table dimensions are MEM_TABLE_COLS x MEM_TABLE_ROWS so it can be
tinkered with. But it is likely either 16 x 256 or 32 x 128.

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
            i.e. no drag, shift-click etc. multiple selections
        '''
        self.setCornerButtonEnabled(False)
        self.setShowGrid(False)
        self.setSortingEnabled(False)
        self.setWordWrap(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)

        self.setItemDelegate( MemoryEdit() )
        '''
        Try to get Qt to give the table appropriate space, using
        manual tweaks of various properties - yechhh.
        '''
        self.setMinimumSize(
            QSize(
                MONOFONT_METRICS.width( '00FF' * ( MEM_TABLE_COLS-1 ) ),
                MONOFONT_METRICS.lineSpacing() * 30
                )
            )
        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
            )
        '''
        Instantiate the model and connect it to this view.
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
            PC / MEM_TABLE_COLS,
            PC % MEM_TABLE_COLS )
        end_index = self.model().createIndex(
            (PC+1) / MEM_TABLE_COLS,
            (PC+1) % MEM_TABLE_COLS )
        dbg = [start_index.row(),start_index.column()]
        dbg2 = [end_index.row(), end_index.column() ]
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



class MemoryModel( QAbstractTableModel ) :

    def __init__( self, parent=None ) :
        super().__init__( parent )

    '''
    The flags method tells Qt what the user can do with the table. We allow
    editing (of one byte at a time, see setSelectionMode) but only if the
    emulator is stopped. The MasterWindow uses the beginResetModel() call to
    ensure that nothing will be done with this table while the emulator is
    running.
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
    The data method returns data under various roles.
        display: return 2 hex characters of this byte
        tooltip: return the address of the byte under
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
            return MONOFONT
        elif role == Qt.ForegroundRole :
            return WHITE_BRUSH
        elif role == Qt.BackgroundRole :
            return BLACK_BRUSH
        return None

    '''
    The headerData method returns data for the horizontal and
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
            return MONOFONT
        elif role == Qt.ForegroundRole :
            return BLACK_BRUSH
        elif role == Qt.BackgroundRole :
            return WHITE_BRUSH

    '''
    The setData method stores a byte obtained by the MemoryEdit delegate.
    It probably is not necessary, but check the value for type and length.
    If this function returns False, no change is made. When the update is
    successful it returns True and the table display updates.
    '''
    def setData( self, index, value, role ) :
        hex = '0123456789ABCDEF'
        # ensure a string ... of bloody course it's a string.
        if not isinstance( value, str ) :
            return False
        # ensure uppercase and remove spaces and extraneous chars
        value = [ c for c in value.upper() if c in hex ]
        if 2 != len( value ) :
            return False
        # convert to integer
        number = ( hex.find( value[0] ) * 16 ) + hex.find( value[1] )
        # store in memory
        row = index.row()
        col = index.column()
        chip8.MEMORY[ ( row * MEM_TABLE_COLS) + col ] = number
        return True

'''
Define the register display as a QTableView having only a header row and one
data row. The Table view is based on a QAbstractTableModel that serves up the
register contents.
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
        manual tweaks of various properties - yechhh.
        '''
        self.setMinimumWidth(MONOFONT_METRICS.width( '00FF' * 22 ) )
        self.setMaximumHeight( MONOFONT_METRICS.lineSpacing() * 3.5 )
        self.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
            )
        '''
        Instantiate the model and connect it to this view.
        '''
        self.setModel( RegisterModel( self ) )

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
            16: ' I', 17: ' T', 18: ' S', 19: ' P'
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
        tooltip: return the name of the register under
        font: MONOFONT
        do not return anything for background/foreground, let it default.
    '''
    def data( self, index, role ) :
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole :
            pattern = '{0:02X}' if col < R.P else '{0:04X}'
            return pattern.format( chip8.REGS [ col ] )
        elif role == Qt.ToolTipRole :
            return 'register {}'.format( self.headers[ col ] )
        elif role == Qt.FontRole :
            return MONOFONT
        return None
    '''
    Headerdata returns the names of the registers for horizontal.
    For vertical, the one row header, return "Reg:" Let fonts and colors default.
    '''
    def headerData( self, section, orientation, role ) :
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return self.headers[ section ]
            else :
                return 'Regs'
        elif role == Qt.FontRole :
            return MONOFONT
        return None

'''
Define the Call Stack widget as a QListView based on a QAbstractListModel
which represents the CALL_STACK.
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
        self.setMinimumWidth(MONOFONT_METRICS.width( '00FF' * 20 ) )
        self.setMaximumHeight( MONOFONT_METRICS.lineSpacing() * 2 )
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
        Collect the column number for use later.
        Note whether this column has a stack entry or not.
        '''
        item_number = index.row()
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
            return MONOFONT
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
although all the messages that are displayed are plain ASCII, we make them bold.
'''

class StatusLine( QLabel ):
    def __init__( self, parent=None ) :
        super().__init__( parent )
        self.setLineWidth( 2 )
        self.setMidLineWidth( 1 )
        self.setFrameStyle( QFrame.Box | QFrame.Sunken )
        #self.setFont( MONOFONT ) on mac, system mono font does not have a bold
        self.setMinimumWidth(MONOFONT_METRICS.width( 'F') * 80 )
        self.setMaximumHeight( MONOFONT_METRICS.lineSpacing() * 2 )
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
Define the window. The various widgets are all instantiated during the
initialization code of this object. Note that the chip8 module should have
been initialized before this module.
'''

class MasterWindow( QWidget ) :

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
        * A horizontal layout containing,
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
        STEP_BUTTON = RSSButton()
        STEP_BUTTON.setText( ' STEP  ' )
        hbox.addWidget( STEP_BUTTON )
        hbox.addStretch( 20 )
        '''
        * The instructions/tick spinner, initialized to its saved
          previous value.
        '''
        INST_PER_TICK = InstPerTick( SETTINGS.value( "memory_page/spinner", 10 ) )
        hbox.addWidget( INST_PER_TICK )
        hbox.addStretch( 10 )
        '''
        Set the window's focus policy to click-to-focus. Don't want tabbing
        between the top level windows.
        '''
        self.setFocusPolicy( Qt.ClickFocus )
        '''
        Register a callback with the emulator to be notified when
        the vm is reset.
        '''
        chip8.reset_notify( self.reset_display )
        '''
        With all widgets created, resize and position the window
        from the settings.
        '''
        self.resize( settings.value( "memory_page/size", QSize(600,400) ) )
        self.move(   settings.value( "memory_page/position", QPoint(100, 100) ) )
        '''
        Connect the clicked signal of the STEP switch to our step_click() method.
        '''
        STEP_BUTTON.clicked.connect( self.step_clicked )
        '''
        Connect the clicked signal of the RUN/STOP switch to run_stop_click().
        '''
        RUN_STOP_BUTTON.clicked.connect( self.run_stop_click )
        '''
        Set the window title.
        '''
        self.setWindowTitle( "CHIP-8 Emulator" )
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
            OUR_THREAD.wake_up()

        else :
            '''
            The button has gone from checked to unchecked, i.e. STOP clicked.
            The run thread will notice the button state and enter its wait
            state, at which time it releases the shared mutex. Wait for that.
            '''
            THREAD_MUTEX.lock()
            '''
            * Make the button read RUN again
            * Put the emulator status in the status lin
            * Re-enable and update the various tables.
            * Release the mutex
            '''
            RUN_STOP_BUTTON.setText( RUN_STOP_BUTTON.off_text )
            STATUS_LINE.setText( OUR_THREAD.message_text )
            self.end_resets()
            THREAD_MUTEX.unlock()

    '''
    When the vm is reset, make all the tables update.
    '''
    def reset_display( self ) :
        self.begin_resets()
        self.end_resets()

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
        global MEMORY_CHANGED
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
        if MEMORY_CHANGED :
            self.memory_display.model().beginResetModel()
            self.memory_display.model().endResetModel()
            self.memory_display.resizeColumnsToContents()
            MEMORY_CHANGED = False

        self.memory_display.scroll_to_PC( chip8.REGS[ R.P ] )

    '''
    Override the built-in closeEvent() method to save our geometry and
    the inst/tick spinbox in the settings.
    '''
    def closeEvent( self, event ) :
        '''
        When the window closes, write our geometry and spinbox value
        into the settings.
        '''
        SETTINGS.setValue( "memory_page/size", self.size() )
        SETTINGS.setValue( "memory_page/position", self.pos() )
        SETTINGS.setValue( "memory_page/spinner", INST_PER_TICK.value() )
        super().closeEvent( event ) # pass it along

'''

When the RUN! button is clicked, we want to go into a loop calling the
chip8.step() function as fast as possible. This loop could continue for
an indefinite time, seconds to minutes, even to hours. For this reason the
operation needs to be in a separate thread.

The QThread is passed a mutex that it shares with the MasterWindow. It saves
that. Further initialization has to wait until the thread is started. Then it
initializes a 1/60th second timer and a QWaitCondition.

In operation the thread executes in its run() method, which waits on the
WaitCondition, then runs the emulator until it returns an error or the
Run/Stop switch changes state, whichever comes first.

'''

class RunThread( QThread ) :

    def __init__( self, mutex, parent=None ) :
        '''
        Minimal object initialization, because the timer needs to be
        created in this thread, which means created from the run() method.
        Hence the real __init__ is post_init.
        '''
        super().__init__( parent )
        self.mutex = mutex
        self.message_text = None # type: str

    def post_init( self ) :
        '''
        Create a one-shot timer with an interval of 1/60th second, or just a
        skosh less, which should not be a problem. For one thing, we probably
        blow one millisecond just getting it restarted.

        The timer is (re)started with start(). As long as it isActive() the
        interval has not expired.
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
            Initialize a counter. Start the timer going.
            '''
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
                    '''
                    chip8.tick()
                    shortfall = inst_count - INST_PER_TICK.value()
                    inst_count = 0
                    tick_limit = INST_PER_TICK.value()
                    burn_count = 0 # DBG
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
            an error.
            '''
            if self.message_text is None :
                '''
                We stopped because the Run/Stop button changed state.
                '''
                self.message_text = 'Stopped'
            else :
                '''
                We stopped because the emulator cannot continue.
                Toggle the Run/Stop switch directly.
                '''
                RUN_STOP_BUTTON.click()
            self.message_text += ' ('+str(burn_count)+','+str(shortfall)+')'  # DBG
            '''
            Rinse and repeat.
            '''

'''

The step() function is called when the MasterWindow gets a clicked signal
from the Step pushbutton. Operate the emulator for one instruction.

'''

def step():
    global STATUS_LINE

    STATUS_LINE.clear()

    result = chip8.step()

    if result is not None :
        '''
        chip8 returned some error status, show it.
        '''
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

def initialize( settings: QSettings ) -> None :
    global OUR_WINDOW, SETTINGS, OUR_THREAD, THREAD_MUTEX
    '''
    Save the settings for shutdown time
    '''
    SETTINGS = settings
    '''
    Initialize the font
    '''
    initialize_mono_font()
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
    '''
    Display our window
    '''
    OUR_WINDOW.show()



if __name__ == '__main__' :

    from binasm import binasm

    from PyQt5.QtWidgets import QApplication
    args = []
    the_app = QApplication( args )
    reset_vm( binasm( '6955 6AAA 89A1 89A2 89A3 00FD' ) )
    #chip8.CALL_STACK = [516,532,564]
    initialize(QSettings())
    #STATUS_LINE.setText('helooooo')
    OUR_WINDOW.show()
    the_app.exec_()

