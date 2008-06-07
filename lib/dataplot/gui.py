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

import plot, datatree, plottree, dataselection


class MainWindow(gtk.Window):

    def __init__(self, args=None):
        gtk.Window.__init__(self)
        self.set_default_size(600,400)

        self.vbox1 = gtk.VBox()
        self.add(self.vbox1)

        self.init_toolbar()

        self.vpan1 = gtk.VPaned()
        self.vpan1.set_position(250)
        self.vbox1.pack_start(self.vpan1)
            
        self.hpan1 = gtk.HPaned()
        self.hpan1.set_position(300)
        self.vpan1.pack1(self.hpan1, True, True)
        self.hpan2 = gtk.HPaned()
        self.hpan2.set_position(150)
        self.hpan1.add(self.hpan2)
            
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hpan2.add1(scrollwin)
        self.datamodel = gtk.TreeStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_OBJECT)
        self.datatree = datatree.DataTree(self.datamodel)
        scrollwin.add_with_viewport(self.datatree)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hpan2.add2(scrollwin)
        self.plotmodel = gtk.TreeStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_OBJECT)
        self.plottree = plottree.PlotTree(self.plotmodel)
        scrollwin.add_with_viewport(self.plottree)

        self.plotnotebook = gtk.Notebook()
        self.hpan1.add(self.plotnotebook)

        self.lognotebook = gtk.Notebook()
        self.vpan1.pack2(self.lognotebook, False, True)

        self.infolog = gtk.TextView()
        self.lognotebook.append_page(self.infolog, gtk.Label("infos"))
        self.messagelog = gtk.TextView()
        self.lognotebook.append_page(self.messagelog, gtk.Label("messages"))
        self.errorlog = gtk.TextView()
        self.lognotebook.append_page(self.errorlog, gtk.Label("errors"))

        self.statusbar = gtk.Statusbar()
        self.vbox1.pack_start(self.statusbar, False)

        ########## subsystem inits
        self.new_plot("plot1")

        #self.menubar =

        ########## signals
        self.connect("delete_event", self.event_delete)
        self.datatree.connect("info-message", self.event_info_message)
        self.datatree.connect("table-activated", self.event_table_activated)
        self.plottree.connect("info-message", self.event_info_message)


        self.test()


    def init_toolbar(self):
        """
        Load all toolbar icons and add them to the main window
        """
        toolbar = gtk.Toolbar()
        self.vbox1.pack_start(toolbar, False, False, 0)

        icon_newplot = gtk.Image()
        icon_newplot.set_from_file('data/bitmaps/menu_newplot.png')
        button_newplot = gtk.ToolButton(icon_newplot, 'New Plot')
        button_newplot.connect('clicked', self.event_new_plot)
        toolbar.add(button_newplot)

        icon_deleteplot = gtk.Image()
        icon_deleteplot.set_from_file('data/bitmaps/menu_deleteplot.png')
        button_deleteplot = gtk.ToolButton(icon_deleteplot, 'Delete Plot')
        button_deleteplot.connect('clicked', self.event_delete_plot)
        toolbar.add(button_deleteplot)

        

    def event_delete(self, window, event):
        self.handle_quit()

    def handle_quit (self):
        ## TODO: save plot project ??
        gtk.main_quit()

    def event_info_message(self, widget, infotext):
        self.infolog.get_buffer().set_text(infotext)

    def event_table_activated(self, widget, table):
        colnames = table.datasource.getcolumnnames(table.sourcepath)
        sourcename = self.datamodel[widget.get_cursor()[0][0:1]][1]
        source = self.datamodel[widget.get_cursor()[0][0:1]][2]
        
        dialog = dataselection.DataSelection(self, colnames)
        retcode = dialog.run()

        if retcode == gtk.RESPONSE_ACCEPT:
            data = dialog.get_content()
    
            nthplot = self.plotnotebook.get_current_page()
            xname = data["x_column"]
            if xname:
                xnode = plottree.DataNode(xname, "xaxis")
                xnode.set_data(source, sourcename, table.sourcepath, xname)
                xpath = self.plottree.add_node((nthplot,0), xnode)
                for yname in data["y_columns"]:
                    ynode = plottree.DataNode(yname, "yaxis")
                    ynode.set_data(source, sourcename, table.sourcepath, yname)
                    self.plottree.add_node(xpath, ynode)

        dialog.destroy()

        self.replot()


    def event_new_plot(self, widget):
        self.new_plot("newplot")

    def new_plot(self, name):
        plot1 = plot.Plot()
        self.plottree.add_plot(name, plot1)
        self.plotnotebook.append_page(plot1, gtk.Label(name))
        plot1.show()
        self.plotnotebook.set_current_page(-1)

    def replot(self):
        nth = self.plotnotebook.get_current_page()
        plotiter = self.plotmodel.get_iter((nth))
        plot = self.plotmodel.get_value(plotiter,2).plot
        plot.set_subplot(0)
        subplotiter = self.plotmodel.get_iter((nth,0))
        for x in xrange(self.plotmodel.iter_n_children(subplotiter)):
            xiter = self.plotmodel.iter_nth_child(subplotiter,x)
            xdata = self.plotmodel.get_value(xiter,2)
            for y in xrange(self.plotmodel.iter_n_children(xiter)):
                yiter = self.plotmodel.iter_nth_child(xiter, y)
                ydata = self.plotmodel.get_value(yiter,2)
                yname = self.plotmodel.get_value(yiter,1)
                plot.plot_vector(xdata.get_vector(), ydata.get_vector(), label= yname)
                

    def event_delete_plot(self, name):
        nth = self.plotnotebook.get_current_page()
        self.plotnotebook.remove_page(nth)
        self.plotmodel.remove(self.plotmodel.get_iter((nth,)))
        if self.plotnotebook.get_n_pages() == 0:
            self.new_plot("plot1")


    def test(self):

        self.infolog.get_buffer().set_text("hello infobox")
        self.errorlog.get_buffer().set_text("hello errorlog")
        self.messagelog.get_buffer().set_text("hello messagelog")

        self.datatree.load_file("abc filename", "abc", "test")
        self.datatree.load_file("lib/dataplot/plugins/testdata/dc_current_gain_t0.data",
                                "dc_current_gain_t0.data", "gnucap")
        self.datatree.load_file("lib/dataplot/plugins/testdata/saturation_voltages_t0.data",
                                "saturation_voltages_t0.data", "gnucap")

        self.new_plot("plot2")
        
    

    
    
