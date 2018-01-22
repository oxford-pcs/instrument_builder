import json

import numpy as np
import pylab as plt

class slit():
  def __init__(self, path, name):
    self.cfg = self._getSlitPatternFromFile(path, name)
    
  def _getSlitPatternFromFile(self, path, name):
      '''
        Return slit with name [name] from a JSON file at path [path].
      '''
      with open(path) as fp:
        cfg = json.load(fp)
        
      slit = None
      for c in cfg:
        if c['name'] == name:
          slit = c
          break;
        else:
          continue
      try:
        assert slit is not None
      except AssertionError:
        print "slit config not found"
      
      return slit   
    
  def getFieldsFromSlitPattern(self, nfields, verbose=True, debug=False):
    '''
      Takes the slit pattern and number of fields [nfields] and returns a list 
      of corresponding field points at the entrance slit.
      
      How [nfields] is interpreted depends on the pattern type:
      
        - "brick_wall"  divides the number of fields by the number of slitlets, 
                        creating this many fields per slitlet. Fields will be 
                        spaced in such a way as to maximise the distance 
                        between the points. If only one field per slitlet is 
                        requested, the field point will be at the centre.
    '''
    fields = []
    if self.cfg['pattern'] == 'brick_wall':
      pattern_data = self.cfg['pattern_data'] 
      nfields_per_slitlet = int(nfields/pattern_data['n_slitlets'])
      slit_length = (pattern_data['n_slitlets'] * \
                     pattern_data['slitlet_length']) + \
                    ((pattern_data['n_slitlets'] - 1) * \
                     pattern_data['slitlet_separation'])
      y = self.cfg['pattern_data']['stagger_length']/2.
      for s in range(pattern_data['n_slitlets']):
        x_s = (s*(pattern_data['slitlet_length'] + 
                  pattern_data['slitlet_separation'])) - slit_length/2.
        x_e = ((s+1)*pattern_data['slitlet_length'] +
               s*pattern_data['slitlet_separation']) - slit_length/2.
        if nfields_per_slitlet == 1:
          fields.append((x_s+(x_e-x_s)/2., y))
        elif nfields_per_slitlet > 1:
          x_sampling = pattern_data['slitlet_length']/(nfields_per_slitlet-1)
          for x in range(0, nfields_per_slitlet):
            fields.append((x_s + (x * x_sampling), y))
        y = -y
          
    if debug:
      plt.plot([xy[0] for xy in fields], [xy[1] for xy in fields], 'ko')
      plt.show()
      
    return fields
