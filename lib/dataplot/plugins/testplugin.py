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


a = numpy.random.rand(30,10)

table1 = dict([("test" + str(i), a[:,i]) for i in xrange(a.shape[1])])
table2 = dict([("test" + str(i), a[i,:]) for i in xrange(a.shape[0])])

testdata = [[[], "/root", "testroot", "folder", None],
            [[0], "/root/table1", "testtable1", "table", table1],
            [[0], "/root/table2", "testtable2", "table", table2],
            [[0], "/root/arrays", "arrays", "folder", None],
            [[0,1], "/root/arrays/data1d1", "data1d1", "array1d", numpy.arange(100)],
            [[0,1], "/root/arrays/data1d2", "data1d2", "array1d", numpy.random.rand(100)],
            [[0,1], "/root/arrays/data2d", "data2d", "array2d", numpy.random.rand(20,20)],
            [[0,1], "/root/arrays/data3d", "data3d", "array3d", numpy.random.rand(10,20,30)]]

class TestPlugin(datasource.DataSource):
    """
    The TestPlugin is used to test different kinds of DataSource elements.
    It can be used as example to write other plugins
    """
    name = "test"
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.filename = filename
        self.testdatadict = {}
        self.testtabledict = {}
        
    def load(self):
        ret = []
        for dataset in testdata:
            localparent, path, name, nodetype, data = dataset
            node = datasource.DataNode(name, nodetype, path, self)
            ret.append((localparent, node))
            if nodetype[:5] == "array":
                self.testdatadict[path] = data
            elif nodetype == "table":
                self.testtabledict[path] = data
        return ret
                
    def get_info(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename
        
    def get_data(self, path, slicer):
        if self.testdatadict.has_key(path):
            return self.testdatadict[path]
        else:
            return self.testtabledict[path][slicer]

    def get_shape(self, path):
        return self.testdatadict[path].shape

    def get_tableinfo(self, path):
        return "Colnames: " + " ".join(self.get_columnnames(path)) + "\n"

    def get_columnnames(self, path):
        return self.testtabledict[path].keys()

