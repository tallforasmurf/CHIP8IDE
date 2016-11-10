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

This module defines the Source window, which is the Qt Main Window and owns
the menus. It displays one main widget, a QTextEdit, a status line, and two
buttons named LOAD and CHECK.

CHIP-8 assembly programs are loaded into the editor, or entered there by the
user. Lexical errors are caught as statements are entered. An invalid statement
is highlighted by a pink background.

Not all errors can be recognized on entry. For example, a statement that
refers to a name that has not yet been defined may be an error, or may become
correct when the name is defined on a later statement, or when the spelling
of the name is edited on this or some other statement.

At any time the CHECK button can be clicked. The existing program source is
assembled and any further error lines are highlighted.

Clicking the LOAD button also causes assembly and if there are no errors, the
assembled binary is loaded into the emulator ready to execute.

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
Import the Statement class.
'''
from statement_class import Statement

'''
Import the statement inspection routine from the assembler1 module and
the assemble() and disassemble methods from their modules.
'''
from assembler1 import phase_one
from assembler2 import assemble
from disassemble import disassemble

'''
Import the reset_vm method of chip8, which is called by the Load button.
'''
from chip8 import reset_vm

'''
Import sys for .platform, and os/os.path for file ops.
'''
import sys
import os
import os.path

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
    QBrush,
    QCloseEvent,
    QColor,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextBlock,
    QTextBlockUserData
    )
from PyQt5.QtWidgets import (
    qApp,
    QAction,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget
    )

'''

Define the QSyntaxHighlighter by way of which we inspect each new
statement after it is edited.

A syntax highlighter is independent of the editor; it is associated with a
QTextDocument. When first connected to the document, the highlighter is
called to inspect every line. Thereafter it is called whenever a line is
edited, even by one keystroke.

The job of this highlighter is to validate the current statement, and to
store the Statement object that results. Validation is done by the
phase_one() function in module assembler1.

When phase_one() returns a Statement with is_valid False, we make the
line turn INVALID_LINE_COLOR.

'''

'''
The QTextBlock's userData member will only accept a QTextBlockUserData
object. So we wrap our Statement object in one of those.
'''
class StatementWrapper ( QTextBlockUserData ) :
    def __init__( self, statement ) :
        super().__init__( )
        self.statement = statement

class Highlighter( QSyntaxHighlighter ) :
    def __init__( self ) :
        '''
        Initialize the parent class with no parent. It will be linked
        to a document later using self.setDocument().
        '''
        super().__init__( None )
        '''
        Make a QTextCharFormat to apply to errors.
        '''
        self.error_format = QTextCharFormat( )
        self.error_format.setBackground( QBrush( QColor( INVALID_LINE_COLOR ) ) )
        self.error_format.setProperty(QTextCharFormat.FullWidthSelection, True)

    '''
    This method is called by the document to inspect a line (actually, a
    QTextBlock, but that means one line in a plain text editor) whenever it
    changes. Really. Every damn character! So be quick!

    The input is the text of the line as a string. However we can also access
    the text block itself via self.currentBlock(). The Statement object
    always returned by phase_one() is set as the text block user data, where
    it provides info to the later assembly passes.
    '''
    def highlightBlock( self, text ) :
        U = self.currentBlockUserData()
        if U is None :
            '''
            No Statement created for this line yet; make one and install it.
            This code assumes that Qt does not *copy* the user data but only
            holds a reference to it, so we can modify it in place.
            '''
            S = Statement()
            U = StatementWrapper( S )
            self.setCurrentBlockUserData( U )
        else :
            '''
            We had previously (like, milliseconds ago) made a Statement object
            for this text block, so just get it out of the wrapper it's in.
            '''
            S = U.statement

        '''
        Perform tokenization and lexical validation of this line.
        '''
        phase_one( text, S )

        if S.text_error or S.expr_error :
            self.setFormat( 0, len(text), self.error_format )

'''
Define some colors, quite arbitrarily.

* Current line: a very light yellow.
* Invalid statement: pale tomato soup
* Breakpoint line: light lilac
'''
CURRENT_LINE_COLOR = "#FAFAE0"
INVALID_LINE_COLOR = "#FF8090"
BREAKPOINT_LINE_COLOR = "thistle"
'''
    Define the Editor

