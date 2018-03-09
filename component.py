import json

class Component(object):
  def __init__(self, path, name, logger):
    self.cfg = self._getConfigFromFile(path, name)

    # Assemble logger.
    #
    if logger is None:
      logger = logging.getLogger()
      logger.setLevel(logging.DEBUG)
      ch = logging.StreamHandler()
      ch.setLevel(logging.DEBUG)
      formatter = logging.Formatter("(" + str(os.getpid()) + \
        ") %(asctime)s:%(levelname)s: %(message)s")
      ch.setFormatter(formatter)
      logger.addHandler(ch)
    self.logger = logger

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
  def __init__(self, path, name, logger):
    super(Preoptics, self).__init__(path, name, logger)
    try:
      assert self.cfg is not None
    except AssertionError:
      logger.critical("Pre-optics config not found.")
      exit(0)

class IFU(Component):
  def __init__(self, path, name, logger):
    super(IFU, self).__init__(path, name, logger)
    try:
      assert self.cfg is not None
    except AssertionError:
      logger.critical("IFU config not found.")
      exit(0)

class Spectrograph(Component):
  def __init__(self, path, name, logger):
    super(Spectrograph, self).__init__(path, name, logger)
    try:
      assert self.cfg is not None
    except AssertionError:
      logger.critical("Spectrograph config not found.")
      exit(0)    

class Detector(Component):
  def __init__(self, path, name, logger):
    super(Detector, self).__init__(path, name, logger)
    try:
      assert self.cfg is not None
    except AssertionError:
      logger.critical("Detector config not found.")
      exit(0)

