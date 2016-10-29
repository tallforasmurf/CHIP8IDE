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
This is the top level of the CHIP8IDE program. It sets up the PyQt application,
creates the three top windows, and waits for termination.

We use the name of the app in a couple of places so define it once.
'''

APPNAME = 'CHIP8IDE'

'''
Determine the platform. Based on that, work out the path to a writable
location for our log files.
'''

import sys
import os

if sys.platform == 'darwin' : # Mac OS
    log_path = os.path.expanduser( '~/Library/Logs' )

elif hasattr( sys, 'getwindowsversion' ) : # Some level of Windows
    if 'TMP' in os.environ :
        log_path = os.environ['TMP']
    elif 'TEMP' in os.environ :
        log_path = os.environ['TEMP']
    elif 'WINDIR' in os.environ :
        log_path = os.path.join( os.environ['WINDIR'], 'TEMP' )
    else :
        log_path = '/Windows/Temp'

else: # Assuming Linux; could be BSD
    log_path = '/var/tmp'

log_path = os.path.join( log_path, 'CHIP8IDE.log' )

'''
Prepare logging to a rotating set of log files located on that path.
'''

import logging, logging.handlers
log_handler = logging.handlers.RotatingFileHandler(
    log_path, mode='a', encoding='UTF-8', maxBytes=100000, backupCount=5
)


'''
Set up the log at level INFO, meaning that INFO and ERROR messages
go into it while DEBUG messages do not.

TODO: find some way to make this optional. Not from command line
options since, as a GUI app, we don't usually see command line options.
Maybe an environment var?
'''

logging.basicConfig( handlers=[log_handler], level=logging.INFO )

'''
Write startup lines to the log
'''
import datetime
now = datetime.datetime.now()

from PyQt5.QtCore import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR

logging.info( '==========================================' )
logging.info( '{} starting up on {} with Qt {} and PyQt {}'.format(
    APPNAME,
    now.ctime(),
    QT_VERSION_STR,
    PYQT_VERSION_STR
    )
             )

'''
Create the QApplication. This does a ton of Qt setup stuff.
'''

from PyQt5.QtWidgets import QApplication
args = []
the_app = QApplication( args )

'''
With the application started, set the constants that define where
the settings file is stored and what it is called. Then open the settings.

Locations for Qt settings values:
Linux: $HOME/.config/TassoSoft/CHIP8IDE.conf
Mac OSX: $HOME/Library/Preferences/com.TassoSoft.CHIP8IDE.plist
Windows (registry): HKEY_CURRENT_USER\Software\TassoSoft\CHIP8IDE

'''

the_app.setOrganizationName( "TassoSoft" )
the_app.setOrganizationDomain( "tassos-oak.com" )
the_app.setApplicationName( APPNAME )

from PyQt5.QtCore import QSettings
the_settings = QSettings()

'''
Uncomment the following to wipe all settings forcing windows
back to their defaults.
'''
#the_settings.clear()

'''
Import all the modules. This lets Python create their namespaces.
Call the .initialize() entry of each, passing the QSettings object.
Each saves a reference to that object to use when it receives the
QcloseEvent.

Import in the following order:
   display.py has no dependencies
'''

import display

display.initialize( the_settings )

'''
   chip8.py refers to display entry points
'''

import chip8

chip8.initialize( the_settings )


'''
   memory.py refers to chip8 and display entry points
'''

import memory

memory.initialize( the_settings )

'''
   source.py refers to chip8 and display entry points
'''

import source

source.initialize( the_settings )

'''
All the windows are visible.

Start the application event loop. This does not return until the
application ends, e.g. File > Quit.

Each window traps the close event and saves its geometry in the settings.
'''

the_app.exec_()

'''
The app has terminated, probably due to File>Quit. It delivered a
QCloseEvent to each of the three windows, which should have saved their
geometry in the settings. The chip8 module doesn't have a QWidget so it
won't have gotten the word. (Always that 10%...) Just in case it wants to
save something, call it.
'''

chip8.closeEvent()

'''
Annotate the log file for shutdown.
'''

now = datetime.datetime.now()
logging.info( '{} shutting down at {}'.format( APPNAME, now.ctime() ) )
logging.info( '==========================================' )

'''
And that's that.
'''