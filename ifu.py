import json
import numpy as np
import pylab as plt

from component import *

class IFU(object):
  def __init__(self, preoptics_config_name, slicer_config_name, 
    slit_config_name, config_dir="etc/configs"):
    config_dir = config_dir.rstrip('/')
    if preoptics_config_name is not None:
      self.preoptics = Preoptics(config_dir + '/preoptics.json', 
        preoptics_config_name)
    if slicer_config_name is not None:
      self.slicer = Slicer(config_dir + '/slicers.json', slicer_config_name)
    if slit_config_name is not None:
      self.slit = Slit(config_dir + '/slits.json', slit_config_name)

class IFU_SWIFT(IFU):
  '''
    A SWIFT-type IFU with demagnifying lenslet array in a brick-wall type 
    pattern.
  '''
  def __init__(self, preoptics_config_name, slicer_config_name,
    slit_config_name, config_dir="etc/configs"):
    try:
      assert preoptics_config_name is not None
      assert slicer_config_name is not None
      assert slit_config_name is not None
    except AssertionError:
      print "one of the configs has not been supplied."
      exit(0)
    super(IFU_SWIFT, self).__init__(preoptics_config_name, 
      slicer_config_name, slit_config_name, config_dir)

    try:
      self.n_slices = self.n_slitlets = self.slicer.cfg['n_slices']
      self.preooptics_anamorphic_magnification = \
        self.preoptics.cfg['image_scale_across_slices_arcsec_per_mm'] / \
        self.preoptics.cfg['image_scale_along_slices_arcsec_per_mm']

      self.slicer_spaxel_scale = (self.slicer.cfg['slice_width_physical'] * \
        self.preooptics_anamorphic_magnification, \
        self.slicer.cfg['slice_width_physical']) # (along, across)
      
      self.slicer_dimensions_physical = ( \
        self.slicer_spaxel_scale[0] * self.slicer.cfg['slice_length_spaxels'], \
        self.slicer_spaxel_scale[1] * self.n_slices) # (along, across)

      self.slice_active_spaxels = self.slicer.cfg['slice_length_spaxels'] - \
        self.slicer.cfg['slice_inactive_spaxels']  

      self.slicer_dimensions_physical_active = ( \
        self.slicer_spaxel_scale[0] * self.slice_active_spaxels, \
        self.slicer_spaxel_scale[1] * self.n_slices) # (along, across)

      self.slicer_FOV = (self.slicer_dimensions_physical_active[0] * \
        self.preoptics.cfg['image_scale_along_slices_arcsec_per_mm']*1E3, \
        self.slicer_dimensions_physical_active[1] * \
        self.preoptics.cfg['image_scale_across_slices_arcsec_per_mm']*1E3)

      self.slitlet_length_physical_active = \
        self.slicer_dimensions_physical_active[0] * \
        self.slit.cfg['stack_to_entrance_slit_magnification']

      self.slitlet_separation_physical = \
        self.slicer.cfg['slice_inactive_spaxels'] * \
        self.slicer_spaxel_scale[0] * \
        self.slit.cfg['stack_to_entrance_slit_magnification']

      # following taken from geometry of packing circular lenslets
      self.stagger_length = self.slit.cfg['lenslet_diameter'] * 0.5 * (3**0.5) 
    except KeyError:
      print "unable to find necessary key in config files. it's possible " + \
        "you have chosen an incompatible component assembly for this type " + \
        "of ifu."
      exit(0)    

  def getEntranceSlitFields(self, nfields, nspectrographs=2, lumultiplier=1e3, 
    verbose=True, debug=False):
    '''
      Takes the ifu component assembly and number of fields [nfields] and 
      returns a list of corresponding field points at the entrance slit. 

      To get the field points, we divide the number of fields [nfields] by the 
      number of slices, creating this many fields per slitlet. Fields will be 
      spaced in such a way as to maximise the distance between the points. If
      only one field per slice is requested, the field point will be at the 
      centre. The total slit length [slit_length_physical] used for this 
      calculation takes into account the number of spectrographs 
      [nspectrographs] over which the slit would be divided.

      If interfacing with Zemax, it may be necessary to move the units to lens
      units (typically mm). This means setting the [lumultiplier] parameter.
    '''
    fields = []

    n_slices_per_spec = self.n_slices/nspectrographs
    slit_length_physical = (n_slices_per_spec * \
      self.slitlet_length_physical_active) + ((n_slices_per_spec-1) * \
      self.slitlet_separation_physical)

    try:
      assert nfields % self.n_slitlets == 0
    except AssertionError:
      print "number of fields should be a multiple of the number of slitlets"
      exit(0)
        
    nfields_per_slitlet = int(nfields/self.n_slitlets)
    y = self.stagger_length/2.
    for s in range(n_slices_per_spec):
      x_s = (s*(self.slitlet_length_physical_active + \
        self.slitlet_separation_physical)) - slit_length_physical/2.
      x_e = ((s+1)*self.slitlet_length_physical_active + \
        s*self.slitlet_separation_physical) - slit_length_physical/2.
      print x_s, x_e
      if nfields_per_slitlet == 1:
        fields.append((x_s+(x_e-x_s)/2., y))
      elif nfields_per_slitlet > 1:
        x_sampling = self.slitlet_length_physical_active/(nfields_per_slitlet-1)
        for x in range(0, nfields_per_slitlet):
          fields.append((x_s + (x * x_sampling), y))
      y = -y

    if lumultiplier != 1:
      tmp = []
      [tmp.append((xy[0]*lumultiplier, xy[1]*lumultiplier)) for xy in fields]
      fields = tmp

    if debug:
      plt.plot([xy[0] for xy in fields], [xy[1] for xy in fields], 'ko')
      plt.show()
        
    return fields
