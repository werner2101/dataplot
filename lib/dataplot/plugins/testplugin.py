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


import gtk, gobject, gtk.gdk
import numpy

import datasource

testdata = [[[], ["root"], "testroot", "folder", None],
            [[0], ["root","table"], "testtable", "table", None],
            [[0], ["root","arrays"], "arrays", "folder", None],
            [[0,1], ["root","arrays","data1d1"], "data1d1", "array1d", numpy.arange(100)],
            [[0,1], ["root","arrays","data1d2"], "data1d2", "array1d", numpy.random.rand(100)],
            [[0,1], ["root","arrays","data2d"], "data2d", "array2d", numpy.random.rand(20,20)],
            [[0,1], ["root","arrays","data3d"], "data3d", "array3d", numpy.random.rand(10,20,30)]]

class TestPlugin(datasource.DataSource):
    name = "test"
    filename = "None"
    testdatadict = {}
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.filename = filename
        
    def load(self):
        ret = []
        for dataset in testdata:
            localparent, path, name, nodetype, data = dataset
            node = datasource.DataNode(name, nodetype, path, self)
            ret.append((localparent, node))
            if data != None:
                self.testdatadict[tuple(path)] = data
        return ret
                
    def getdata(self, path):
        if type(self.testdatadict[tuple(path)]) == numpy.ndarray:
            return self.testdatadict[tuple(path)]
        else:
            print "Not implemented yet"

    def getinfo(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename
        
    def getcolumnnames(self, path=None):
        return ["Col1", "Col2"]

    def gettableinfo(self, path):
        return "Colnames: " + " ".join(self.getcolumnnames([])) + "\n Rows: 20"
