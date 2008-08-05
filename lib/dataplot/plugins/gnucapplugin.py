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

import os.path

import gtk, gobject, gtk.gdk
import numpy

import datasource


class GnucapPlugin(datasource.DataSource):
    """
    The gnucap plugin loads a whitespace seperated datafile to
    a table. The first line are the column titles.
    """
    name = "gnucap"
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.table = {}   ## a dictionary to numpy arrays
        self.colnames = []
        self.filename = filename
        self.testdatadict = {}
        self.loadfile()

    def loadfile(self):
        lines = open(self.filename).readlines()
        self.colnames = lines[0].split()

        rows = [ numpy.array([float(i) for i in l.split()]) for l in lines[1:] ]
        array = numpy.vstack(rows)
        for i, col in enumerate(self.colnames):
            self.table[col] = array[:,i]
        
    def load(self):
        node = datasource.DataNode("gnucap-data", "table", "/table", self)
        return [((), node)]
                
    def get_data(self, path, slicer):
        return self.table[slicer]

    def get_columnnames(self, path):
        return self.colnames

    def get_info(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename

    def get_tableinfo(self, path):
        return "Colnames: " + " ".join(self.get_columnnames([])) \
               + "\nRows: %i " % len(self.table[self.colnames[0]])

