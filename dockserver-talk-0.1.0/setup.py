from distutils.core import setup
import glob

setup (name = 'dockserver-talk',
       version = '0.1.0',
       description = \
       'A python package for communication with a Slocum glider dockserver.',
       author = 'Lucas Merckelbach',
       author_email = 'lucas.merckelbach@hzg.de',
       url = 'https://sourceforge.net/projects/dockserver-talk',
       license = 'GPLv.3',
       packages = ['dockserverTalk'],
       py_modules=[],
       data_files=[('share/dockserverTalk/examples',glob.glob('examples/*'))],
       scripts = [],
       long_description ='''
                dockserver-talk

Dockserver-talk is a python package intended for communication with a Slocum glider
dockserver. 


Two applications that have been built using this package:

B.UG.S: an application to track  buoys, underwater gliders and ships, respective to a reference 
        location (e.g. a ship)

Surfalarm : an application that interfaces with a (GSM) modem. It can send text messages, or 
            initiate phone calls, depending on particular strings seen in the glider dialogs.

''')



