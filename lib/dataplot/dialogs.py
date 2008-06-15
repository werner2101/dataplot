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

import gtk, gobject


class TableDataSelection(gtk.Dialog):

    returns = {}

    def __init__(self, parent, columnnames):
        gtk.Dialog.__init__(self, "Row Selection", parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwin.set_size_request(-1, 200)
        
        self.listview = gtk.TreeView()
        x_cell = gtk.CellRendererToggle()
        x_cell.set_property("radio", True)
        x_cell.set_property("activatable", True)
        x_cell.connect('toggled', self.x_toggle, self.listview)
                      
        y_cell = gtk.CellRendererToggle()
        y_cell.set_property("activatable", True)
        y_cell.connect('toggled', self.y_toggle, self.listview)

        self.listview.append_column(gtk.TreeViewColumn("X", x_cell , active=0))
        self.listview.append_column(gtk.TreeViewColumn("Y", y_cell , active=1))
        self.listview.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=2))

        liststore = gtk.ListStore( gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, str)
        for name in columnnames:
            liststore.append([False, False, name])
        self.listview.set_model(liststore)
        
        scrollwin.add_with_viewport(self.listview)
        self.vbox.add(scrollwin)
        self.show_all()
        

    def get_content(self):
        x,y = None, []
        for row in self.listview.get_model():
            if row[0] == True:
                x = row[2]
            if row[1] == True:
                y.append(row[2])
        return {"x_column": x,
                "y_columns": y}
            
        
    def x_toggle(self, cell, path, listview):
        """
        Callback when the toggle buttons of the X-row is toggled.
        Only allow one x-value to be selected from the x-row
        """
        mm = listview.get_model()
        newstate = not mm[path][0]
        for row in mm:
            row[0] = False
        mm[path][0] = newstate
        
    
    def y_toggle(self, cell, path, listview):
        mm = listview.get_model()
        mm[path][1] = not mm[path][1]


class ArrayDataSelection(gtk.Dialog):

    returns = {}

    def __init__(self, parent, shape):
        gtk.Dialog.__init__(self, "Array Selection", parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.shape = shape
        self.sel_ranks = []

        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, True)
        for rank in xrange(len(self.shape)):
            hbox.pack_start(gtk.Label("D%i: " % rank), False, False)

            liststore = gtk.ListStore(gobject.TYPE_STRING)
            sel = [ '%i'%i for i in xrange(self.shape[rank]) ]
            for n in ['Var', 'Sel'] + sel:
                liststore.append((n,))

            combo = gtk.ComboBox(liststore)
            cell = gtk.CellRendererText()
            combo.pack_start(cell, True)
            combo.add_attribute(cell, 'text', 0)
            if rank == list(self.shape).index(max(self.shape)):
                combo.set_active(0)
            else:
                combo.set_active(1)
            self.sel_ranks.append(combo)
            hbox.pack_start(combo, False, False)
            combo.connect("changed", self.event_selection_changed)


        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwin.set_size_request(-1, 200)

        self.listview = gtk.TreeView()
        x_cell = gtk.CellRendererToggle()
        x_cell.set_property("radio", True)
        x_cell.set_property("activatable", True)
        x_cell.connect('toggled', self.x_toggle, self.listview)
                      
        y_cell = gtk.CellRendererToggle()
        y_cell.set_property("activatable", True)
        y_cell.connect('toggled', self.y_toggle, self.listview)

        self.listview.append_column(gtk.TreeViewColumn("X", x_cell , active=0))
        self.listview.append_column(gtk.TreeViewColumn("Y", y_cell , active=1))
        self.listview.append_column(gtk.TreeViewColumn("Slice", gtk.CellRendererText(), text=2))

        scrollwin.add_with_viewport(self.listview)
        self.vbox.add(scrollwin)

        self.fill_model()
        self.show_all()

    def fill_model(self):
        liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, str)
        groups = []
        for rank, combo in enumerate(self.sel_ranks):
            content = combo.get_model()[combo.get_active()][0]
            if content == "Var":
                groups.append([':'])
            elif content == "Sel":
                l = [ '%i'%i for i in xrange(self.shape[rank]) ]
                groups.append(l)
            else:
                groups.append([content])

        sel = [""]
        for g in groups:
            sel_new = []
            for s in sel:
                sel_new.extend([ s + gm + ','  for gm in g ])
            sel = sel_new
        
        for s in sel:
            liststore.append([False, False, '[' + s[:-1] + ']'])
        self.listview.set_model(liststore)


    def get_content(self):
        x,y = None, []
        for row in self.listview.get_model():
            if row[0] == True:
                x = row[2]
            if row[1] == True:
                y.append(row[2])
        return {"x_column": x,
                "y_columns": y}
            
    def event_selection_changed(self, combo):
        self.fill_model()
        
    def x_toggle(self, cell, path, listview):
        """
        Callback when the toggle buttons of the X-row is toggled.
        Only allow one x-value to be selected from the x-row
        """
        mm = listview.get_model()
        newstate = not mm[path][0]
        for row in mm:
            row[0] = False
        mm[path][0] = newstate
        
    
    def y_toggle(self, cell, path, listview):
        mm = listview.get_model()
        mm[path][1] = not mm[path][1]



