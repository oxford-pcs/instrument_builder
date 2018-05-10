import json
import logging
import os

import numpy as np
import pylab as plt

from component import *

class Instrument(object):
  def __init__(self, preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir="etc/configs", 
    logger=None):

    # Assemble logger.
    #
    if logger is None:
      print "hello"
      logger = logging.getLogger()
      logger.setLevel(logging.DEBUG)
      ch = logging.StreamHandler()
      ch.setLevel(logging.DEBUG)
      formatter = logging.Formatter("(" + str(os.getpid()) + \
        ") %(asctime)s:%(levelname)s: %(message)s")
      ch.setFormatter(formatter)
      logger.addHandler(ch)
    self.logger = logger

    config_dir = config_dir.rstrip('/')
    if preoptics_config_name is not None:
      self.preoptics = Preoptics(config_dir + '/preoptics.json', 
        preoptics_config_name, logger)
    if ifu_config_name is not None:
      self.ifu = IFU(config_dir + '/ifus.json', ifu_config_name, logger)
    if spectrograph_config_name is not None:
      self.spectrograph = Spectrograph(config_dir + \
      '/spectrographs.json', spectrograph_config_name, logger)
    if detector_config_name is not None:
      self.detector = Detector(config_dir + \
      '/detectors.json', detector_config_name, logger)      

class SWIFT_like(Instrument):
  '''
    Instrument using IFU with demagnifying lenslet array in a brick-wall type 
    pattern.
  '''
  def __init__(self, preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir="etc/configs",
    logger=None):
    super(SWIFT_like, self).__init__(preoptics_config_name, ifu_config_name, 
    spectrograph_config_name, detector_config_name, config_dir, logger)

    self.logger = logger
    self.assembled = False

    # Test we have all the necessary keys to construct this instrument.
    #
    try:
      self.ifu.cfg['n_slices']
      self.spectrograph.cfg['camera_EFFL']
      self.spectrograph.cfg['collimator_EFFL']
      self.spectrograph.cfg['n_spectrographs']
      self.detector.cfg['pixel_pitch']
      self.preoptics.cfg['magnification_along_slices']
      self.preoptics.cfg['magnification_across_slices']
      self.ifu.cfg['slice_width_physical']
      self.ifu.cfg['slice_length_spaxels']
      self.ifu.cfg['slice_inactive_spaxels']
      self.ifu.cfg['stack_to_entrance_slit_magnification']
      self.ifu.cfg['lenslet_diameter']
    except KeyError, e:
      logger.critical(" Unable to find necessary key in config files. It's " + \
        "possible you have chosen an incompatible component assembly for " + \
        "this type of instrument.")
      exit(0)

  def assemble(self, verbose=True, debug=False):
    '''
      Assemble the instrument, given the configuration parameters.
    '''
    self.n_slices = self.n_slitlets = self.ifu.cfg['n_slices']
    self.camera_EFFL = self.spectrograph.cfg['camera_EFFL']
    self.collimator_EFFL = self.spectrograph.cfg['collimator_EFFL']
    self.n_spectrographs = self.spectrograph.cfg['n_spectrographs']
    self.preoptics_WFNO = self.preoptics.cfg['WFNO']
    self.detector_pixel_pitch = self.detector.cfg['pixel_pitch']

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

    if verbose:
      self.logger.debug(" Created SWIFT_like instrument with following " + \
        "parameters:")
      self.logger.debug(" -> Pre-optics anamorphic magnification: " + \
        str(round(self.preooptics_anamorphic_magnification, 1)))
      self.logger.debug(" -> Number of slices: " + \
        str(self.n_slices))
      self.logger.debug(" -> Slicer spaxel scale along and across slices " + \
        "(mm): " + \
        str(round(self.slicer_spaxel_scale[0]*1E3, 2)) + ", " + \
        str(round(self.slicer_spaxel_scale[1]*1E3, 2)))      
      self.logger.debug(" -> Number of active spaxels along: " + \
        str(self.slice_active_spaxels))   
      self.logger.debug(" -> Active slicer dimensions along and across " + \
        "slices (mm): " + \
        str(round(self.slicer_dimensions_physical_active[0]*1E3, 2)) + ", " + \
        str(round(self.slicer_dimensions_physical_active[1]*1E3, 2)))   
      self.logger.debug(" -> Active slitlet length (mm): " + \
        str(round(self.slitlet_length_physical_active*1E3, 3)))     
      self.logger.debug(" -> Slitlet separation (mm): " + \
        str(round(self.slitlet_separation_physical*1E3, 3)))  
      self.logger.debug(" -> Stagger length (mm): " + \
        str(round(self.stagger_length*1E3, 3)))     
      self.logger.debug(" -> Camera EFFL (mm): " + \
        str(round(self.camera_EFFL*1E3, 1)))
      self.logger.debug(" -> Collimator EFFL (mm): " + \
        str(round(self.collimator_EFFL*1E3, 1))) 
      self.logger.debug(" -> Number of spectrographs: " + \
        str(self.n_spectrographs))  
      self.logger.debug(" -> Detector pixel pitch (um): " + \
        str(round(self.detector_pixel_pitch*1E6, 1)))  

    self.assembled=True

  def getEntranceSlitFields(self, n_fields_per_slitlet, n_spectrographs=1, 
    lumultiplier=1e3, verbose=True, debug=False):
    '''
      Takes the ifu component assembly and number of fields per slitlet, 
      [nfields_per_slitlet] and returns a list of corresponding field points 
      at the entrance slit. 

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
    if self.assembled:
      fields = []

      n_slices_per_spec = self.n_slices/n_spectrographs
      slit_length_physical = (n_slices_per_spec * \
        self.slitlet_length_physical_active) + ((n_slices_per_spec-1) * \
        self.slitlet_separation_physical)
          
      y = self.stagger_length/2.
      for s in range(n_slices_per_spec):
        this_slice_fields = []
        x_s = (s*(self.slitlet_length_physical_active + \
          self.slitlet_separation_physical)) - slit_length_physical/2.
        x_e = ((s+1)*self.slitlet_length_physical_active + \
          s*self.slitlet_separation_physical) - slit_length_physical/2.
        if n_fields_per_slitlet == 1:
          this_slice_fields.append((x_s+(x_e-x_s)/2., y))
        elif n_fields_per_slitlet > 1:
          x_sampling = self.slitlet_length_physical_active/ \
          (n_fields_per_slitlet-1)
          for x in range(0, n_fields_per_slitlet):
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

    else:
      logger.critical(" Instrument has not been assembled. Call assemble() " + \
        "first.")
      exit(0)
