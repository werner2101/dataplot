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
import xml.dom.minidom

import datatree, plottree, dialogs

import testplugin, gnucapplugin, spiceplugin, touchstoneplugin


class MainWindow(gtk.Window):
    """
    This is the MainWindow of the program
    """
    def __init__(self, args=None):
        """
        Init the base class gtk.Window, all internal data stru
        """
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
        if args:
            self.file_load(args[0])
        else:
            self.new_plot("plot1")
        

        ########## development tests
        #self.test()


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
        self.plugins["spice"] = spiceplugin.SpicePlugin
        self.plugins["touchstone"] = touchstoneplugin.TouchstonePlugin


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

        
    #################### events
    def event_file_new(self, menuitem):
        self.delete_plot(self)
        self.delete_data(self)

        self.filename = None
        self.filenchanged = True

    def event_file_open(self, menuitem):
        dialog = gtk.FileChooserDialog("Load data and plot configuration", parent=self,
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            self.file_load(filename)
        dialog.destroy()

    def event_file_save(self, menuitem):
        if self.filename:
            self.file_save(self.filename)
        else:
            self.event_file_saveas(menuitem)

    def event_file_saveas(self, menuitem):
        dialog = gtk.FileChooserDialog("Save data and plot configuration", parent=self,
                                       action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            self.file_save(filename)
            self.filename = filename

        dialog.destroy()

    def event_file_quit(self, menuitem):
        self.handle_quit()

    def event_data_load(self, menuitem, filetype):
        if filetype == None:
            title = "Load data source"
            print "TODO: load data without plugin"
            return
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
            self.data_load(filename, basename, self.plugins[filetype])

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
        colnames = table.datasource.get_columnnames(table.sourcepath)
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

    def event_delete_plot(self, name):
        self.delete_plot(self.plotnotebook.get_current_page())
        ## recreate one empty plot if we've deleted the last plot
        if self.plotnotebook.get_n_pages() == 0:
            self.new_plot("plot1")
        


    #################### BACKEND functions
    def file_save(self, filename):
        dom = xml.dom.minidom.getDOMImplementation().createDocument(None, "dataplot", None)
        top = dom.documentElement
        sources = dom.createElement("datasources")
        top.appendChild(sources)
        for s in self.datamodel:
            source = dom.createElement("datasource")
            source.setAttribute("name", s[1])
            source.setAttribute("filename", s[2].filename)
            source.setAttribute("plugin", s[2].name)
            sources.appendChild(source)

        plots = dom.createElement("plotdata")
        top.appendChild(plots)
        for plot in self.plotmodel:
            plot_node = dom.createElement("plot")
            plots.appendChild(plot_node)
            plot_node.setAttribute("name", plot[1])

            for subplot in plot.iterchildren():
                subplot_node = dom.createElement("subplot")
                plot_node.appendChild(subplot_node)
                subplot_node.setAttribute("name", subplot[1])
                properties = dom.createElement("properties")
                subplot_node.appendChild(properties)
                for k,v in subplot[2].get_properties().items():
                    v = { None: "", True: "1", False: "0"}.get(v,v)
                    properties.setAttribute(k, str(v))

                for xaxis in subplot.iterchildren():
                    xaxis_node = dom.createElement("xaxis")
                    subplot_node.appendChild(xaxis_node)
                    xaxis_node.setAttribute("name", xaxis[1])
                    xsource_node = dom.createElement("datasource")
                    xaxis_node.appendChild(xsource_node)
                    for k,v in xaxis[2].get_source().items():
                        v = { None: "", True: "1", False: "0"}.get(v,v)
                        xsource_node.setAttribute(k, v)

                    for yaxis in xaxis.iterchildren():
                        yaxis_node = dom.createElement("yaxis")
                        xaxis_node.appendChild(yaxis_node)
                        yaxis_node.setAttribute("name", yaxis[1])
                        ysource_node = dom.createElement("datasource")
                        yaxis_node.appendChild(ysource_node)
                        for k,v in yaxis[2].get_source().items():
                            v = { None: "", True: "1", False: "0"}.get(v,v)
                            ysource_node.setAttribute(k, v)
                        
        open(filename, "w").write(dom.toprettyxml("  "))

    def file_load(self, filename):
        self.delete_plot()
        self.delete_data()
        self.filename = filename
        self.filechanged = False
        source_dict = {}
        
        dom = xml.dom.minidom.parse(filename)
        data = dom.getElementsByTagName("dataplot")[0]
        sources = data.getElementsByTagName("datasources")[0]
        
        for s in sources.getElementsByTagName("datasource"):
            plugin = s.getAttribute("plugin")
            source_filename = s.getAttribute("filename")
            name = s.getAttribute("name")
            source_dict[name] = self.data_load(source_filename, name,
                                               self.plugins[plugin])

        plotdata = data.getElementsByTagName("plotdata")[0]
        for ip, plot in enumerate(plotdata.getElementsByTagName("plot")):
            sp_path = self.new_plot(plot.getAttribute("name"))
            for isp, subplot in enumerate(plot.getElementsByTagName("subplot")):
                for ix, xaxis in enumerate(subplot.getElementsByTagName("xaxis")):
                    xnode = plottree.DataNode(xaxis.getAttribute("name"), "xaxis")
                    xsource = xaxis.getElementsByTagName("datasource")[0]
                    if xsource.getAttribute("source") != "":
                        xnode.set_data(source_dict[xsource.getAttribute("source")],
                                       xsource.getAttribute("source"),
                                       xsource.getAttribute("path").split(" "),
                                       xsource.getAttribute("slicer"))
                    xpath = self.plottree.add_node((ip,isp), xnode)
                    for iy, yaxis in enumerate(xaxis.getElementsByTagName("yaxis")):
                        ynode = plottree.DataNode(yaxis.getAttribute("name"), "yaxis")
                        ysource = yaxis.getElementsByTagName("datasource")[0]
                        ynode.set_data(source_dict[ysource.getAttribute("source")],
                                       ysource.getAttribute("source"),
                                       ysource.getAttribute("path").split(" "),
                                       ysource.getAttribute("slicer"))
                        ypath = self.plottree.add_node((ip,isp,ix), ynode)
                        self.plottree.add_line(ypath)

                properties = subplot.getElementsByTagName("properties")[0]
                self.plotmodel[ip,isp][2].set_properties(dict(properties.attributes.items()))
                self.plotmodel[ip,isp][2].update()
                        

    def new_plot(self, name):
        plot = plottree.PlotNode(name)
        path = self.plottree.add_node(None, plot)
        subplot = plottree.SubplotNode(name, plot.figure)
        path = self.plottree.add_node(path, subplot)
        self.plotnotebook.append_page(plot.plot, gtk.Label(name))
        plot.plot.show()
        self.plotnotebook.set_current_page(-1)
        return path

    def delete_plot(self, nth = None):
        """
        Remove the nth plot from the gui. If the number of the plot is None,
        all plots are removed.
        If there's no plot remaining, create an empty plot.
        """

        if nth:
            deletelist = [ nth ]
        else:
            # create a delete list in reversed order
            deletelist = range(self.plotnotebook.get_n_pages() - 1, -1, -1)
        
        for n in deletelist:
            self.plotnotebook.remove_page(n)
            self.plotmodel.remove(self.plotmodel.get_iter((n,)))


    def delete_data(self, nth = None):
        """
        Remove the nth data source from the gui. If the number of the data source
        is None, all plots are removed.
        """
        if nth:
            deletelist = [ nth ]
        else:
            # create a delete list in reversed order
            deletelist = range(len(self.datamodel) - 1, -1, -1)

        for n in deletelist:
            self.datamodel.remove(self.datamodel.get_iter((n,)))


    def data_load(self, filename, name, plugin):
        mm = self.datamodel
        ii = mm.append(None)
        parent = mm.get_path(ii)
        datasource = plugin(filename)
        mm.set(ii, 0, self.datatree.icons["file"], 1, name, 2, datasource)

        for (path, obj) in datasource.load():
            mm.set(mm.append(mm.get_iter(parent + tuple(path))),
                   0, self.datatree.icons[obj.get_type()],
                   1, obj.get_name(),
                   2, obj)
        return datasource


    def test(self):

        self.infolog.get_buffer().set_text("hello infobox")
        self.errorlog.get_buffer().set_text("hello errorlog")
        self.messagelog.get_buffer().set_text("hello messagelog")

        self.data_load("abc filename", "abc", self.plugins["test"])
        self.data_load("lib/dataplot/plugins/testdata/dc_current_gain_t0.data",
                       "dc_current_gain_t0.data", self.plugins["gnucap"])
        self.data_load("lib/dataplot/plugins/testdata/saturation_voltages_t0.data",
                       "saturation_voltages_t0.data", self.plugins["gnucap"])

        self.new_plot("plot2")
        
    

    
    
