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


bitmaps = [["file", "data/bitmaps/data_file.png"],
           ["folder", "data/bitmaps/data_folder.png"],
           ["table", "data/bitmaps/data_table.png"],
           ["array1d","data/bitmaps/data_array1d.png"],
           ["array2d", "data/bitmaps/data_array2d.png"],
           ["array3d", "data/bitmaps/data_array3d.png"]]

class DataTree(gtk.TreeView):
    """
    The DataTree class contains the view part of all data sources.
    """
    __gsignals__ = { 'info-message':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_STRING, )),
                     'table-activated':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_OBJECT,)),
                     'array-activated':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_OBJECT,))
                     }
    
    

    def __init__(self, datamodel):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), pixbuf=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.append_column(column)
        self.set_property("enable-tree-lines", True)
        self.set_property("headers-visible", False)
        self.set_model(datamodel)

        ## SETUP signals
        self.connect("cursor-changed", self.event_cursor_changed)
        self.connect("row-activated", self.event_row_activated)

    def event_cursor_changed(self, treeview):
        """
        Print the infotext of the object that is attached into the
        third column of the treemodel.
        """
        m = treeview.get_model()
        path = treeview.get_cursor()[0]
        self.emit('info-message', m[path][2].get_info())

    def event_row_activated(self, treeview, path, column):
        """
        This event is triggered if a tree element is double clicked
        I will emit a new signal to the gui which nodetype has been
        activated
        """
        m = treeview.get_model()
        node = m[path][2]
        if node.get_type() == "table":
            self.emit('table-activated', node)
        elif node.get_type() in ["array2d", "array3d"]:
            self.emit('array-activated', node)


class DataModel(gtk.TreeStore):
    """
    The PlotModel class contains the model part of the Plot Tree.
    """
    def __init__(self):
        gtk.TreeStore.__init__(self,
                               gtk.gdk.Pixbuf,
                               gobject.TYPE_STRING,
                               gobject.TYPE_OBJECT)

        self.icons = {}
        for name,filename in bitmaps:
            self.icons[name] = gtk.gdk.pixbuf_new_from_file(filename)

    
    def add_node(self, parentpath, nodeobject):
        if not parentpath:
            i_new = self.append(None)
        else:
            i = self.get_iter(parentpath)
            i_new = self.append(i)
        self.set(i_new,
                 0, self.icons[nodeobject.get_type()],
                 1, nodeobject.get_name(),
                 2, nodeobject)
        return self.get_path(i_new)

    def create_name(self, name):
        """
        We need uniq names of our sources. If a name is already in use,
        attach a (i) suffix to the given name
        """
        d = dict([ (row[1],0) for row in self ])
        if d.has_key(name):
            i = 2
            while (1):
                new_name = name + "(%i)"%i
                if d.has_key(new_name):
                    i += 1
                else:
                    return new_name
        else:
            return name
