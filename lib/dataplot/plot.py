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
import numpy
import matplotlib.figure
import matplotlib.backends.backend_gtk



class Plot(matplotlib.backends.backend_gtk.FigureCanvasGTK):

    subplots = {}
    subplot = None

    def __init__(self):
        self.figure = matplotlib.figure.Figure()
        matplotlib.backends.backend_gtk.FigureCanvasGTK.__init__(self,self.figure)
        self.subplots[0] = self.figure.add_subplot(111)


    def plot_vector(self, x, y, label=None):
        if x == None:
            self.subplot.plot(y, label=label)
        else:
            self.subplot.plot(x, y, label=label)

    def set_subplot(self, n):
        self.subplot = self.subplots[n]

    def test(self):
        x = numpy.linspace(-10,10,1000)
        p = self.subplots[0]
        p.plot(x, numpy.sin(x), label="sin(x)")

