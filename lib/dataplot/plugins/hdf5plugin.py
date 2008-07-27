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
import tables

import datasource


class Hdf5Plugin(datasource.DataSource):
    """
    The TestPlugin is used to test different kinds of DataSource elements.
    It can be used as example to write other plugins
    """
    name = "hdf5"
    
    def __init__(self, filename):
        datasource.DataSource.__init__(self)
        self.filename = filename
        self.hdf = tables.openFile(self.filename, "r")
        
    def load(self):
        """
        Build a list with all hdf5 nodes and return it to the caller
        """
        ret = []
        parent = []
        stack = [('/',())]   # root node is in the stack
        
        while stack != []:
            parentpath, parent = stack.pop()
            n_child = -1
            for node in self.hdf.getNode(parentpath):
                n_child += 1
                pathname = node._v_pathname
                if type(node) == tables.group.Group:
                    stack.append((pathname, parent+(n_child,)))
                    nodetype = 'folder'
                elif type(node) == tables.array.Array:
                    l = len(node.shape)
                    nodetype = {1:'array1d', 2: 'array2d', 3: 'array3d'}.get(l)
                elif type(node) == tables.table.Table:
                    nodetype = 'table'
                else:
                    print "ERROR: unknown type [%s]" % str(type(node))
                    continue
                path = pathname.split('/')[1:]
                datanode = datasource.DataNode(path[-1], nodetype, tuple(path), self)

                ret.append((parent, datanode))
        return ret
                
    def get_info(self):
        return "Sourcename: " + self.name \
               + "\nFilename: " + self.filename
        
    def get_data(self, path, slicer):
        p = '/'.join(path)
        node = self.hdf.getNode('/' + p)
        if type(node) == tables.array.Array:
            return node
        else: # a table
            return node.col(slicer)

    def get_shape(self, path):
        p = '/'.join(path)
        node = self.hdf.getNode('/' + p)
        return node.shape

    def get_tableinfo(self, path):
        colnames = ' '.join(self.get_columnnames(path))
        p = '/'.join(path)
        table = self.hdf.getNode('/' + p)
        rows = len(table)
        return 'table lenght: %i\nColnames: %s' % (rows, colnames)

    def get_columnnames(self, path):
        p = '/'.join(path)
        table = self.hdf.getNode('/' + p)
        return table.colnames



    
