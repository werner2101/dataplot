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


class DataSource(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)

    def getdata(self, path):
        print "getdata not implemented in that plugin: ", str(path)

    def getinfo(self):
        print "getinfo not implemented in that DataSource plugin"

gobject.type_register( DataSource )




class DataNode(gobject.GObject):

    name = ""
    datatype = None
    sourcepath = None
    datasource = None
    
    def __init__(self, name, datatype, path, source):
        gobject.GObject.__init__(self)
        self.name = name
        self.datatype = datatype
        self.sourcepath = path
        self.datasource = source

    def getdata(self):
        self.datasource.getdata(self.sourcepath)

    def getname(self):
        return self.name

    def getinfo(self):
        sourceinfo = self.datasource.getinfo()
        return sourceinfo + "\nPath: " + str(self.sourcepath) \
               + "\nName: " + self.name + "\nType: " + self.datatype

    def gettype(self):
        return self.datatype
    

gobject.type_register( DataNode )
