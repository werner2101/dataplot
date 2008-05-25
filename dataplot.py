#!/usr/bin/python
# -*-Python-*-

# dataplot - plot hierachical datasets
# Copyright (C) 2008 Werner Hoch <werner.ho@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import pygtk
pygtk.require('2.0')

import sys, gtk, os.path

sys.path.insert(0, os.path.abspath("lib/dataplot"))

from gui import *

#gtk.window_set_default_icon_name('geda-xgsch2pcb')

if len(sys.argv) > 1:
    window = MainWindow(sys.argv[1:])
else:
    window = MainWindow()
window.show_all()

gtk.main()

