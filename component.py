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
      print "pre-optics config not found"
      return None

class Slicer(Component):
  def __init__(self, path, name):
    super(Slicer, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "slicer config not found"
      return None

class Slit(Component):
  def __init__(self, path, name):
    super(Slit, self).__init__(path, name)
    try:
      assert self.cfg is not None
    except AssertionError:
      print "slit config not found"
      return None