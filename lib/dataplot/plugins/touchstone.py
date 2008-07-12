#!/usr/bin/python

#     Copyright (C) 2008 Werner Hoch
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy

class touchstone():
    """
    class to read touchstone s-parameter files
    The reference for writing this class is the draft of the
    Touchstone(R) File Format Specification Rev 2.0
    http://www.eda-stds.org/ibis/adhoc/interconnect/touchstone_spec2_draft.pdf
    """
    def __init__(self,filename):
        self.sparameters = None
        self.noise = None
        self.filename = filename
        self.version = '1.0'
        self.reference = None

        self.load_file(filename)

    def load_file(self, filename):
        extention = filename.split('.')[-1].lower()
        self.rank = {'s1p':1, 's2p':2, 's3p':3, 's4p':4}.get(extention, None)
        if not self.rank:
            print "filename does not have a s-parameter extention [%s]" %(extention)
            return

        f = open(filename)
        linenr = 0
        values = []
        while (1):
            linenr +=1
            line = f.readline()
            if not line:
                break

            ## remove comment extentions '!'
            ## this may even be the whole line if '!' is the first character
            ## everything is case insensitive in touchstone files
            line = line.split('!',1)[0].strip().lower()
            if len(line) == 0:
                continue

            ## grab the [version] string
            if line[:9] == '[version]':
                self.version = line.split()[1]
                continue

            ## grab the [reference] string
            if line[:11] == '[reference]':
                self.reference = [ float(r) for r in line.split()[2:] ]
                continue

            ## the option line
            if line[0] == '#':
                toks = line[1:].strip().split()
                ## fill the option line with the missing defaults
                toks.extend(['ghz', 's', 'ma', 'r', '50'][len(toks):])
                self.frequency_unit = toks[0]
                self.parameter = toks[1]
                self.format = toks[2]
                self.resistance = toks[4]
                if self.frequency_unit not in ['hz', 'khz', 'mhz', 'ghz']:
                    print 'ERROR: illegal frequency_unit [%s]',  self.frequency_unit
                    ## TODO: Raise
                if self.parameter not in 'syzgh':
                    print 'ERROR: illegal parameter value [%s]', self.parameter
                    ## TODO: Raise
                if self.format not in ['ma', 'db', 'ri']:
                    print 'ERROR: illegal format value [%s]', self.format
                    ## TODO: Raise

                continue

            ## collect all values without taking care of there meaning
            ## we're seperating them later
            values.extend([ float(v) for v in line.split() ])

        ## let's do some postprocessing to the read values
        ## for s2p parameters there may be noise parameters in the value list
        values = numpy.asarray(values)
        if self.rank == 2:
            ## the first frequency value that is smaller than the last one is the
            ## indicator for the start of the noise section
            ## each set of the s-parameter section is 9 values long
            pos = numpy.where(numpy.sign(numpy.diff(values[::9])) == -1)
            if len(pos) != 0:
                ## we have noise data in the values
                pos = pos[0][0] + 1   # add 1 because diff reduced it by 1
                noise_values = values[pos*9:]
                values = values[:pos*9]
                self.noise_values = noise_values.reshape((-1,5))

        ## reshape the values to match the rank
        self.sparameters = values.reshape((-1, 1 + 2*self.rank**2))

        self.frequency_mult = {'hz':1.0, 'khz':1e3,
                               'mhz':1e6, 'ghz':1e9}.get(self.frequency_unit)

    def get_format(self, format="ri"):
        if format == 'orig':
            frequency = self.frequency_unit
            format = self.format
        else:
            frequency = 'hz'
        return "%s %s %s r %s" %(frequency, self.parameter,
                                 format, self.resistance)

    def get_names(self, format="ri"):
        names = ['frequency']
        if format == 'orig':
            format = self.format
        ext1, ext2 = {'ri':('R','I'),'ma':('M','A'), 'db':('DB','A')}.get(format)
        for r1 in xrange(self.rank):
            for r2 in xrange(self.rank):
                names.append("S%i%i%s"%(r1+1,r2+1,ext1))
                names.append("S%i%i%s"%(r1+1,r2+1,ext2))
        return names
    
    def get_sparameter_data(self, format='ri', angle='degree', unwrapped=False):
        """
        get the data of the 
        """
        ret = {}
        ret.append(('frequency', self.sparameters[:,0]))
        for i,n in enumerate(self.get_names(format=format)):
            ret[n] = self.sparameters[:,i]
        return ret

    def get_noise_names(self):
        TBD = 1
        
        
    def get_noise_data(self):
        TBD = 1
"""
                self.noise_frequency = noise_values[:,0]
                self.noise_minimum_figure = noise_values[:,1]
                self.noise_source_reflection = noise_values[:,2]
                self.noise_source_phase = noise_values[:,3]
                self.noise_normalized_resistance = noise_values[:,4]
"""

if __name__ == "__main__":
    import sys
    import pylab
    
    t = touchstone(sys.argv[1])
    d = dict(t.get_data())
    f = d.pop('frequency')
    pylab.subplot(211)
    for s in ['S11_1', 'S12_1', 'S21_1', 'S22_1']:
        pylab.plot(f, d[s], label=s)
    pylab.legend(loc='best')
    pylab.grid()
    pylab.subplot(212)
    for s in ['S11_2', 'S12_2', 'S21_2', 'S22_2']:
        pylab.plot(f, d[s], label=s)
    pylab.legend(loc='best')
    pylab.grid()
    pylab.show()

    
            
            
    

        
