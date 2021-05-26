# gmcode

Python helper for writing g-code

## Motivation

I have spent a fair bit of time standing in front of a manual mill and turning wheels and levers until a part came out. After one particular day where I cut to a dimension of 22.1 instead of 21.2 three times - each time ruining a part I had already spent 2 hours on - I decided machining is one of those repetitive, error prone jobs that is very suited to automation. So I built myself a CNC router/mill.

Traditional CAM packages are useless to me because:

* I have lost a lot of work previously when I lost access to a subscription model CAD package. This is unacceptable, and I'll now go to extreme lengths to use reproducible software, which excludes all restrictively licensed CAM software.
* The user friendly interfaces and the high-level abstraction ontop of the g-code are inefficient for me. I know where I want my tools to cut, I don't want to have to learn how to make a CAM package drive a tool there.
* I use CadQuery to produce models in Python. I have all the dimensions of my models available to me as Python objects, so it would be unproductive to step out of Python and into some monolithic CAM package.

## Geometry classes

I have some classes in `geom.py` that might appear to be general purpose, but note they are customised for the XY plane of a CNC router. eg. the "normal" of a line is constructed by taking it's tangent and cross multiply it with the Z unit vector. I would not use them in any other packages if I were you.

## Similar packages

### [mecode](https://github.com/jminardi/mecode)

This was absolutely the inspiration for gmcode. I started using it, but I had some minor annoyances with the bloat introduced from 3D printer features and serial communications.