A QPlainTextEdit is a very capable editor on its own, but it needs
a lot of customization to do the things we want it to do.
'''

class SourceEditor( QPlainTextEdit ) :
    def __init__( self, main_window, parent=None ) :
        super().__init__( parent )
        self.main_window = main_window
        '''
        Set the editor options:
           font to our Monofont
           accept the focus by click or by tab
           accept dropped text
           don't wrap lines
           make tab stops half the default
              n.b. tabStopWidth is in pixels, defaults to 80
        '''
        font = QFont( MONOFONT )
        font.setPointSize( 12 )
        self.setFont( font )
        self.setFocusPolicy( Qt.StrongFocus )
        self.setAcceptDrops( True )
        self.setLineWrapMode( QPlainTextEdit.NoWrap )
        self.setTabStopWidth( int( self.tabStopWidth()/2 ) )
        '''
        Set up a list of "extra selections", the mechanism by which we get
        the editor to show different lines in different colors. The list is a
        list of QTextEdit.ExtraSelection objects, see make_extra_selection()
        below. Initially and often the list has only one item, the selection
        for painting the current line a nice pale lemony yellow.
        '''
        self.current_line_selection = self.make_extra_selection( CURRENT_LINE_COLOR )
        self.extra_selection_list = [ self.current_line_selection ]

        '''
        Connect the signal that the cursor moved, to our routine that updates
        the color of the current line. Set up a current text block variable
        so that routine can know when the actual line has changed. Then fake
        the signal to start us off.
        '''
        self.last_text_block = None
        self.cursorPositionChanged.connect( self.cursor_moved )
        self.cursor_moved()

    '''
    Upon any movement of the cursor, even by one character, this slot
    is entered. (So, it behooveth us to be snappy!).

    If we have fields with meta-data about the current line, like the
    current line or column number, this would be the place to update them.
    But we don't, as of now.

    If the cursor is now on a different line number (text block) than before,
    change the cursor in the current-line "extra selection" to the position
    of the current line. Note that the cursor in an extra selection may not
    have a selection. The current cursor might have one, so clear it.

    To make the new selection(s) appear we have to call setExtraSelections.
    The whole list (which might or might not include breakpoints) is set.
    The current line selection last so it will take precedence over breakpoints
    (and, it happily turns out, over red error-highlighting).

    '''

    def cursor_moved( self ) :
        cursor = self.textCursor()
        text_block = cursor.block()
        if text_block == self.last_text_block :
            # same line, nothing to do
            return
        self.last_text_block = text_block
        self.current_line_cursor = QTextCursor( cursor )
        self.current_line_cursor.movePosition( text_block.position(), QTextCursor.MoveAnchor )
        self.current_line_selection.cursor = self.current_line_cursor
        self.setExtraSelections( self.extra_selection_list )
        '''
        Get the Statement out of the current text block and have a look.
        '''
        status_msg = ''
        U = text_block.userData()
        if U : # is not None,
            S = U.statement # unwrap the Statement object
            if S.text_error or S.expr_error :
                '''
                The new current line is an error line, display its error text
                in the status line.
                '''
                status_msg = S.error_msg
                if S.error_pos : # is not zero,
                    status_msg += ' near ' + str( S.error_pos )
            else :
                '''
                The new current line is not an error. If it has been assembled,
                and the document is unchanged, display its text and PC.
                '''
                if S.value and self.main_window.clean_assembly :
                    if S.value_dump == '' :
                        '''
                        The line has been assembled but the display needs to be
                        created for it -- once, so we don't repeat this.
                        '''
                        dump = [ '{:02X}'.format(n) for n in S.value ]
                        S.value_dump = '{:04X} : '.format( S.PC ) + ''.join( dump )
                    status_msg = S.value_dump
        self.main_window.status_line.setText( status_msg )



    '''
    Make a given line number (origin-0) the current line and center
    it in the edit window. This is done by:

    * getting the QTextBlock that corresponds to that line number
    * making a QTextCursor positioned to that line's origin
    * setting that QTextCursor as the edit cursor
    * telling the editor to center the cursor

    Note this removes any existing selection, and also probably triggers
    a cursorMoved signal.
    '''

    def go_to_line( self, line_number ) :
        text_block_for_line = self.document().findBlockByLineNumber( line_number )
        cursor = QTextCursor( self.textCursor() )
        cursor.setPosition( text_block_for_line.position() )
        self.setTextCursor( cursor )
        self.centerCursor( )

    '''
    Create a QTextCharFormat given a color, specified as a string that
    QColor will accept: a standard name or in #RRGGBB form.

    The only formats we use are solid background color formats that extend
    the full width of the line. n.b. that property is essential to successful
    use of extra-selections to highlight lines.
    '''
    def make_format( self, color ) :
        format = QTextCharFormat( )
        format.setBackground( QBrush( QColor( color ) ) )
        format.setProperty(QTextCharFormat.FullWidthSelection, True)
        return format

    '''
    Create a QtextEdit.ExtraSelection given a color. It won't be
    usable until a non-empty QTextCursor replaces this dummy one.
    '''
    def make_extra_selection( self, color ) :
        thingummy = QTextEdit.ExtraSelection()
        thingummy.format = self.make_format( color )
        thingummy.cursor = QTextCursor( )
        return thingummy


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
        Create and save a reference to the status line widget.
        It has to exist now because as soon as we create the editor,
        the cursor_moved function will try to reference it.
        '''
        self.status_line = QLabel()
        self.status_line.setFont( MONOFONT )

        '''
        Create a flag that shows whether the current source has been
        assembled and not yet edited since then. Set in do_assembly()
        and document_changed(), tested in cursor_moved().
        '''
        self.clean_assembly = False

        '''
        Create the text edit widget and put it in the layout. Give it
        a reference to this object so it can access the status_line.
        '''
        self.editor = SourceEditor( self )
        self.editor.setSizePolicy(
            QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            )
        vbox.addWidget( self.editor, 10 )

        '''
        Keep a reference to the text document. We need it often.
        Connect its contentsChanged signal to our contents_changed.
        '''
        self.document = self.editor.document()
        self.document.contentsChanged.connect( self.contents_changed )
        '''
        Create the syntax highlighter and attach it to the document.
        '''
        self.highlighter = Highlighter()
        self.highlighter.setDocument( self.document )

        '''
        Make a little hbox and use it to lay out our buttons
        to the right of a status display.
        '''
        hbox = QHBoxLayout()

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
        Set the window's focus policy to click-to-focus. Don't want tabbing
        between the top level windows.
        '''
        self.setFocusPolicy( Qt.ClickFocus )
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
        Create the menus.
        First create a couple of variables used by file_save and file_open.
        '''
        self.last_dir_path = ''

        menu_bar = self.menuBar()

        '''
        Create the File menu and populate it with the actions New, Open,
        Save, and Save-As (because I'm old-school).
        '''
        self.file_menu = menu_bar.addMenu( '&File' )

        temp_action = self.file_menu.addAction( '&New' )
        temp_action.setShortcut( QKeySequence.New )
        temp_action.setToolTip( 'Create a new, empty assembly program' )
        temp_action.triggered.connect(self.file_new)

        temp_action = self.file_menu.addAction( '&Open' )
        temp_action.setShortcut( QKeySequence.Open )
        temp_action.setToolTip( 'Open an existing assembly program file' )
        temp_action.triggered.connect(self.file_open)

        temp_action = self.file_menu.addAction( '&Save' )
        temp_action.setShortcut( QKeySequence.Save )
        temp_action.setToolTip( 'Save the assembly program in a file' )
        temp_action.triggered.connect(self.file_save)

        temp_action = self.file_menu.addAction( 'Save &As' )
        temp_action.setShortcut( QKeySequence.SaveAs )
        temp_action.setToolTip( 'Save the assembly program in a file by name' )
        temp_action.triggered.connect(self.file_save_as)

        ### DBG TEMP ONLY REMOVE
        temp_action = self.file_menu.addAction( 'Bazongas!' )
        temp_action.triggered.connect( self.bazongas )

        '''
        Create the Quit action, which Qt will put in the appropriate menu
        for the platform: File menu for Windows and Linux, App menu for mac.
        When triggered it calls the QWidget.close() method which in turn will
        issue a QCloseEvent, which we trap later.
        '''
        temp_action = QAction( '&Quit', self )
        temp_action.setMenuRole( QAction.QuitRole )
        temp_action.setShortcut( QKeySequence.Quit )
        temp_action.triggered.connect(self.close)

        self.file_menu.addAction( temp_action )

        '''
        Call File>New to initialize the window title.
        '''
        self.file_new()

    '''
    Upon any change whatever in the document since the last assembly,
    stop displaying assembled values in the status line. It's impossible
    to define a set of changes that would NOT invalidate at least the
    PC values of that and following lines.
    '''
    def contents_changed( self ):
        self.clean_assembly = False

    '''
    Internal method common to both Check and Load buttons:
    Pass the first text block of the document to the assemble() function
    which iterates over the source, updating all the Statement objects, and
    returning a new memory load, or a count of errors found.

    If assemble returns errors, construct and display a warning dialog
    and return None, else return the memory load from assembly.
    '''
    def do_assembly( self ) -> bool :
        first_block = self.document.firstBlock()
        mem_load = assemble( first_block )
        if mem_load[0] < 0 :
            '''
            The assembler found errors. The count of syntax errors (which
            the user ought to have corrected before clicking CHECK!) is in
            mem_load[1], and the count of errors found while evaluating
            expressions is in mem_load[2].

            Build a warning dialog and tell the user. Also call the syntax
            highlighter to re-inspect the whole document to make sure all
            the errors are marked.

            The title= argument to QMessageBox.warning is invisible on OSX.
            So we do some formatting in the text string.
            '''
            title = 'Assembly Errors Found'
            s_errors = ''
            x_errors = ''
            if mem_load[1] :
                s_errors = 'one format error' if mem_load[1]==1 \
                    else '{} syntax errors'.format(mem_load[1])
                if mem_load[2] :
                    s_errors += ' and '
            if mem_load[2] :
                x_errors = 'one expression error' if mem_load[2]==1 \
                    else '{} expression errors'.format(mem_load[2])
            msg = 'Assembly finds ' + s_errors + x_errors + '.\nCorrect and try again'
            QMessageBox.warning( self, title, msg )
            self.highlighter.rehighlight()
            return None
        self.clean_assembly = True
        return mem_load

    '''
    This method is called when the CHECK button is clicked. It performs
    the assembly and that is all.
    '''
    def check_clicked( self ) :
        mem_load = self.do_assembly()
        return

    '''
    This method is called when the LOAD button is clicked.
    It performs the assembly and if all is good,
    it resets the chip8 memory with a new memory load.
    '''
    def load_clicked( self ) :
        mem_load = self.do_assembly()
        if mem_load : # is not None,
            reset_vm( mem_load )

    '''
    Copied from the Qt Application Example, maybe_save() is called
    whenever there is a chance of losing the user's work, to give
    the user an option of saving or cancelling the operation.
    '''
    def maybe_save( self, why:str ) :
        if self.document.isModified() :
            choice = QMessageBox.warning(
                self, '',
                '''The source file has been modified:
                Save the file, Discard it, or Cancel ''' + why,
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
            if choice == QMessageBox.Cancel :
                return False
            if choice == QMessageBox.Save :
                return self.file_save()
        return True

    '''
    Set the current file name as the window title, save the file path (if
    given) as the window file path, and clear the modified flag if it is set.
    '''
    def set_file_name( self, name: str, path: str = None ) :
        self.document.setModified( False )
        self.setWindowModified( False )
        self.setWindowFilePath( path )
        self.setWindowTitle( name )

    '''
    This method is called when File>New is selected. Empty our document of
    all content. Set the document name to Untitled and mark it unmodified. Do
    not clear the window file path, leave it at what some previous open or
    save might have set, to act as a starting directory for a subsequent
    save-as.
    '''
    def file_new( self ) :
        if self.maybe_save( "File>New" ) :
            self.document.clear()
            self.set_file_name( "Untitled" )

    '''
    This method is called when File>Open is selected. Show the user
    a file-selection dialog and attempt to read the file.

    Open the path selected by the user and read it as a byte stream.
    Then try to decode the bytes as Latin-1. If this succeeds assume
    it represents an assembler source.

    If decoding fails, assume we have a CHIP-8 binary file. Pass it
    to the disassembler which returns a string.

    Load the string into the editor.

    '''
    def file_open( self ) :
        if self.maybe_save( "File>Open" ) :
            '''
            The arguments to QFileDialog.getOpenFile() are:
            * parent, i.e. this window, over which the dialog centers,
            * caption, which on some platforms will be a dialog title,
            * the starting directory, which comes from the last successful
            file-open or file-save operation,
            * a filter string that would limit the available file suffixes
            but since there are no established CHIP-8 suffixes, don't do it.
            The return is a tuple, (file-path, chosen-filter), and we ignore
            the latter. If the user hits Cancel, the file-path is null.
            '''
            (chosen_path, _) = QFileDialog.getOpenFileName(
                self, 'Open a CHIP-8 Assembly or binary file',
                self.last_dir_path,
                ''
                )
            if len(chosen_path) == 0 :
                return False

        '''
        We have a file path to (try to) open. We will use Python facilities
        for this (as opposed to using QFile and QTextStream).

        Open the file as bytes and read all its contents as a single
        bytestream. If that fails for some reason, tell the user and give up.
        '''
        chosen_path = os.path.abspath( chosen_path )
        try :
            file = open( chosen_path, 'rb' )
            byte_string = file.read( -1 )
        except Exception as E :
            QMessageBox.warning( self, 'Error opening file:\n', str(E) )
            return False

        '''
        The file might be an assembly source. If so, it will be possible to
        decode it as ASCII. Note that even decode('ASCII',errors='strict') is
        not really strict; it will pass any byte less than 0x80. A CHIP-8
        binary is almost guaranteed to contain a byte over 0x80.

        This disallows Latin-1 in assembler source files, or at least disallows
        the use of any character over 0x7f, symbols and accented characters.

        If it can't be decoded, assume it is a CHIP-8 binary file. Pass it to
        the disassembler which always returns a string. In either case, we
        end up with a string.
        '''
        source_string = ''
        try:
            source_string = byte_string.decode( 'ASCII', errors='strict' )

        except Exception as E:
            source_string = disassemble( byte_string )

        '''
        Install the source string as the contents of our document.
        This applies the syntax highlighter to every line, btw.
        '''
        self.document.setPlainText( source_string )
        self.document.setModified( False )

        '''
        Set the filename as our window title, and the file path as
        our file path.
        '''
        (prefix, filename) = os.path.split( chosen_path )
        self.set_file_name( filename, path=prefix )
        return True

    '''
    This method is called when File>Save is selected. If the document
    name is Untitled, call file_save_as() which will call back here.
    Save the file in the pathname set by file_open or file_save_as.

    Note that when opening, the default newline=None means that the single
    newlines returned by toPlainText() will be converted to the system
    default line-ending characters.
    '''
    def file_save( self ) :
        if self.windowTitle().startswith( 'Untitled' ) :
            return self.file_save_as( )

        full_path = os.path.join( self.windowFilePath(), self.windowTitle() )
        try :
            f = open( full_path, 'w', encoding='Latin-1' )
        except Exception as E :
            QMessageBox.warning( self, 'Error opening file:', str(E) )
            return False
        try :
            f.write( self.document.toPlainText() )
        except Exception as E :
            QMessageBox.warning( self, 'Error saving file:', str(E) )
            return False
        self.document.setModified( False )
        return True

    '''
    This method is called when File>Save As is selected. Show the user
    a file-selection dialog, save the resulting pathname as the file
    pathname, and call file_save() above.

    The arguments to QFileDialog.getSaveFile() are:
    * parent, i.e. this window, over which the dialog centers,
    * caption, which on some platforms will be a dialog title,
    * the starting directory, which comes from the last successful
      file-open or file-save operation,
    * a filter string that would limit the available file suffixes
      but since there are no established CHIP-8 suffixes, we don't do it.
    The return is a tuple, (file-path, chosen-filter), and we ignore
    the latter. If the user hits Cancel, the file-path is null.
    '''
    def file_save_as( self ) :
        (chosen_path, _) = QFileDialog.getSaveFileName( self,
                                     'Name the file to save',
                                     self.windowFilePath(),
                                     '' )
        if 0 == len( chosen_path ) :
            return False
        (prefix, filename) = os.path.split( chosen_path )
        self.set_file_name( filename, path=prefix )
        return self.file_save()

    ### DBG REMOVE
    def bazongas( self ) :
        (chosen_path, _) = QFileDialog.getSaveFileName( self,
                                     'Name BINARY to save',
                                     self.windowFilePath(),
                                     '' )
        if 0 == len( chosen_path ) : return False
        try :
            bf = open( chosen_path, 'wb' )
        except Exception as E :
            QMessageBox.warning( self, 'Error opening file:', str(E) )
            return False
        from chip8 import MEMORY
        for j in range( len(MEMORY)-1, -1, -1 ) :
            if MEMORY[j] : break
        try:
            bf.write( bytes( MEMORY[ 0x200 : j+1 ] ) )
        except Exception as E :
            QMessageBox.warning( self, 'Error writing file:', str(E) )
            return False
        finally:
            bf.close()



    '''
    Override the built-in closeEvent() method. Check to see if the
    current document is modified, and if so, ask the user if she wants
    to save it. If the user cancels, or a file_save fails, return False,
    thus cancelling the shutdown. Otherwise, save our geometry and
    invoke the parent's closeEvent.
    '''
    def closeEvent( self, event:QCloseEvent ) :
        if self.maybe_save( "Quit" ) :
            '''
            When the window closes, write our geometry and spinbox value
            into the settings.
            '''
            SETTINGS.setValue( "source_page/size", self.size() )
            SETTINGS.setValue( "source_page/position", self.pos() )
            event.accept()
            qApp.closeAllWindows()
        else :
            event.ignore()




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

