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

    CHIP-8 IDE Source Window

This module defines the Source window, which is the Qt Main Window, and owns
the menus. It displays one main widget, a QTextEdit, and two buttons named
LOAD and CHECK.

CHIP-8 assembly programs are loaded into the editor, or entered there by the
user. Some errors are caught as statements are entered. An invalid statement
is highlighted by a pink background.

Not all errors can be recognized on entry. For example, a statement that
refers to a name that has not yet been defined may be an error, or may become
correct when the name is defined on a later statement or some other
statement is edited.

At any time the CHECK button can be clicked. The existing program source is
assembled and any error lines are highlighted. Clicking the LOAD button also
causes assembly (if necessary) and if there are no errors, the assembled
binary is loaded into the emulator ready to execute.

Information about the line on which the edit cursor rests is shown in a
field below the editor. This can include an error message, or after an
assembly pass, the actual bytes assembled for that statement.

The assembler syntax supported is essentially the same as that of CHIPPER-8
(see README/Sources) and by Jeffrey Bian's MOCHI-I. Those assemblers also
support the directives for conditional assembly (DEFINE, UNDEF, IFDEF, etc.).
This assembler does NOT support those directives. (To be revisited if it
turns out desirable game programs use them.)

The File>Load and File>Save commands are implemented in this module.

   DESCRIPTION TODO

'''

'''
Define exported names. TODO
'''
__all__ = [ 'initialize' ]

'''
Import the monofont prepared by the memory module, and its
definition of a button class.
'''
from memory import MONOFONT, MONOFONT_METRICS, RSSButton


'''
Import needed PyQt modules
'''

from PyQt5.QtCore import (
    QPoint,
    QSettings,
    QSize,
    Qt
    )

from PyQt5.QtGui import (
    QFont,
    QBrush
    )
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,QSizePolicy,
    QVBoxLayout,
    QWidget
    )

'''
    Define the Editor

A QPlainTextEdit is a very capable editor on its own, but it needs
a lot of customization to do the things we want it to do.
'''

class SourceEditor( QPlainTextEdit ) :
    def __init__( self, parent=None ) :
        super().__init__( parent )
        font = QFont( MONOFONT )
        font.setPointSize( 12 )
        self.setFont( font )



'''
    Define the window

Our window is based on QMainWindow, which simplifies creating and managing
the menu bar and File menu. QMainWindow widget comes with a predefined layout
that incorporates a toolbar and a docking area, neither of which we want, so
we just ignore them.

The contents of the window are, from top to bottom,

   * A QPlainTextEdit
   * A status line that gets updated with info about the cursor line
   * Two buttons, CHECK and LOAD


        if C.PLATFORM_IS_MAC :
            _MENU_BAR = QMenuBar() # parentless menu bar for Mac OS
        else :
            _MENU_BAR = self.menuBar() # refer to the default one

'''

class SourceWindow( QMainWindow ) :
    def __init__( self, settings, parent = None ) :
        super().__init__( parent )
        '''
        QMainWindow requires a CentralWidget. Make a widget in which
        we lay out a QPlainTextEdit above a label flanked by buttons.
        '''
        widg = QWidget()
        vbox = QVBoxLayout()

        '''
        Create the text edit widget and put it in the layout.
        '''
        self.editor = SourceEditor()
        self.editor.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            )
        vbox.addWidget( self.editor, 10 )

        '''
        Keep a reference to the text document. We need it often.
        '''
        self.document = self.editor.document()

        '''
        Make a little hbox and use it to lay out our buttons
        to the right of a status display.
        '''
        hbox = QHBoxLayout()

        self.status_line = QLabel()
        self.status_line.setFont( MONOFONT )
        # DBG
        self.status_line.setText( 'Status line' )

        hbox.addWidget( self.status_line, 10, Qt.AlignLeft )

        self.check_button = RSSButton()
        self.check_button.setText( 'CHECK' )
        self.load_button = RSSButton()
        self.load_button.setText( 'LOAD' )

        hbox.addWidget( self.check_button, 1 )
        hbox.addWidget( self.load_button, 1 )

        vbox.addLayout( hbox, 1 )

        '''
        Put the widget with those items as our central widget
        '''
        widg.setLayout( vbox )
        self.setCentralWidget( widg )

        '''
        With all widgets created and layed-out, recover
        the previous geometry from the settings.
        '''
        self.resize( settings.value( "source_page/size", QSize(400,600) ) )
        self.move(   settings.value( "source_page/position", QPoint(100, 100) ) )
        '''
        Connect the signals from the two buttons to methods to
        implement those actions.
        '''
        self.check_button.clicked.connect( self.check_clicked )
        self.load_button.clicked.connect( self.load_clicked )

    '''
    This method is called when the CHECK button is clicked.
    It calls the pass 2 and 3 assembly functions in assembler2.
    '''
    def check_clicked( self ) :
        pass

    '''
    This method is called when the LOAD button is clicked.
    It calls the pass 2 and 3 assembly functions and if all is good,
    it resets the chip8 memory with a new memory load.
    '''
    def load_clicked( self ) :
        pass

    '''
    This method is called when File>Load is selected. Show the user
    a file-selection dialog and attempt to read the file.
    '''
    def file_load( self ) :
        pass

    '''
    This method is called when File>Save is selected. Show the user
    a file-selection dialog and attempt to save the file.
    '''
    def file_save( self ) :
        pass


    '''
    Override the built-in closeEvent() method to save our geometry and
    the inst/tick spinbox in the settings.
    '''
    def closeEvent( self, event ) :
        '''
        When the window closes, write our geometry and spinbox value
        into the settings.
        '''
        SETTINGS.setValue( "source_page/size", self.size() )
        SETTINGS.setValue( "source_page/position", self.pos() )
        super().closeEvent( event ) # pass it along





SETTINGS = None # type: QSettings

OUR_WINDOW = None # type: QMainWindow

def initialize( settings ) :
    global SETTINGS, OUR_WINDOW

    SETTINGS = settings

    OUR_WINDOW = SourceWindow( settings )

    OUR_WINDOW.show()



if __name__ == '__main__' :

    '''
    Aaaaand we hack up some tests. Lasciate ogne speranza...
    '''
    #from binasm import binasm

    from PyQt5.QtWidgets import QApplication
    args = []
    the_app = QApplication( args )

