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

import testplugin



bitmaps = [["file", "data/bitmaps/data_file.png"],
           ["folder", "data/bitmaps/data_folder.png"],
           ["table", "data/bitmaps/data_table.png"],
           ["array1d","data/bitmaps/data_array1d.png"],
           ["array2d", "data/bitmaps/data_array2d.png"],
           ["array3d", "data/bitmaps/data_array3d.png"]]

class DataTree(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), pixbuf=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.append_column(column)
        self.set_property("enable-tree-lines", True)
        self.set_property("headers-visible", False)

        self.load_icons()
        self.load_plugins()
        self.create_model()
        self.test()

    def load_icons(self):
        self.icons = {}
        for name,filename in bitmaps:
            self.icons[name] = gtk.gdk.pixbuf_new_from_file(filename)

    def load_plugins(self):
        self.plugins = {}
        self.plugins["test"] = testplugin.TestPlugin

    def create_model(self):
        model = gtk.TreeStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        self.set_model(model)

    def test(self):
        self.load_file("abc filename", "abc", "test")


    def load_file(self, filename, name, plugin):
        mm = self.get_model()
        ii = mm.append(None)
        mm.set(ii, 0, self.icons["file"], 1, name)
        parent = mm.get_path(ii)
        self.plugins[plugin](filename, self, parent)

    def newnode(self, parent, localparent, node):
        mm = self.get_model()
        mm.set(mm.append(mm.get_iter(parent + tuple(localparent))),
               0, self.icons[node.gettype()],
               1, node.getname())
        
        


