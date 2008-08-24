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
    """
    DataSource is the base class of all data plugins
    A datasource has to implement different functions to act as a DataSource
    Plugin.
    """
    def __init__(self):
        """
        Init the GObject base class of the DataSource class.
        """
        gobject.GObject.__init__(self)

    def load(self):
        """
        The load function returns a list of representations for all nodes
        below the DataSource parent node.
        The list items are tuples with the content
          * parent node tuple, (where an empty tuple refers to no parent)
          * DataNode (describing the data type)
        Example:
          [((), DataNode('abc', 'table', 'path', self)),
           ((0,), DataNode( ...
           ((0,0), DataNode( ...
           ((0,1), DataNode( ...
        """
        print "ERROR: load function not implemented in DataSource plugin [%s]" % str(self)
        return []

    def get_info(self):
        """
        get_info should return an information string describing the DataSource.
        """
        w = "WARNING: get_info() not implemented in that DataSource plugin [%s]" % str(self)
        print w
        return w

    def get_data(self, path, slicer=None):
        """
        get_data selects data form the DataSource.
        The path points to the data array or the data table.
        If the data is a table the slicer is the columnname.
        Note: The slicer is currently not used for numpy arrays.
        returns a numpy array (either a column from a table or the data itself)
        """
        print "ERROR: get_data not implemented in that DataSource plugin [%s] " % str(self)
        return None

    def get_slice(self, data, slicer):
        """
        get a single one-dimentional array slice of the multidimentional data array.
        data is a numpy array.
        slicer is a string that looks like a numpy slice. e.g. "[1,:,4]"
        """
        ## convert the slicer string into slice object
        if len(slicer) < 5:  # at least "[1,:]"
            raise ValueError, 'slice description too short: "%s"' % slicer

        toks = slicer[1:-1].split(',')

        if len(toks) != len(data.shape):
            raise ValueError, 'length of slicer "%s" does not match the' \
                  'data.ndim [%i]' % (slicer, data.ndim)

        slice_obj = []

        for t,s in zip(toks, data.shape):
            if t == ':':
                slice_obj.append(slice(None,None,None))
            elif int(t) > -1 and int(t) < s:
                slice_obj.append(slice(int(t), int(t)+1))
            else:
                raise ValueError, 'problem with slicer "%s", ' \
                      'data.shape %s' %(slicer, str(data.shape))

        # slicing with the slice object delivers an ndim array, even if only
        # a onedimensional array is in that array. --> flatten it.
        return data[tuple(slice_obj)].flatten()

    def get_shape(self, path):
        """
        This function is required to get the shape of the multidimensional numpy array
        located at path. The shape is a tuple.
        This function is only required if the DataSource uses numpy arrays as data representation.
        """
        print "ERROR: get_shape not implemented in that DataSource plugin [%s] " % str(self)
        return None

    def get_tableinfo(self, path):
        """
        This function returns a info string about the table at the location path.
        This function is only required if the DataSource uses tables as data representation.
        """
        w = "WARNING: get_info() not implemented in that DataSource plugin [%s]" % str(self)
        print w
        return w

    def get_columnnames(self, path):
        """
        This function returns a list of column names of the table at the location path.
        This function is only required if the DataSource uses tables as data representation.
        """
        print "ERROR: get_columnnames not implemented in that DataSource plugin [%s] " % str(self)
        return []

gobject.type_register( DataSource )


class DataNode(gobject.GObject):
    """
    DataNode represents a single data or folder element of the data tree.
    """
    def __init__(self, name, datatype, path, source):
        gobject.GObject.__init__(self)
        self.name = name
        self.datatype = datatype
        self.sourcepath = path
        self.datasource = source

    def get_name(self):
        """
        returns the name of this DataNode
        """
        return self.name

    def get_info(self):
        """
        returns some more info about this DataNode and the data that the node
        represents
        """
        sourceinfo = self.datasource.get_info()
        obj_info = "\nPath: " + self.sourcepath \
                   + "\nName: " + self.name + "\nType: " + self.datatype
        data_info = ""
        if self.datatype == "table":
            data_info = "\nTableInfo:\n" + self.datasource.get_tableinfo(self.sourcepath)
        return sourceinfo + obj_info + data_info

    def get_type(self):
        """
        return the datatype of this DataNode
        """
        return self.datatype

gobject.type_register( DataNode )
