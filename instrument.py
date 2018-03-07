import json
import numpy as np
import pylab as plt

from component import *

class Instrument(object):
  def __init__(self, preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir="etc/configs"):
    config_dir = config_dir.rstrip('/')
    if preoptics_config_name is not None:
      self.preoptics = Preoptics(config_dir + '/preoptics.json', 
        preoptics_config_name)
    if ifu_config_name is not None:
      self.ifu = IFU(config_dir + '/ifus.json', ifu_config_name)
    if spectrograph_config_name is not None:
      self.spectrograph_config_name = Spectrograph(config_dir + \
      '/spectrographs.json', spectrograph_config_name)
    if detector_config_name is not None:
      self.detector_config_name = Detector(config_dir + \
      '/detectors.json', detector_config_name)      

class SWIFT_like(Instrument):
  '''
    Instrument using IFU with demagnifying lenslet array in a brick-wall type 
    pattern.
  '''
  def __init__(self, preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir="etc/configs"):
    try:
      assert preoptics_config_name is not None
      assert ifu_config_name is not None
      assert spectrograph_config_name is not None
      assert detector_config_name is not None
    except AssertionError:
      print "one of the configs has not been supplied."
      exit(0)
    super(SWIFT_like, self).__init__(preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir)

    try:
      self.n_slices = self.n_slitlets = self.ifu.cfg['n_slices']
      self.preooptics_anamorphic_magnification = \
        self.preoptics.cfg['magnification_along_slices'] / \
        self.preoptics.cfg['magnification_across_slices']

      self.slicer_spaxel_scale = (self.ifu.cfg['slice_width_physical'] * \
        self.preooptics_anamorphic_magnification, \
        self.ifu.cfg['slice_width_physical']) # (along, across)
      
      self.slicer_dimensions_physical = ( \
        self.slicer_spaxel_scale[0] * self.ifu.cfg['slice_length_spaxels'], \
        self.slicer_spaxel_scale[1] * self.n_slices) # (along, across)

      self.slice_active_spaxels = self.ifu.cfg['slice_length_spaxels'] - \
        self.ifu.cfg['slice_inactive_spaxels']  

      self.slicer_dimensions_physical_active = ( \
        self.slicer_spaxel_scale[0] * self.slice_active_spaxels, \
        self.slicer_spaxel_scale[1] * self.n_slices) # (along, across)

      self.slitlet_length_physical_active = \
        self.slicer_dimensions_physical_active[0] * \
        self.ifu.cfg['stack_to_entrance_slit_magnification']

      self.slitlet_separation_physical = \
        self.ifu.cfg['slice_inactive_spaxels'] * \
        self.slicer_spaxel_scale[0] * \
        self.ifu.cfg['stack_to_entrance_slit_magnification']

      # following taken from geometry of packing circular lenslets
      self.stagger_length = self.ifu.cfg['lenslet_diameter'] * 0.5 * (3**0.5) 
    except KeyError, e:
      print e
      print "unable to find necessary key in config files. it's possible " + \
        "you have chosen an incompatible component assembly for this type " + \
        "of ifu."
      exit(0)    

  def getEntranceSlitFields(self, n_fields, n_spectrographs=1, lumultiplier=1e3, 
    verbose=True, debug=False):
    '''
      Takes the ifu component assembly and number of fields [n_fields] and 
      returns a list of corresponding field points at the entrance slit. 

      To get the field points, we divide the number of fields [nfields] by the 
      number of slices, creating this many fields per slitlet. Fields will be 
      spaced in such a way as to maximise the distance between the points. If
      only one field per slice is requested, the field point will be at the 
      centre. The total slit length [slit_length_physical] used for this 
      calculation takes into account the number of spectrographs 
      [n_spectrographs] over which the slit would be divided.

      If interfacing with Zemax, it may be necessary to move the units to lens
      units (typically mm). This means setting the [lumultiplier] parameter.
    '''
    fields = []

    n_slices_per_spec = self.n_slices/n_spectrographs
    slit_length_physical = (n_slices_per_spec * \
      self.slitlet_length_physical_active) + ((n_slices_per_spec-1) * \
      self.slitlet_separation_physical)

    try:
      assert n_fields % self.n_slitlets == 0
    except AssertionError:
      print "number of fields should be a multiple of the number of slitlets"
      exit(0)
        
    nfields_per_slitlet = int(n_fields/self.n_slitlets)
    y = self.stagger_length/2.
    for s in range(n_slices_per_spec):
      this_slice_fields = []
      x_s = (s*(self.slitlet_length_physical_active + \
        self.slitlet_separation_physical)) - slit_length_physical/2.
      x_e = ((s+1)*self.slitlet_length_physical_active + \
        s*self.slitlet_separation_physical) - slit_length_physical/2.
      if nfields_per_slitlet == 1:
        this_slice_fields.append((x_s+(x_e-x_s)/2., y))
      elif nfields_per_slitlet > 1:
        x_sampling = self.slitlet_length_physical_active/(nfields_per_slitlet-1)
        for x in range(0, nfields_per_slitlet):
          this_slice_fields.append((x_s + (x * x_sampling), y))
      fields.append(this_slice_fields)
      y = -y

    if lumultiplier != 1:
      tmp_fields = []
      for slice_fields in fields:
        tmp_slice_fields = []
        for xy in slice_fields:
          tmp_slice_fields.append((xy[0]*lumultiplier, xy[1]*lumultiplier))
        tmp_fields.append(tmp_slice_fields)
      fields = tmp_fields

    if debug:
      for slice_fields in fields:
        plt.plot([xy[0] for xy in slice_fields], \
          [xy[1] for xy in slice_fields], 'o')
      plt.show()
        
    return fields
