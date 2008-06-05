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


bitmaps = [["notebook", "data/bitmaps/plot_notebook.png"],
           ["singleplot", "data/bitmaps/plot_singleplot.png"],
           ["xaxis", "data/bitmaps/plot_xaxis.png"],
           ["yaxis", "data/bitmaps/plot_yaxis.png"],
           ["math", "data/bitmaps/plot_math.png"]]

class PlotTree(gtk.TreeView):


    __gsignals__ = { 'info-message':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_STRING, )),
                     }
    
    def __init__(self, plotmodel):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), pixbuf=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.append_column(column)
        self.set_property("enable-tree-lines", True)
        self.set_property("headers-visible", False)

        self.load_icons()
        self.set_model(plotmodel)
        
        ## SETUP signals
        self.connect("cursor-changed", self.event_cursor_changed)
        

    def load_icons(self):
        self.icons = {}
        for name,filename in bitmaps:
            self.icons[name] = gtk.gdk.pixbuf_new_from_file(filename)

    def add_node(self, parentpath, nodeobject):
        m = self.get_model()
        if not parentpath:
            i_new = m.append(None)
        else:
            i = m.get_iter(parentpath)
            i_new = m.append(i)
        m.set(i_new, 0, self.icons[nodeobject.nodetype], 1, nodeobject.name, 2, nodeobject)
        return m.get_path(i_new)

    def add_plot(self, name, subplotname="subplot"):
        plot = PlotNode(name)
        path = self.add_node(None, plot)
        subplot = SubplotNode("subplot")
        spath1 = self.add_node(path, subplot)
        return spath1


    def event_cursor_changed(self, treeview):
        """
        Print the infotext of the object that is attached into the
        third column of the treemodel.
        """
        m = self.get_model()
        path = self.get_cursor()[0]
        self.emit('info-message', m[path][2].getinfo())


    def test(self):
        plot = PlotNode("plot1")
        path = self.add_node(None, plot)

        plot = PlotNode("plot2")
        path = self.add_node(None, plot)

        subplot = SubplotNode("subplot1")
        spath1 = self.add_node(path, subplot)

        xaxis = DataNode("x-axis","xaxis")
        xpath = self.add_node(spath1, xaxis)

        yaxis = DataNode("y-axis1", "yaxis")
        self.add_node(xpath, yaxis)
        yaxis = DataNode("y-axis2", "yaxis")
        self.add_node(xpath, yaxis)
        
        subplot = SubplotNode("subplot2")
        spath2 = self.add_node(path, subplot)

        xaxis = DataNode("x-axis","xaxis")
        xpath = self.add_node(spath2, xaxis)

        yaxis = DataNode("y-axis1", "yaxis")
        self.add_node(xpath, yaxis)
        

class PlotNode(gobject.GObject):

    name = None
    nodetype = "notebook"

    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name

    def getinfo(self):
        return "PlotNode info not implemented yet"


class SubplotNode(gobject.GObject):

    name = None
    nodetype = "singleplot"

    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name

    def getinfo(self):
        return "SubplotNode info not implemented yet"


class DataNode(gobject.GObject):

    name = None
    nodetype = ""
    datasource = None
    datapath = None
    dataslicer = None
    simpleoperator = None

    def __init__(self, name, nodetype):
        gobject.GObject.__init__(self)
        self.name = name
        self.nodetype = nodetype

    def set_data(self, datasource, datapath, dataslicer=None):
        self.datasource = datasource
        self.datapath = datapath
        self.dataslicer = dataslicer

    def getinfo(self):
        x = ["Name: " + str(self.name),
             "Type: " + str(self.nodetype),
             "Data Source: " + str(self.datasource),
             "Data Path: " + str(self.datapath),
             "Slicer: " + str(self.dataslicer),
             "Operator: " + str(self.simpleoperator)]

        return "\n".join(x)
    
