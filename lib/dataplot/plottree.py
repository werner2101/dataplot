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
import matplotlib.backends.backend_gtkagg


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
        self.current_plot = 0
        self.current_subplot = 0
        self.current_xdata = 0
        self.current_ydata = 0

        self.icons = {}
        for name,filename in bitmaps:
            self.icons[name] = gtk.gdk.pixbuf_new_from_file(filename)

    def add_plot(self, plotobject):
        path = self.add_node(None, plotobject)
        self.current_plot = path[0]

    def add_subplot(self, subplotobject):
        path = self.add_node((self.current_plot,), subplotobject)
        self.current_subplot = path[1]

    def add_xdata(self, xdataobject):
        path = self.add_node((self.current_plot, self.current_subplot),
                             xdataobject)
        self.current_xdata = path[2]

    def add_ydata(self, ydataobject):
        path = self.add_node((self.current_plot, self.current_subplot,
                              self.current_xdata), ydataobject)
        self.current_ydata = path[3]
        self.add_line()

    def add_node(self, parentpath, nodeobject):
        if not parentpath:
            i_new = self.append(None)
        else:
            i = self.get_iter(parentpath)
            i_new = self.append(i)
        self.set(i_new, 0, self.icons[nodeobject.nodetype],
                 1, nodeobject.name, 2, nodeobject)
        return self.get_path(i_new)

    def add_line(self):
        ypath = (self.current_plot, self.current_subplot,
                 self.current_xdata, self.current_ydata)
        ynode = self.get_value(self.get_iter(ypath), 2)
        xnode = self.get_value(self.get_iter(ypath[0:3]),2)
        subplotnode = self.get_value(self.get_iter(ypath[0:2]),2)

        yv = ynode.get_vector()
        xv = xnode.get_vector()
        if xv == None:
            xv = numpy.arange(len(yv))

        axes = subplotnode.axes
        ynode.line = axes.plot(xv, yv, label=ynode.name)

    def set_subplot_properties(self, properties):
        subplotnode = self[self.current_plot, self.current_subplot][2]
        subplotnode.set_properties(properties)

    def update_subplot(self):
        subplotnode = self[self.current_plot, self.current_subplot][2]
        subplotnode.update()

class PlotNode(gobject.GObject):

    nodetype = "notebook"

    def __init__(self, name):
        gobject.GObject.__init__(self)
        self.name = name
        self.figure = matplotlib.figure.Figure()
        self.plot = matplotlib.backends.backend_gtkagg.FigureCanvasGTKAgg(self.figure)

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
        """
        callback for the mouse scroll event
        """
        ## get the coordinate of the data where the mouse points to.
        ## the origin for the point (event.x, event.y) is top left.
        ## matplotlib refers expects the origin at bottom left. The event.y must be inverted
        width, height = self.figure.canvas.get_width_height()
        ## get the data location
        xdata, ydata = self.axes.transData.inverted().transform_point((event.x, height - event.y))
        [xmin, xmax, ymin, ymax] = self.axes.axis()

        if event.state & gtk.gdk.CONTROL_MASK:
            if event.state & gtk.gdk.SHIFT_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                    ymin, ymax = self.zoom(ymin, ydata, ymax, "out",
                                            self.properties['ylog'] == '1')
                else:
                    ymin, ymax = self.zoom(ymin, ydata, ymax, "in",
                                            self.properties['ylog'] == '1')
                self.axes.axis(ymin=ymin, ymax=ymax)
            else:
                if event.direction == gtk.gdk.SCROLL_UP:
                    xmin, xmax = self.zoom(xmin, xdata, xmax, "out",
                                            self.properties['xlog'] == '1')
                else:
                    xmin, xmax = self.zoom(xmin, xdata, xmax, "in",
                                            self.properties['xlog'] == '1')
                self.axes.axis(xmin=xmin, xmax=xmax)
        else:
            if event.state & gtk.gdk.SHIFT_MASK:
                if event.direction == gtk.gdk.SCROLL_UP:
                    # pan up
                    ymin, ymax = self.pan(ymin, ymax, "up",
                                          self.properties['ylog'] == '1')
                else:
                    # pan down
                    ymin, ymax = self.pan(ymin, ymax, "down",
                                          self.properties['ylog'] == '1')
                self.axes.axis(ymin=ymin, ymax=ymax)
            else: 
                if event.direction == gtk.gdk.SCROLL_UP:
                    # pan right
                    xmin, xmax = self.pan(xmin, xmax, "up",
                                          self.properties['xlog'] == '1')
                else:
                    # pan left
                    xmin, xmax = self.pan(xmin, xmax, "down",
                                          self.properties['xlog'] == '1')
                self.axes.axis(xmin=xmin, xmax=xmax)

        self.figure.canvas.draw()

    def zoom(self, smin, scur, smax, direction="in", logscale=False):
        if direction == "out":
            factor = 1.2
        else:
            factor = 1/1.2

        if logscale:
            smin = math.log10(smin)
            scur = math.log10(scur)
            smax = math.log10(smax)

        smin = scur - (scur - smin)* factor
        smax = scur + (smax - scur)* factor

        if logscale:
            smin = 10**smin
            smax = 10**smax

        return smin, smax

    def pan (self, smin, smax, direction="down", logscale=False):
        factor = 0.2
        if direction == "down":
            d = -1
        else:
            d = 1

        if logscale:
            smin = math.log10(smin)
            smax = math.log10(smax)

        delta = d * (smax - smin) * factor
        smin = smin + delta
        smax = smax + delta

        if logscale:
            smin = 10**smin
            smax = 10**smax

        return smin, smax

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
        self.figure.canvas.draw()

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
        if (self.properties["xmin"]) != "":
            self.properties["xmin"] = str(xmin).replace(',','.')
        if (self.properties["xmax"]) != "":
            self.properties["xmax"] = str(xmax).replace(',','.')
        if (self.properties["ymin"]) != "":
            self.properties["ymin"] = str(ymin).replace(',','.')
        if (self.properties["ymax"]) != "":
            self.properties["ymax"] = str(ymax).replace(',','.')
        return self.properties
        


class DataNode(gobject.GObject):

    def __init__(self, name, nodetype):
        gobject.GObject.__init__(self)
        self.name = name
        self.nodetype = nodetype
        self.datasource = ""
        self.sourcename = ""
        self.datapath = ""
        self.dataslicer = ""
        self.simpleoperator = ""

    def set_data(self, datasource, sourcename, datapath, dataslicer=None):
        self.datasource = datasource
        self.sourcename = sourcename
        self.datapath = datapath
        self.dataslicer = dataslicer

    def get_vector(self):
        if self.datasource == "":
            return None
        else:
            data = self.datasource.get_data(self.datapath, self.dataslicer)

        # maybe move that code should be move to the datasource plugins
        if len(data.shape) > 1:
            data = self.datasource.get_slice(data, self.dataslicer)

        return data

    def get_source(self):
        return { "source": self.sourcename,
                 "path": self.datapath,
                 "slicer": self.dataslicer,
                 "operator": self.simpleoperator}

    def getinfo(self):
        x = ["Name: " + self.name,
             "Type: " + self.nodetype,
             "Data Source: " + self.sourcename,
             "Data Path: " + self.datapath,
             "Slicer: " + self.dataslicer,
             "Operator: " + self.simpleoperator]

        return "\n".join(x)
    
