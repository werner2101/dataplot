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

import os.path

import gtk, gobject, gtk.gdk

import datatree, plottree, dialogs

import testplugin, gnucapplugin

class MainWindow(gtk.Window):

    def __init__(self, args=None):
        gtk.Window.__init__(self)

        self.init_data()
        self.init_plugins()
        self.init_gui()
        
        ########## signals
        self.connect("delete_event", self.event_delete)
        self.plotnotebook.connect("switch-page", self.event_notebook_changed)
        self.datatree.connect("info-message", self.event_info_message)
        self.datatree.connect("table-activated", self.event_table_activated)
        self.datatree.connect("array-activated", self.event_array_activated)
        self.plottree.connect("plotnode-activated", self.event_plotnode_acitvated)
        self.plottree.connect("info-message", self.event_info_message)

        ########## subsystem inits / handle cli args
        self.new_plot("plot1")

        ########## development tests
        self.test()


    def init_data(self):
        self.filename = None
        self.filechanged = False

        self.datamodel = gtk.TreeStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_OBJECT)

        self.plotmodel = gtk.TreeStore(gtk.gdk.Pixbuf,
                                       gobject.TYPE_STRING,
                                       gobject.TYPE_OBJECT)

    def init_plugins(self):
        self.plugins = {}
        self.plugins["test"] = testplugin.TestPlugin
        self.plugins["gnucap"] = gnucapplugin.GnucapPlugin


    def init_gui(self):
        self.set_default_size(800,600)

        self.vbox1 = gtk.VBox()
        self.add(self.vbox1)

        self.accel_group = gtk.AccelGroup()
        self.init_menubar()
        self.init_toolbar()
        self.add_accel_group(self.accel_group)

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
        self.datatree = datatree.DataTree(self.datamodel)
        scrollwin.add_with_viewport(self.datatree)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hpan2.add2(scrollwin)
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
        

    def init_menubar(self):
        """
        create a menubar with menu items
        """

        menubar = gtk.MenuBar()
        self.vbox1.pack_start(menubar, False, False, 0)
        
        menu_file = gtk.Menu()
        menu_data = gtk.Menu()
        menu_plot = gtk.Menu()
        menu_help = gtk.Menu()
        
        menuitem_file = gtk.MenuItem('_File')
        menuitem_file.set_submenu(menu_file)
        menuitem_data = gtk.MenuItem('_Data')
        menuitem_data.set_submenu(menu_data)
        menuitem_plot = gtk.MenuItem('_Plot')
        menuitem_plot.set_submenu(menu_plot)
        menuitem_help = gtk.MenuItem('_Help')
        menuitem_help.set_submenu(menu_help)

        ## File menu entries
        menuitem_file_new = gtk.ImageMenuItem(gtk.STOCK_NEW, self.accel_group)
        menuitem_file_new.connect('activate', self.event_file_new)
        menu_file.append(menuitem_file_new)
        
        menuitem_file_open = gtk.ImageMenuItem(gtk.STOCK_OPEN, self.accel_group)
        menuitem_file_open.connect('activate', self.event_file_open)
        menu_file.append(menuitem_file_open)
        
        menuitem_file_save = gtk.ImageMenuItem(gtk.STOCK_SAVE, self.accel_group)
        menuitem_file_save.connect('activate', self.event_file_save)
        menu_file.append(menuitem_file_save)
                         
        menuitem_file_saveas = gtk.ImageMenuItem(gtk.STOCK_SAVE_AS, self.accel_group)
        menuitem_file_saveas.connect('activate', self.event_file_saveas)
        menu_file.append(menuitem_file_saveas)

        sep = gtk.SeparatorMenuItem()
        sep.set_sensitive(False)
        menu_file.append(sep)
        
        menuitem_file_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT, self.accel_group)
        menuitem_file_quit.connect('activate', self.event_file_quit)
        menu_file.append(menuitem_file_quit)

        menubar.append(menuitem_file)

        ## Data menu entries
        menuitem_data_load = gtk.MenuItem('Load source')
        menuitem_data_load.connect('activate', self.event_data_load, None)
        menu_data.append(menuitem_data_load)

        sep = gtk.SeparatorMenuItem()
        sep.set_sensitive(False)
        menu_data.append(sep)

        for k in self.plugins.keys():
            ## load a file with a user defined plugin
            ## this is required if the file type can't be guessed from the filename
            menuitem_data_load = gtk.MenuItem('Load ' + k + ' file')
            menuitem_data_load.connect('activate', self.event_data_load, k)
            menu_data.append(menuitem_data_load)

        menubar.append(menuitem_data)

        ## Plot menu entries
        menubar.append(menuitem_plot)

        ## Help menu entries
        menubar.append(menuitem_help)
        
        

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

        
    def event_file_new(self, menuitem):
        self.delete_plot(self)
        self.delete_data(self)

        self.filename = None
        self.filenamechanged = True

    def event_file_open(self, menuitem):
        print "event_file_open not implemented yet"

    def event_file_save(self, menuitem):
        print "event_file_save not implemented yet"

    def event_file_saveas(self, menuitem):
        print "event_file_saveas not implemented yet"

    def event_file_quit(self, menuitem):
        self.handle_quit()

    def event_data_load(self, menuitem, filetype):
        if filetype == None:
            title = "Load data source"
            print "TODO: load data without plugin"
        else:
            title = "Load " + filetype + " data source"
        dialog = gtk.FileChooserDialog(title, parent=self,
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            basename = os.path.basename(filename)
            # TODO: guess plugin if filetype is None
            # TODO: what shall we do with duplicate source names
            self.load_file(filename, basename, self.plugins[filetype])

        dialog.destroy()

    def event_delete(self, window, event):
        self.handle_quit()

    def handle_quit(self):
        ## TODO: save plot project ??
        gtk.main_quit()

    def event_info_message(self, widget, infotext):
        self.infolog.get_buffer().set_text(infotext)

    def event_notebook_changed(self, notebook, page, page_num):
        self.plottree.collapse_all()
        self.plottree.expand_row((page_num,), True)

    def event_table_activated(self, widget, table):
        colnames = table.datasource.getcolumnnames(table.sourcepath)
        sourcename = self.datamodel[widget.get_cursor()[0][0:1]][1]
        source = self.datamodel[widget.get_cursor()[0][0:1]][2]
        
        dialog = dialogs.TableDataSelection(self, colnames)
        retcode = dialog.run()

        if retcode == gtk.RESPONSE_ACCEPT:
            data = dialog.get_content()
    
            nthplot = self.plotnotebook.get_current_page()
            xname = data["x_column"]
            if xname:
                xnode = plottree.DataNode(xname, "xaxis")
                xnode.set_data(source, sourcename, table.sourcepath, xname)
            else:
                xnode = plottree.DataNode('generic', "xaxis")
            xpath = self.plottree.add_node((nthplot,0), xnode)

            for yname in data["y_columns"]:
                ynode = plottree.DataNode(yname, "yaxis")
                ynode.set_data(source, sourcename, table.sourcepath, yname)
                ypath = self.plottree.add_node(xpath, ynode)
                self.plottree.add_line(ypath)

            self.plottree.expand_row((nthplot,), True)
            self.plotmodel.get_value(self.plotmodel.get_iter((nthplot,0)),2).update()
        dialog.destroy()

    def event_array_activated(self, widget, arraynode):
        shape = arraynode.datasource.get_shape(arraynode.sourcepath)
        sourcename = self.datamodel[widget.get_cursor()[0][0:1]][1]
        source = self.datamodel[widget.get_cursor()[0][0:1]][2]

        dialog = dialogs.ArrayDataSelection(self, shape)
        retcode = dialog.run()

        if retcode == gtk.RESPONSE_ACCEPT:
            data = dialog.get_content()
            nthplot = self.plotnotebook.get_current_page()
            xname = data["x_column"]
            if xname:
                xnode = plottree.DataNode(xname, "xaxis")
                xnode.set_data(source, sourcename, arraynode.sourcepath, xname)
            else:
                xnode = plottree.DataNode('generic', "xaxis")
            xpath = self.plottree.add_node((nthplot,0), xnode)

            for yname in data["y_columns"]:
                ynode = plottree.DataNode(arraynode.name + yname, "yaxis")
                ynode.set_data(source, sourcename, arraynode.sourcepath, yname)
                ypath = self.plottree.add_node(xpath, ynode)
                self.plottree.add_line(ypath)

            self.plottree.expand_row((nthplot,), True)
            self.plotmodel.get_value(self.plotmodel.get_iter((nthplot,0)),2).update()

        dialog.destroy()
        

    def event_plotnode_acitvated(self, widget, node):
        if node.nodetype == "notebook":
            print "TODO: row activation for notebook"
        elif node.nodetype == "singleplot":
            dialog = dialogs.SingleplotOptions(self, node.get_properties())
            ret = dialog.run()
            if ret == gtk.RESPONSE_ACCEPT:
                node.set_properties(dialog.get_content())
            dialog.destroy()
                
        elif node.nodetype == "yaxis":
            print "TOD0: row activation for yaxis"
        elif node.nodetype == "xaxis":
            print "TOD0: row activation for xaxis"
        else:
            print "UPS: unknown node type in plottree"


    def event_new_plot(self, widget):
        self.new_plot("newplot")

    def new_plot(self, name):
        plot = plottree.PlotNode(name)
        path = self.plottree.add_node(None, plot)
        subplot = plottree.SubplotNode(name, plot.figure)
        path = self.plottree.add_node(path, subplot)
        self.plotnotebook.append_page(plot.plot, gtk.Label(name))
        plot.plot.show()
        self.plotnotebook.set_current_page(-1)

    def delete_plot(self, nth = None):
        """
        Remove the nth plot from the gui. If the number of the plot is None,
        all plots are removed.
        If there's no plot remaining, create an empty plot.
        """

        if not nth:
            deletelist = [ nth ]
        else:
            # create a delete list in reversed order
            deletelist = range(self.plotnotebook.get_n_pages() - 1, -1, -1)
        
        for n in deletelist:
            self.plotnotebook.remove_page(n)
            self.plotmodel.remove(self.plotmodel.get_iter((n,)))
            
        if self.plotnotebook.get_n_pages() == 0:
            self.new_plot("plot1")

    def delete_data(self, nth = None):
        """
        Remove the nth data source from the gui. If the number of the data source
        is None, all plots are removed.
        """
        if not nth:
            deletelist = [ nth ]
        else:
            # create a delete list in reversed order
            deletelist = range(len(self.datamodel) - 1, -1, -1)

        for n in deletelist:
            self.datamodel.remove(self.datamodel.get_iter((n,)))


    def load_file(self, filename, name, plugin):
        mm = self.datamodel
        ii = mm.append(None)
        parent = mm.get_path(ii)
        datasource = plugin(filename)
        mm.set(ii, 0, self.datatree.icons["file"], 1, name, 2, datasource)

        for (path, obj) in datasource.load():
            mm.set(mm.append(mm.get_iter(parent + tuple(path))),
                   0, self.datatree.icons[obj.gettype()],
                   1, obj.getname(),
                   2, obj)

    def event_delete_plot(self, name):
        delete_plot(self.plotnotebook.get_current_page())


    def test(self):

        self.infolog.get_buffer().set_text("hello infobox")
        self.errorlog.get_buffer().set_text("hello errorlog")
        self.messagelog.get_buffer().set_text("hello messagelog")

        self.load_file("abc filename", "abc", self.plugins["test"])
        self.load_file("lib/dataplot/plugins/testdata/dc_current_gain_t0.data",
                       "dc_current_gain_t0.data", self.plugins["gnucap"])
        self.load_file("lib/dataplot/plugins/testdata/saturation_voltages_t0.data",
                       "saturation_voltages_t0.data", self.plugins["gnucap"])

        self.new_plot("plot2")
        
    

    
    
