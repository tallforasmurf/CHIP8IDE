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
See below for commentary.

'''
from typing import List
import logging

'''
Define exported names. TODO
'''
__all__ = [ 'initialize' ]

'''
Import the chip8util module for access to the chip8util.MONOFONT definition and the
RSSButton class.
'''
import chip8util

'''
get access to the memory module's new-PC-value signal
'''
from memory import connect_signal

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
Import chip8, the emulator, for reset_vm and breakpoint ops.
'''
import chip8

'''
Import the memory and display windows so we can connect them
to the Quit signal.
'''
import display
import memory

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
    QKeyEvent,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextBlock,
    QTextBlockUserData,
    QTextDocument
    )
from PyQt5.QtWidgets import (
    qApp,
    QAction,
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
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
    Define the Find/Replace dialog.

It's a basic QDialog with two text fields and four pushbuttons.

The SourceEditor instantiates one copy and keeps it around. It is shown when
the user keys ^F. But its find_text and replace_text widgets remain available
after it has closed again, and can be used from e.g. the ^G key event.

'''
class FindDialog( QDialog ) :
    def __init__( self, parent ) :
        super().__init__( parent )

        '''
        Instantiate the widgets and lay them out. First the lineedits.
        '''
        vbox = QVBoxLayout()
        self.find_text = QLineEdit( self )
        vbox.addWidget( self.find_text )
        self.replace_text = QLineEdit( self )
        vbox.addWidget( self.replace_text )
        '''
        Four buttons: Find, Close, Replace, All!, in a row.
        '''
        self.find_button = QPushButton( '&Find' )
        self.find_button.setDefault(True)
        self.close_button = QPushButton( 'Close' )
        self.repl_button = QPushButton( '&Replace' )
        self.all_button = QPushButton( 'All!' )
        hbox = QHBoxLayout()
        hbox.addWidget( self.find_button )
        hbox.addStretch(1)
        hbox.addWidget( self.close_button )
        hbox.addStretch(2)
        hbox.addWidget( self.repl_button )
        hbox.addStretch(1)
        hbox.addWidget( self.all_button )
        vbox.addLayout( hbox )
        self.setLayout( vbox )

        '''
        Connect the buttons to some methods. In fact, the important methods
        are in the parent editor, so they can be used directly from keystrokes.

        The close button just calls accept, which closes the dialog (but does
        not destroy it).
        '''
        self.close_button.clicked.connect( self.accept )
        '''
        The action buttons call into the parent. The code in those methods
        refers via a parent member, to the find_text and replace_text fields here.
        '''
        self.find_button.clicked.connect( parent.find_next )
        self.repl_button.clicked.connect( parent.replace_selection )
        self.all_button.clicked.connect( parent.replace_all )
        '''
        Also connect Find to self.accept, so that hitting return does a Find
        and also closes the dialog. It's just in the way once the find text
        has been entered.
        '''
        self.find_button.clicked.connect( self.accept )
        # that's about it

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
           font to our chip8util.MONOFONT
           accept the focus by click or by tab
           accept dropped text
           don't wrap lines
           make tab stops half the default
              n.b. tabStopWidth is in pixels, defaults to 80
        '''
        font = QFont( chip8util.MONOFONT )
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
        Connect the memory module's EmulatorStopped signal to our show_pc_line
        slot.
        '''
        connect_signal( self.show_pc_line )
        '''
        Initialize a dispatch table for the key event handler. Cannot do
        static initialization of this as a class variable.
        '''
        self.key_dispatch = {
            int(Qt.Key_B) | int(Qt.ControlModifier) : self.toggle_bp,
            int(Qt.Key_E) | int(Qt.ControlModifier) : self.find_next_error_line,
            int(Qt.Key_F) | int(Qt.ControlModifier) : self.start_find,
            int(Qt.Key_G) | int(Qt.ControlModifier) : self.find_next,
            int(Qt.Key_G) | int(Qt.ControlModifier) | int(Qt.ShiftModifier) : self.find_prior,
            int(Qt.Key_Equal) | int(Qt.ControlModifier) : self.replace_selection,
            int(Qt.Key_T) | int(Qt.ControlModifier) : self.replace_and_find
            }
        '''
        Create one instance of the Find dialog and save it for use later.
        '''
        self.find_dialog = FindDialog(self)

    '''
    For the convenience of the File>New, wipe out any possible extra
    selections for breakpoints. Note this should only be called if it
    is known that there are no textblocks with breakpoint status (i.e.
    following a document.clear().
    '''
    def clear_all_bps( self ) :
        self.extra_selection_list = [ self.current_line_selection ]
        self.setExtraSelections( self.extra_selection_list )

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
        self.current_line_cursor = QTextCursor( text_block )
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
    The following method is the slot to receive the EmulatorStopped signal
    out of the memory module. The signal carries an int value which is the
    new PC. We want to find the statement (QTextBlock) that matches that PC,
    move the edit cursor to that line (thus highlighting it, see cursor_moved above),
    and make sure it is visible in the window.

    This requires:
    * Find the QTextBlock with a Statement containing that PC value.
    * Make a QTextCursor positioned to that line's origin.
    * Set that QTextCursor as the edit cursor (which incidentally
      clears any existing selection).
    * Tell the editor to make the cursor visible.
    '''

    def show_pc_line( self, PC ) :
        '''
        If we have main_window.clean_assembly, then we can rely on the S.PC values
        in the Statements in all the textblocks. If not, we can do nothing.
        '''
        if not self.main_window.clean_assembly :
            return
        '''
        Since execution usually moves forward, start looking with the current
        statement, expecting to get a match on it or the next statement along.
        '''
        this_block = self.textCursor().block()
        '''
        Scan forward looking for the matching PC, stopping at the end
        of the document. N.B. empty statements have S.PC=None.
        '''
        current_block = this_block
        while current_block.isValid() :
            U = current_block.userData()
            S = U.statement
            if PC == S.PC : # bingo
                break
            current_block = current_block.next()
        '''
        If that search failed, then current_block.isValid is False (end of
        document). Try again starting from the first line of the document
        down to here.
        '''
        if not current_block.isValid() :
            current_block = self.document().firstBlock()
            while current_block != this_block :
                U = current_block.userData()
                S = U.statement
                if PC == S.PC :
                    break
                current_block = current_block.next()

            if current_block == this_block :
                '''
                We failed to get a match, do nothing.
                '''
                return
        '''
        Make current_block the current cursor line (which invokes
        cursor_moved, above) and ensure it is visible. It will not
        necessarily be centered. If it was already visible on the screen,
        nothing happens.
        '''
        self.setTextCursor( QTextCursor( current_block ) )
        self.ensureCursorVisible()

    '''
    Clear the breakpoint status of a particular text block, if it has that
    status. The status has to be removed from chip8, but the tricky bit is
    getting the matching extra-selection out of the list. The extra selection
    has a text cursor. We match this block that cursor on the basis that both
    have the same document position value.

    Note that the following code modifies a list that is controlling
    a for-loop, ordinarily a no-no. But we immediately break the loop,
    so it's ok.
    '''
    def clear_bp_status( self, text_block:QTextBlock ) :
        if text_block.userState() == 1 :
            U = text_block.userData()
            S = U.statement
            chip8.bp_rem( S.PC )
            pos = text_block.position()
            for extra_sel in self.extra_selection_list :
                sel_pos = extra_sel.cursor.position()
                if sel_pos == pos and extra_sel != self.current_line_selection :
                    self.extra_selection_list.remove( extra_sel )
                    break
            text_block.setUserState( -1 )

    '''
    The following methods are dispatched from the keyPressEvent handler, below
    (except for replace_all which is called only from the Find dialog).
    '''

    '''
    Toggle the breakpoint status of the current line. If it ought not
    to be a breakpoint, or is currently a breakpoint, clear the breakpoint
    status. If it is not now a breakpoint and can be, set that status.
    Note this is the only place where breakpoint status is set on.
    All other breakpoint-related methods only clear it.
    '''
    def toggle_bp( self ) :
        this_block = self.textCursor().block()
        bp_state = this_block.userState()
        U = this_block.userData()
        S = U.statement
        if (S.PC is not None) \
           and (not S.text_error) \
           and (not S.expr_error) \
           and bp_state == -1 :
            chip8.bp_add( S.PC )
            extra_sel = self.make_extra_selection( BREAKPOINT_LINE_COLOR )
            extra_sel.cursor = QTextCursor( this_block )
            self.extra_selection_list.append( extra_sel )
            this_block.setUserState( 1 )
        else :
            '''
            This line either has a breakpoint that the user wants to clear
            (bp_state==1) or it is not elegible for breakpoints (because
            S.PC is None, indicating it has not been assembled, or because
            it has error status).
            In all cases, clear any bp status; in the latter, beep.
            '''
            self.clear_bp_status( this_block )
            if bp_state != 1 : QApplication.beep()

    '''
    This is called on the control-E key event. Starting from the line after
    the current line, scan forward for a textblock in which the Statement has
    either expr_error or text_error.
    '''
    def find_next_error_line( self ) :
        this_block = self.textCursor().block()
        next_block = this_block.next()
        while next_block.isValid() :
            U = next_block.userData()
            S = U.statement
            if S.text_error or S.expr_error :
                break
            next_block = next_block.next()
        if not next_block.isValid() :
            '''
            Try again from the top down.
            '''
            next_block = self.document().firstBlock()
            while next_block != this_block :
                U = next_block.userData()
                S = U.statement
                if S.text_error or S.expr_error :
                    break
                next_block = next_block.next()

            if next_block == this_block :
                '''
                We found no (other) errors.
                '''
                QApplication.beep()
                return
        self.setTextCursor( QTextCursor( next_block ) )

    '''
    Make the Find dialog visible. It's a modal dialog so it hogs the focus
    until the user clicks Close or hits ESC. Then it returns a code that we
    don't care about.

    While the dialog is running, it may call into the following methods.
    '''
    def start_find( self ) :
        retcode = self.find_dialog.exec_()

    '''
    This is the heart of the Find process, factored out of find_next and
    find_prior. The only difference between them is the flag value and
    which end of the document you go to, if you want to wrap.

    This method returns True when it found a match, and False when not.
    The only caller that cares is the replace_all method.
    '''
    def find_it( self, forward=True, wrap=True ) :
        find_flag = QTextDocument.FindCaseSensitively
        if not forward :
            find_flag |= QTextDocument.FindBackward
        '''
        Execute a find starting at the current selection, self.textCursor()
        '''
        new_cursor = self.document().find(
            self.find_dialog.find_text.text(),
            self.textCursor(),
            options=find_flag
        )
        if not new_cursor.hasSelection() :
            '''
            Search failed from the current point. If the caller wants, try it
            again from the other end of the document.
            '''
            if wrap :
                start_cursor = QTextCursor(
                    self.document().firstBlock() if forward \
                              else self.document().lastBlock()
                    )
                new_cursor = self.document().find(
                    self.find_dialog.find_text.text(),
                    start_cursor,
                    options= find_flag
                )
            '''
            If that didn't work, or wasn't wanted, return False.
            '''
            if not new_cursor.hasSelection() :
                return False
        '''
        Eureka! literally. Make that the edit selection and make it visible.
        '''
        self.setTextCursor( new_cursor )
        self.ensureCursorVisible()
        return True

    '''
    This is called from the FIND button of the dialog, and from the ^g key,
    to find the next match to the text in the find dialog.
    '''
    def find_next( self ) :
        hit = self.find_it( forward= True )
        if not hit :
            QApplication.beep()

    '''
    This is called from the keyEvent handler for control-shift-G, to find
    the previous match to the text entered to the find dialog.
    '''
    def find_prior( self ) :
        hit = self.find_it( forward= False )
        if not hit:
            QApplication.beep()

    '''
    This is called from the REPLACE button of the Find dialog, and from the
    following ^= and ^t methods. We use the contents of the Find dialog
    Replace lineedit to replace the current selection -- which we ASSUME is
    the result of having done a Find. But we don't check that.

    It would be possible to check; define a flag that is set True on a
    successful Find, and set False on any change of selection. It could be
    done here but I don't think it's necessary.
    '''
    def replace_selection( self ) :
        replace_text = self.find_dialog.replace_text.text()
        self.textCursor().insertText( replace_text )

    '''
    This is called from the control-t key event. Replace the current text
    and do a find-next.
    '''
    def replace_and_find( self ) :
        self.replace_selection()
        hit = self.find_it( forward=True)
        if not hit :
            QApplication.beep()

    '''
    This is called only from the ALL! button of the Find dialog. We could
    just blindly run through the document doing find_next, replace_selection
    until we hit the end. Which would be OK, but I prefer to add just a
    little code and give the user a chance to back out.

    We run through the document doing find_next() and making a list of
    QTextCursors for the 0-or-more text matches. If there were 0 matches,
    exit with a beep. If there was only 1 match, just do the replace.

    When there were 2 or more matches, put up a dialog saying how many of
    what and ask for OK or Cancel. On OK, do all in the list, in such a
    way that a single ^z backs out all changes.
    '''

    def replace_all( self ) :
        '''
        Move our edit cursor to the top of the document.
        '''
        self.setTextCursor( QTextCursor( self.document().firstBlock() ) )
        '''
        Make a list of text cursors for all matches.
        '''
        cursor_list = []
        while True:
            hit = self.find_it( forward= True, wrap= False )
            if not hit : break
            cursor_list.append( QTextCursor( self.textCursor() ) )
        '''
        If no hits, beep and exit.
        '''
        if 0 == len( cursor_list ) :
            QApplication.beep()
            return
        '''
        If just one hit, then the current document cursor is selecting that
        matched text. Do the replace and exit.
        '''
        if 1 == len( cursor_list ) :
            self.replace_selection( )
            return
        '''
        Let the user know how many changes we plan to make, of what to what.
        '''
        msg = '''Click YES to convert {} instances of
{}
to
{}'''.format( len(cursor_list),
              self.find_dialog.find_text.text(),
              self.find_dialog.replace_text.text()  )

        answer = QMessageBox.question(
            self,
            'Approve global replace',
            msg
            )
        if answer == QMessageBox.Yes :
            for cursor in cursor_list :
                self.setTextCursor( cursor )
                self.replace_selection( )

    '''

    Implement a keyPressEvent handler to capture the command keys we support,
       * control-B to toggle breakpoint status on the current line
       * control-E to jump to the next line with Error status
       * control-F to open a Find dialog
       * control-G to search forward to the next match
       * control-shift-G to search backward to the prior match
       * control-equals to replace
       * control-T to replace and find again
    '''
    def keyPressEvent(self, event: QKeyEvent ) -> None :
        '''
        The only keys we handle have the control modifier.
        '''
        modifiers = int( event.modifiers() )
        # uncomment this to see how many events this handles.
        #print( '{:X} {:X} {:X}'.format(modifiers,int(event.key()),key_code) )
        if modifiers & Qt.ControlModifier :
            '''
            Make sure it is one of the key+modifier combos we want.
            '''
            key_code = int( int( event.key() ) | modifiers )
            if key_code in self.key_dispatch :
                '''
                This is an event we handle, note that. Then dispatch the
                appropriate routine.
                '''
                event.accept()
                self.key_dispatch[ key_code ]()
                return
        '''
        Not one of our keys, pass it on to mamma.
        '''
        super().keyPressEvent(event)
        return

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
        self.status_line = QLineEdit()
        self.status_line.setReadOnly( True )
        self.status_line.setFont( chip8util.MONOFONT )
        self.status_line.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
        self.status_line.setMinimumWidth( chip8util.MONOFONT_METRICS.width( 'M'*30 ) )

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
        hbox.addWidget( self.status_line, 2, Qt.AlignLeft )

        self.check_button = chip8util.RSSButton()
        self.check_button.setText( 'CHECK' )
        self.load_button = chip8util.RSSButton()
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

        '''
        Create the Quit action, which Qt will put in the appropriate menu for
        the platform: File menu for Windows and Linux, App menu for mac. We
        connect the menu action's triggered signal to our own QWidget.close()
        method, which in turn will issue a QCloseEvent for this window to
        trap. See closeEvent() below for more comments.
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
    def do_assembly( self ) -> List[int]  :
        '''
        Clear the status line on the presumption that any error will
        have been fixed.
        '''
        self.status_line.clear()

        '''
        Because we are about to (re) assemble, clear all breakpoints both
        from the emulator and from any statements that have them. We have to
        do this statement by statement because all these statements will
        still be here (unlike File>New or >Open where we know all existing
        statements will be erased).
        '''
        first_block = self.document.firstBlock()
        next_block = first_block
        while next_block.isValid():
            self.editor.clear_bp_status( next_block )
            next_block = next_block.next()

        '''
        Assemble the document text, getting back a list of ints (which might
        be empty, for an empty doc).
        '''
        mem_load = assemble( first_block )
        if (mem_load) and mem_load[0] < 0 :
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
        self.highlighter.rehighlight()
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
        if mem_load is not None :
            chip8.reset_vm( mem_load )

    '''
    Copied from the Qt Application Example, maybe_save() is called
    whenever there is a chance of losing the user's work, to give
    the user an option of saving or cancelling the operation.
    Returns:
      - True if the current document is not modified OR if the
        user clicks Discard/Don't Save
      - False if user clicks Cancel (meaning abort this operation)
      - The result of File>Save if the user clicks Save -- and that might
        be False if the save fails or is cancelled, so abort.
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
        return True # document not modified or choice==QMB.Discard

    '''
    Set up a new document, either from File>Open or File>New.
    Put the current file name as the window title; save the file path (if
    given) as the window file path, and clear the modified flag if it is set.
    Clear a field in the editor, too.

    This is also an opportune place to tell the emulator to clear all
    breakpoints. This is only called when the active file is new and can
    have no existing breakpoints.
    '''
    def set_up_new_document( self, name: str, path: str = None ) :
        self.document.setModified( False )
        self.editor.last_text_block = None
        self.setWindowModified( False )
        self.setWindowFilePath( path )
        self.setWindowTitle( name )
        self.editor.clear_all_bps()
        chip8.bp_clear()

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
            self.set_up_new_document( "Untitled" )

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
        else :
            '''
            User clicked Cancel on maybe_save, or save failed.
            '''
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
        binary however, is almost guaranteed to contain a byte over 0x80.

        This disallows Latin-1 in assembler source files, or at least disallows
        the use of any character over 0x7f, symbols and accented characters.

        If it can't be decoded, assume it is a CHIP-8 binary file. Pass it to
        the disassembler which always returns a string. In either case, we
        end up with a string.
        '''
        source_string = ''
        try:
            source_string = byte_string.decode( 'ASCII', errors='strict' )
            '''
            It's an assembly source, so set the filename as our window title,
            and the file path as our file path -- i.e. it is safe to do a
            File>Save onto this file after editing.
            '''
            (prefix, filename) = os.path.split( chosen_path )
            self.set_up_new_document( filename, path=prefix )

        except Exception as E:
            '''
            It's a binary file. Convert to a source file, but we really do not
            want to encourage File>Save which would wipe out the binary with
            the source. So force it to an equivalent of New.
            '''
            source_string = disassemble( byte_string )
            self.set_up_new_document( "Untitled" )
            self.document.setModified( True )

        '''
        Install the source string as the contents of our document.
        This applies the syntax highlighter to every line, btw.
        '''
        self.document.setPlainText( source_string )
        self.document.setModified( False )

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
        self.set_up_new_document( filename, path=prefix )
        return self.file_save()



    '''
    Override the built-in closeEvent() method. Check to see if the
    current document is modified, and if so, ask the user if she wants
    to save it. If the user cancels, or a file_save fails, ignore the event,
    thus cancelling the shutdown.

    Otherwise, accept the event, save our geometry and
    invoke the closeAllWindows method to shut down the rest of the app.

    We want the Memory and Display windows to ignore the Red-X button on
    windows and equivalents elsewhere, but we also want them to close in this
    case. To that end we call them at a quit_signal_slot method so they know
    this is serious. (It's called quit_signal_slot because originally I
    hooked it to the File>Quit menu action, but it needs to be generalized to
    any close of the Source window.)

    '''
    def closeEvent( self, event:QCloseEvent ) :
        if self.maybe_save( "Quit" ) :
            '''
            When the window closes, write our geometry and spinbox value
            into the settings.
            '''
            SETTINGS.setValue( "source_page/size", self.size() )
            SETTINGS.setValue( "source_page/position", self.pos() )
            display.quit_signal_slot( )
            memory.quit_signal_slot( )
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
    pass
    #'''
    #Aaaaand we hack up some tests. Lasciate ogne speranza...
    #'''
    from binasm import binasm

    from PyQt5.QtWidgets import QApplication
    args = []
    the_app = QApplication( args )
    chip8util.initialize_mono_font()
    initialize(QSettings())
    the_app.exec_()



