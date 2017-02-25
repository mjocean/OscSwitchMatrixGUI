PyProcGame GUI Development Tool (formerly OscSwitchMatrixGUI)
==================

A cross-platform (wxPython-based) interactive testing tool that lets you send switch events to the OSC mode for PyProcGame and see lamp updates.
(Thread for questions/support: http://www.pinballcontrollers.com/forum/index.php?topic=1400)

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/gui-tool-buffy-example.png "Screenshot of the tool being used for Buffy testing with lamps and switches enabled")

The tool reads your machine yaml for switch definitions.  Left click a switch to toggle it 
(mouse down for active, mouse up for inactive), and right click to turn it on.  If no playfield image is provided, the user gets a simple switch matrix interface based on the game's machine yaml file.

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/OSC_Gui_Preview.png "Screenshot of the tool running against my T2.yaml")

If you provide a playfield image as a background (command line option -i [filemname]), you may use the layout mode to place lamps and switches around the playfield (make sure you save your layout!  --next time load with -l [file.layout]).

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/OSC_Gui_PlayfieldLayout.png "Screenshot of the tool running in graphical mode against my T2.yaml")

RGB Show creation using image sequences (and real-time preview):

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/rgb_show_maker.png "RGB Show maker")

This has been tested with Williams machines and PDB boards.  Both switch number types are supported

# Requirements:
You will need:

1. A SkeletonGame installation (which includes pyOSC and an OSC mode with RGB support): http://skeletongame.com/ (or you can add the OSC mode it provides to your working PyProcGame based game).

2. wxPython.  http://www.wxpython.org/download.php

