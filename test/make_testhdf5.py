#!/usr/bin/python
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

import numpy
import tables



#################### MAIN

f = tables.openFile("data/testdata.hdf5","w")

f.createGroup('/', 'sin_cos')

# create some arrays with different sizes
# this is used to do some performance tests
for n in [100,1000,10000,100000,1000000]:
    x = numpy.linspace(-10,10,n)
    y_sin1 = numpy.sin(x)
    y_sin2 = 0.9*numpy.sin(2*x)
    y_cos1 = 1.1*numpy.sin(3.5*x)
    y_cos2 = 1*numpy.sin(5*x)
    a = numpy.vstack([x, y_sin1, y_sin2, y_cos1, y_cos2])

    f.createArray('/sin_cos',"N%i"%n, a)

# create some complex datasets
# this will be used to test operators for complex data like abs, real, imag, ..
f.createGroup('/', 'complex')
x = numpy.linspace(-10,10,1000)
y_sin1 = numpy.sin(x)
y_sin2 = 0.9*numpy.sin(2*x)
y_cos1 = 1.1*numpy.sin(3.5*x)
y_cos2 = 1*numpy.sin(5*x)
a = numpy.vstack([x, 1j*y_sin1 + y_cos1, 1j*y_sin2 + y_cos2])
f.createArray('/complex', 'sin', a)

# create data that is only positive or negativ
f.createGroup('/', 'quadrant')
y_sin1 = numpy.sin(x) + 2
y_cos1 = numpy.cos(x) + 2
y_sin2 = numpy.sin(x) - 2
y_cos2 = numpy.cos(x) - 2
a = numpy.vstack([x, y_sin1, y_sin2, y_cos1, y_cos2])
f.createArray('/quadrant', 'sin_cos', a)


f.close()
