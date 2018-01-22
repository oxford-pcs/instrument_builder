import json

class detector():
  def __init__(self, path, name):
    self.cfg = self._getDetectorConfigFromFile(path, name)
    
  def _getDetectorConfigFromFile(self, path, name):
      '''
        Return detector config with name [name] from a JSON file at path [path].
      '''
      with open(path) as fp:
        cfg = json.load(fp)
        
      detector = None
      for c in cfg:
        if c['name'] == name:
          detector = c
          break;
        else:
          continue
      try:
        assert detector is not None
      except AssertionError:
        print "detector config not found"
      
      return detector     
