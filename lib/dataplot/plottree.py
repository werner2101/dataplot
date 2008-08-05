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


import math
import gtk, gobject, gtk.gdk
import numpy
import matplotlib.figure
import matplotlib.backends.backend_gtk


bitmaps = [["notebook", "data/bitmaps/plot_notebook.png"],
           ["singleplot", "data/bitmaps/plot_singleplot.png"],
           ["xaxis", "data/bitmaps/plot_xaxis.png"],
           ["yaxis", "data/bitmaps/plot_yaxis.png"],
           ["math", "data/bitmaps/plot_math.png"]]

class PlotTree(gtk.TreeView):
    """
    The PlotTree class contains the view part of the all data that
    is required to represent the plots.
    """

    __gsignals__ = { 'info-message':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_STRING, )),
                     'plotnode-activated':
                     ( gobject.SIGNAL_NO_RECURSE,
                       gobject.TYPE_NONE,
                       (gobject.TYPE_OBJECT,))
                     }
    
    def __init__(self, plotmodel):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), pixbuf=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.append_column(column)
        self.set_property("enable-tree-lines", True)
        self.set_property("headers-visible", False)

        self.set_model(plotmodel)
        
        ## SETUP signals
        self.connect("cursor-changed", self.event_cursor_changed)
        self.connect("row-activated", self.event_row_activated)
        

    def event_cursor_changed(self, treeview):
        """
        Print the infotext of the object that is attached into the
        third column of the treemodel.
        """
        m = self.get_model()
        path = self.get_cursor()[0]
        self.emit('info-message', m[path][2].getinfo())

    def event_row_activated(self, treeview, path, column):
        
        node = treeview.get_model()[path][2]
        self.emit('plotnode-activated', node)


class PlotModel(gtk.TreeStore):
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
        self.set(i_new, 0, self.icons[nodeobject.nodetype], 1, nodeobject.name, 2, nodeobject)
        return self.get_path(i_new)

    def add_line(self, ypath):
        ynode = self.get_value(self.get_iter(ypath), 2)
        xnode = self.get_value(self.get_iter(ypath[0:3]),2)
        subplotnode = self.get_value(self.get_iter(ypath[0:2]),2)

        yv = ynode.get_vector()
        xv = xnode.get_vector()
        if xv == None:
            xv = numpy.arange(len(yv))

        axes = subplotnode.axes
        ynode.line = axes.plot(xv, yv, label=ynode.name)
                

class PlotNode(gobject.GObject):

    nodetype = "notebook"

    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name
        self.figure = matplotlib.figure.Figure()
        self.plot = matplotlib.backends.backend_gtk.FigureCanvasGTK(self.figure)

    def getinfo(self):
        return "Plot: " + self.name

    def replot(self):
        self.figure.canvas.draw()



