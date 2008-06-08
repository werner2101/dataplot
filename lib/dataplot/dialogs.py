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


class singleplot_options(gtk.Dialog):

    returns = {}

    def __init__(self, parent, properties):
        gtk.Dialog.__init__(self, "Subplot Options", parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.create_dialog(properties)

        self.show_all()

    def create_dialog(self, prop):

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
        