class SingleplotOptions(gtk.Dialog):

    returns = {}

    def __init__(self, parent, properties):
        gtk.Dialog.__init__(self, "Subplot Options", parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.create_dialog(properties)

        self.show_all()

    def create_dialog(self, prop):

        ## Grid, legend and x/y settings
        label = gtk.Label()
        label.set_markup("<b>Misc Settings</b>")
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_use_markup(True)
        self.vbox.pack_start(label, False, True)

        align = gtk.Alignment()
        align.set_padding(0, 0, 10, 0)
        self.vbox.add(align)

        avbox = gtk.VBox()
        align.add(avbox)

        table = gtk.Table(3, 2)
        avbox.add(table)

        table.attach(gtk.Label("title: "), 0, 1, 0, 1)
        self.title_entry = gtk.Entry()
        self.title_entry.set_text(prop.get("title",""))
        table.attach(self.title_entry, 1, 2, 0, 1)
        table.attach(gtk.Label("x-label: "), 0, 1, 1, 2)
        self.xlabel_entry = gtk.Entry()
        self.xlabel_entry.set_text(prop.get("xlabel",""))
        table.attach(self.xlabel_entry, 1, 2, 1, 2)
        table.attach(gtk.Label("y-label: "), 0, 1, 2, 3)
        self.ylabel_entry = gtk.Entry()
        self.ylabel_entry.set_text(prop.get("ylabel",""))
        table.attach(self.ylabel_entry, 1, 2, 2, 3)

        self.grid_check = gtk.CheckButton("Enable Grid")
        self.grid_check.set_active(prop.get("grid", True))
        avbox.add(self.grid_check)

        self.legend_check = gtk.CheckButton("Enable Legend")
        self.legend_check.set_active(prop.get("legend", True))
        avbox.add(self.legend_check)

        hbox = gtk.HBox()
        avbox.add(hbox)
        self.xlog_check = gtk.CheckButton("Logarithmic x-axis")
        self.xlog_check.set_active(prop.get("xlog", False))
        hbox.add(self.xlog_check)
        self.ylog_check = gtk.CheckButton("Logarithmic y-axis")
        self.ylog_check.set_active(prop.get("ylog", False))
        hbox.add(self.ylog_check)

        ## Axis Settings
        label = gtk.Label()
        label.set_markup("<b>Axis Ranges:</b>")
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_use_markup(True)
        self.vbox.pack_start(label, False, True)

        align = gtk.Alignment()
        align.set_padding(0, 0, 10, 0)
        self.vbox.add(align)

        table = gtk.Table(2, 6)
        align.add(table)
                
        self.xmin_check = gtk.CheckButton()
        self.xmin_check.set_active(True)
        self.xmax_check = gtk.CheckButton()
        self.xmax_check.set_active(True)
        self.xmin_entry = gtk.Entry()
        self.xmin_entry.set_text(str(prop.get("xmin", 0.0)))
        self.xmin_entry.set_width_chars(10)
        self.xmax_entry = gtk.Entry()
        self.xmax_entry.set_text(str(prop.get("xmax", 0.0)))
        self.xmax_entry.set_width_chars(10)

        self.ymin_check = gtk.CheckButton()
        self.ymin_check.set_active(True)
        self.ymax_check = gtk.CheckButton()
        self.ymax_check.set_active(True)
        self.ymin_entry = gtk.Entry()
        self.ymin_entry.set_text(str(prop.get("ymin", 0.0)))
        self.ymin_entry.set_width_chars(10)
        self.ymax_entry = gtk.Entry()
        self.ymax_entry.set_text(str(prop.get("ymax", 0.0)))
        self.ymax_entry.set_width_chars(10)


        self.xmin_check.connect('toggled', self.event_range_toggle, self.xmin_entry)
        self.xmax_check.connect('toggled', self.event_range_toggle, self.xmax_entry)
        self.ymin_check.connect('toggled', self.event_range_toggle, self.ymin_entry)
        self.ymax_check.connect('toggled', self.event_range_toggle, self.ymax_entry)
        

        table.attach(self.xmin_check, 0, 1, 0, 1)
        table.attach(gtk.Label("xmin="), 1, 2, 0, 1)
        table.attach(self.xmin_entry, 2, 3, 0, 1)
        table.attach(self.xmax_check, 3, 4, 0, 1)
        table.attach(gtk.Label("xmax="), 4, 5, 0, 1)
        table.attach(self.xmax_entry, 5, 6, 0, 1)

        table.attach(self.ymin_check, 0, 1, 1, 2)
        table.attach(gtk.Label("ymin="), 1, 2, 1, 2)
        table.attach(self.ymin_entry, 2, 3, 1, 2)
        table.attach(self.ymax_check, 3, 4, 1, 2)
        table.attach(gtk.Label("ymax="), 4, 5, 1, 2)
        table.attach(self.ymax_entry, 5, 6, 1, 2)


    def event_range_toggle(self, widget, entry):
        entry.set_sensitive(widget.get_active())

    def get_content(self):

        prop = {"xmin": None,
                "xmax": None,
                "ymin": None,
                "ymax": None}

        prop["grid"] = self.grid_check.get_active()
        prop["legend"] = self.legend_check.get_active()
        prop["xlog"] = self.xlog_check.get_active()
        prop["ylog"] = self.ylog_check.get_active()
        
        prop["title"] = self.title_entry.get_text()
        prop["xlabel"] = self.xlabel_entry.get_text()
        prop["ylabel"] = self.ylabel_entry.get_text()
        
        if (self.xmin_check.get_active()):
            prop["xmin"] = float(self.xmin_entry.get_text())
        if (self.xmax_check.get_active()):
            prop["xmax"] = float(self.xmax_entry.get_text())
        if (self.ymin_check.get_active()):
            prop["ymin"] = float(self.ymin_entry.get_text())
        if (self.ymax_check.get_active()):
            prop["ymax"] = float(self.ymax_entry.get_text())

        return prop
            
        
    def x_toggle(self, cell, path, listview):
        """
        Callback when the toggle buttons of the X-row is toggled.
        Only allow one x-value to be selected from the x-row
        """
        mm = listview.get_model()
        newstate = not mm[path][0]
        for row in mm:
            row[0] = False
        mm[path][0] = newstate
        
    
    def y_toggle(self, cell, path, listview):
        mm = listview.get_model()
        mm[path][1] = not mm[path][1]
        
