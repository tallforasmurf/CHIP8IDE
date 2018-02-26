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
    CROSS-MODULE ITEMS

Define useful independent Qt resources that are needed in more than one module.

MONOFONT and MONOFONT_METRICS are used in both memory.py and source.py for\
displaying code and memory values.

RSSButton is a pushbutton class that is used in memory.py for Run/Stop and
Step, and in source.py for the Load and Check buttons.
'''

__all__ = [ 'MONOFONT', 'MONOFONT_METRICS', 'initialize_mono_font' ]

'''

This is called from chip8ide after creating the QApplication and before initializing other windows.

Use Qt facilities to get a monospaced font to use in all widgets.

Store it in MONOFONT and MONOFONT_METRICS for use from various other modules.

'''

from PyQt5.QtGui import (
    QFont,
    QFontInfo,
    QFontDatabase,
    QFontMetrics
    )

from PyQt5.QtCore import QSize

MONOFONT = None # type: QFont
MONOFONT_METRICS = None # type: QFontMetrics

def initialize_mono_font( ) :
    global MONOFONT, MONOFONT_METRICS
    '''
    Ask the QFontDatabase for the family of the recommended fixed-pitch font.
    It returns a QFont with a default point size, which we store in the global.
    '''
    MONOFONT = QFontDatabase.systemFont( QFontDatabase.FixedFont )
    MONOFONT_METRICS = QFontMetrics( MONOFONT )


'''

Define the "look" of the Run/Stop and other buttons. Use a scaled-up version
of MONOFONT and have a minimum size based on the font metrics of that font.

Usage note: the using module must import RSSButton and MONOFONT into the
global namespace, e.g. from chip8util import MONOFONT, RSSButton.

'''
from PyQt5.QtWidgets import QPushButton

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
