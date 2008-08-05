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
import touchstone


class TouchstonePlugin(datasource.DataSource):
    """
    The TouchstonePlugin adapts the touchstone class into a DataSource.
    The s-parameters are presented in different formats as data tables.
    Note: All tables represent the same data.
    """
    name = "touchstone"
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.filename = filename
        self.tabledict = {}
        self.touchstone = touchstone.touchstone(filename)
        
    def load(self):
        ret = []
        l = [('unmodified','orig'),
             ('magnitude angle', 'ma'),
             ('magnitude(db) angle', 'db'),
             ('real imaginary', 'ri')]
        for name, key in l:
            path = '/'+ name
            self.tabledict[path] = key
            node = datasource.DataNode(name, 'table', path, self)
            ret.append(((), node))
        return ret
                
    def get_data(self, path, slicer):
        data = self.touchstone.get_sparameter_data(format=self.tabledict[path])
        return data.get(slicer, None)

    def get_info(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename
        
    def get_columnnames(self, path):
        names = self.touchstone.get_sparameter_names(self.tabledict[path])
        return names
            
    def get_tableinfo(self, path):
        format = self.touchstone.get_format(self.tabledict[path])
        colnames = " ".join(self.get_columnnames(path))
        return "Format: %s\nColnames: %s\n" %(format, colnames)
