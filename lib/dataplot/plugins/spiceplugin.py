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
import spice


class SpicePlugin(datasource.DataSource):
    """
    The SpicePlugin adapts the spice class into a DataSource.
    Each plot in the spice simulation data file is represented
    as a table.
    """
    name = "spice"
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.filename = filename
        self.tabledict = {}
        self.plotlist = spice.spice_read(filename).get_plots()
        
    def load(self):
        ret = []
        for i, p in enumerate(self.plotlist):
            name = "plot%i"%(i)
            path = (name,)
            self.tabledict[path] = p
            node = datasource.DataNode(name, "table", path, self)
            ret.append(((), node))
        return ret
                
    def get_data(self, path, slicer):
        scale_vector = self.tabledict[tuple(path)].get_scalevector()
        if slicer == scale_vector.name:
            return scale_vector.get_data()
        for data_vector in self.tabledict[tuple(path)].get_datavectors():
            if slicer == data_vector.name:
                return data_vector.get_data()
        return None

    def get_info(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename
        
    def get_columnnames(self, path):
        vectors = [self.tabledict[tuple(path)].get_scalevector()]
        vectors.extend(self.tabledict[tuple(path)].get_datavectors())

        names = [ v.name for v in vectors ]
        return names
            
    def get_tableinfo(self, path):
        return "Colnames: " + " ".join(self.get_columnnames(path)) + "\n"
