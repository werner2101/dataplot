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


import gtk

import plot, datatree, plottree

class MainWindow(gtk.Window):

    def __init__(self, args=None):
        gtk.Window.__init__(self)
        self.set_default_size(600,400)

        self.vbox1 = gtk.VBox()
        self.add(self.vbox1)

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
        self.datatree = datatree.DataTree()
        scrollwin.add_with_viewport(self.datatree)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hpan2.add2(scrollwin)
        self.plottree = plottree.PlotTree()
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



        #self.menubar =
        #self.iconbar = 

        ########## signals
        self.connect("delete_event", self.event_delete)


        self.test()

    def event_delete(self, window, event):
        self.handle_quit()

    def handle_quit (self):
        ## TODO: save plot project ??
        gtk.main_quit()

    def test(self):

        self.infolog.get_buffer().set_text("hello infobox")
        self.errorlog.get_buffer().set_text("hello errorlog")
        self.messagelog.get_buffer().set_text("hello messagelog")

        self.plot1 = plot.Plot()
        self.plotnotebook.append_page(self.plot1, gtk.Label("plot1"))
        self.plot2 = plot.Plot()
        self.plotnotebook.append_page(self.plot2, gtk.Label("plot2"))
        



