# config_manager

A repository containing configuration files and parsers required by other repositories.

Slit "patterns" and detectors can be added to the `slits.json` and `detectors.json` files in this package respectively, but if adding a new 
type of pattern the corresponding logic to decompose it into field points must be added to the `getFieldsFromSlitPattern()` function 
in `slit.py`.
