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
    
    def __init__(self):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), pixbuf=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1)
        self.append_column(column)
        self.set_property("enable-tree-lines", True)
        self.set_property("headers-visible", False)

        self.load_icons()
        self.create_model()
        self.test()

    def load_icons(self):
        self.icons = {}
        for name,filename in bitmaps:
            self.icons[name] = gtk.gdk.pixbuf_new_from_file(filename)

    def create_model(self):
        model = gtk.TreeStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        self.set_model(model)

    def test(self):
        mm = self.get_model()
        ip = mm.append(None)
        mm.set(ip, 0, self.icons["notebook"], 1, "plot1")

        ip = mm.append(None)
        mm.set(ip, 0, self.icons["notebook"], 1, "plot2")
        
        isp = mm.append(ip)
        mm.set(isp, 0, self.icons["singleplot"], 1, "singleplot")
        
        ix = mm.append(isp)
        mm.set(ix, 0, self.icons["xaxis"], 1, "X-Data1")
        
        iy = mm.append(ix)
        mm.set(iy, 0, self.icons["yaxis"], 1, "Y-Data1")
        iy = mm.append(ix)
        mm.set(iy, 0, self.icons["yaxis"], 1, "Y-Data2")

        ix = mm.append(isp)
        mm.set(ix, 0, self.icons["xaxis"], 1, "X-Data2")
        
        iy = mm.append(ix)
        mm.set(iy, 0, self.icons["yaxis"], 1, "Y-Data1")
        iy = mm.append(ix)
        mm.set(iy, 0, self.icons["math"], 1, "Math-Block")

        





