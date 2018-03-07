# instrument_builder

## Overview
Construct an instrument from a series of components.

Current components include preoptics, IFUs, spectrographs and detectors. The corresponding files are stored as JSON in `etc/configs` and are loaded when an Instrument() instance is created.

When defining a new instrument type, a new object should be created that inherits and calls the constructor from the Instrument() base class. Instrument specific functions can then be written for that particular instrument type e.g. constructing the fields for the entrance slit.

Current Instrument() child classes include:

- "SWIFT_like" - A spectrographic IFU instrument utilising a demagnifying lenslet array in a brick-wall type pattern. 

## Caveats 
Be aware that it is possible to create an undefinable instrument type, e.g. creating an instrument with a SWIFT type IFU without defining slicer stack parameters. You are responsible for making sure that the instrument is realisable and defined by ensuring that the Instrument() child class has access to all the appropriate configuration items that are required by it. This is best done by wrapping its constructor with a try/except clause, attempt access to all the required keys and catching any key errors.

