import json

class Component(object):
  def __init__(self, path, name):
    self.cfg = self._getConfigFromFile(path, name)

  def _getConfigFromFile(self, path, name):
      '''
        Return config with name [name] from a JSON file at path [path].
      '''
      with open(path) as fp:
        cfg = json.load(fp)
        
      config = None
      for c in cfg:
        if c['name'] == name:
          config = c
          break;
        else:
          continue

      return config     
  
class Preoptics(Component):
  def __init__(self, path, name):
    super(Preoptics, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "Pre-optics config not found"
      return None

class IFU(Component):
  def __init__(self, path, name):
    super(IFU, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "IFU config not found"
      return None

class Spectrograph(Component):
  def __init__(self, path, name):
    super(Spectrograph, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "Spectrograph config not found"
      return None      

class Detector(Component):
  def __init__(self, path, name):
    super(Detector, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "Detector config not found"
      return None

