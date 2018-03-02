# ifu_builder

## Overview
Conceptually construct an IFU from a series of components.

Current components include preoptics, slicers and slits. The corresponding files are stored as JSON in `etc/configs` and are loaded when an IFU instance is created.

When defining a new IFU type, a new IFU object should be created that inherits and calls the default constructor from the IFU base class. IFU specific functions can then be written for that particular IFU type e.g. constructing the fields for the entrance slit.

Current IFU child classes include:

- "IFU_SWIFT" - For a SWIFT-like IFU with anamorphic preoptics and demagnifying lenslets in a brickwall pattern. 

## Caveats 
Be aware that the entries in the configuration files do not distinguish between IFU types and thus it is possible to create an undefinable IFU. You are responsible for making sure that the IFU child class functions only access configuration items that are defined for it. For example, you may create an "IFU_brickwall" IFU but not define the `stack_to_entrance_slit_magnification` item in `slits.json`. These keyerror exceptions should be caught in the constructor of the child class.