class SubplotNode(gobject.GObject):

    nodetype = "singleplot"
    lookup = {"1": True, "0": False}

    def __init__(self, name, figure, plot=111):
        gobject.GObject.__init__(self)
        self.name = name
        self.figure = figure
        self.axes = figure.add_subplot(plot)
        self.properties = {'xmin': "",
                           'xmax': "",
                           'ymin': "",
                           'ymax': "",
                           'ylog': "0",
                           'xlog': "0",
                           'xlabel': "",
                           'ylabel': "",
                           'title': "",
                           'grid': "1",
                           'legend': "0"}
        self.figure.canvas.connect('scroll_event', self.event_scroll)


    def event_scroll(self, widget, event):
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.state & gtk.gdk.SHIFT_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.zoomy("out")
                else:
                    self.zoomy("in")
            else:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.zoomx("out")
                else:
                    self.zoomx("in")
        else:
            if event.state & gtk.gdk.SHIFT_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.pany("up")
                else:
                    self.pany("down")
            else:
                if event.direction == gtk.gdk.SCROLL_UP:
                    self.panx("right")
                else:
                    self.panx("left")
        self.figure.canvas.draw()

    def zoomx(self, direction="in"):
        [xmin, xmax, ymin, ymax] = self.axes.axis()
        if direction == "out":
            if self.properties["xlog"] == "1":
                qx = 0.2 * math.log10(xmax / xmin)
                xmax = xmax * 10**(qx)
                xmin = xmin * 10**(-qx)
            else:
                diffx = xmax - xmin
                xmax = xmax + 0.2*diffx
                xmin = xmin - 0.2*diffx
        else:
            if self.properties["xlog"] == "1":
                qx = 0.1 * math.log10(xmax / xmin)
                xmax = xmax * 10**(-qx)
                xmin = xmin * 10**(qx)
            else:
                diffx = xmax - xmin
                xmax = xmax - 0.1*diffx
                xmin = xmin + 0.1*diffx
        self.axes.axis(xmin=xmin, xmax=xmax)

    def zoomy(self, direction="in"):
        [xmin, xmax, ymin, ymax] = self.axes.axis()
        if direction == "out":
            if self.properties["ylog"] == "1":
                qy = 0.2 * math.log10(ymax / ymin)
                ymax = ymax * 10**(qy)
                ymin = ymin * 10**(-qy)
            else:
                diffy = ymax - ymin
                ymax = ymax + 0.2*diffy
                ymin = ymin - 0.2*diffy
        else:
            if self.properties["ylog"] == "1":
                qy = 0.1 * math.log10(ymax / ymin)
                ymax = ymax * 10**(-qy)
                ymin = ymin * 10**(qy)
            else:
                diffy = ymax - ymin
                ymax = ymax - 0.1*diffy
                ymin = ymin + 0.1*diffy
        self.axes.axis(ymin=ymin, ymax=ymax)

    def panx(self, direction="left"):
        [xmin, xmax, ymin, ymax] = self.axes.axis()
        if direction == 'left':
            m = 1
        else:
            m = -1
        if self.properties["xlog"] == "1":
            qx = 0.1 * math.log10(xmax / xmin)
            xmax = xmax * 10**(m*qx)
            xmin = xmin * 10**(m*qx)
        else:
            diffx = 0.1 * (xmax - xmin)
            xmax = xmax + m*diffx
            xmin = xmin + m*diffx
        self.axes.axis(xmin=xmin, xmax=xmax)

    def pany(self, direction="up"):
        [xmin, xmax, ymin, ymax] = self.axes.axis()
        if direction == 'up':
            m = 1
        else:
            m = -1
        if self.properties["ylog"] == "1":
            qy = 0.1 * math.log10(ymax / ymin)
            ymax = ymax * 10**(m*qy)
            ymin = ymin * 10**(m*qy)
        else:
            diffy = 0.1 * (ymax - ymin)
            ymax = ymax + m*diffy
            ymin = ymin + m*diffy
        self.axes.axis(ymin=ymin, ymax=ymax)

    def getinfo(self):
        return "Subplot: " + self.name

    def set_properties(self, properties):
        self.properties = properties
        self.update()

    def update(self):
        if self.properties["xlog"] == "1":
            self.axes.set_xscale('log')
        else:
            self.axes.set_xscale('linear')

        if self.properties["ylog"] == "1":
            self.axes.set_yscale('log')
        else:
            self.axes.set_yscale('linear')

        self.axes.set_xlabel(self.properties['xlabel'])
        self.axes.set_ylabel(self.properties['ylabel'])
        self.axes.set_title(self.properties['title'])

        self.axes.grid(self.lookup[self.properties['grid']])

        if self.properties['legend'] == "1":
            self.axes.legend(loc='best')
        else:
            l = self.axes.legend(())
            l.draw_frame(False)
                             
        self.axes.axis('auto')
        if (self.properties["xmin"]) != "":
            self.axes.axis(xmin=float(self.properties["xmin"]))
        if (self.properties["xmax"]) != "":
            self.axes.axis(xmax=float(self.properties["xmax"]))
        if (self.properties["ymin"]) != "":
            self.axes.axis(ymin=float(self.properties["ymin"]))
        if (self.properties["ymax"]) != "":
            self.axes.axis(ymax=float(self.properties["ymax"]))

        self.figure.canvas.draw()

    def get_properties(self):
        [xmin, xmax, ymin, ymax] = self.axes.axis()
        self.properties["xmin"] = str(xmin)
        self.properties["xmax"] = str(xmax)
        self.properties["ymin"] = str(ymin)
        self.properties["ymax"] = str(ymax)
        return self.properties
        


class DataNode(gobject.GObject):

    def __init__(self, name, nodetype):
        gobject.GObject.__init__(self)
        self.name = name
        self.nodetype = nodetype
        self.datasource = None
        self.sourcename = None
        self.datapath = None
        self.dataslicer = None
        self.simpleoperator = None

    def set_data(self, datasource, sourcename, datapath, dataslicer=None):
        self.datasource = datasource
        self.sourcename = sourcename
        self.datapath = datapath
        self.dataslicer = dataslicer

    def get_vector(self):
        if not self.datasource:
            return None
        else:
            data = self.datasource.get_data(self.datapath, self.dataslicer)

        if len(data.shape) > 1:
            return eval('data'+self.dataslicer)
        else:
            return data

    def get_source(self):
        return { "source": self.sourcename,
                 "path": self.datapath,
                 "slicer": self.dataslicer,
                 "operator": self.simpleoperator}

    def getinfo(self):
        x = ["Name: " + str(self.name),
             "Type: " + str(self.nodetype),
             "Data Source: " + str(self.sourcename),
             "Data Path: " + str(self.datapath),
             "Slicer: " + str(self.dataslicer),
             "Operator: " + str(self.simpleoperator)]

        return "\n".join(x)
    
