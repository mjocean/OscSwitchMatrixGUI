OscSwitchMatrixGUI
==================

A wxPython-based Graphical switch matrix that lets you send switch events to the OSC mode for PyProcGame.

The tool reads your machine yaml for switch definitions.  Left click a switch to toggle it 
(mouse down for active, mouse up for inactive), and right click to turn it on.

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/OSC_Gui_Preview.png "Screenshot of the tool running against my T2.yaml")

If you're feeling fancy, you can use a playfield image as a background (command line option -i [filemname]) and use the layout mode to place the switches around the playfield (make sure you save your layout!  --next time load with -l [file.layout]).

![Screenshot](https://dl.dropboxusercontent.com/u/254844/T2-preview/OSC_Gui_PlayfieldLayout.png "Screenshot of the tool running in graphical mode against my T2.yaml")

This has been tested with Williams machines and PDB boards.  Both switch number types are supported

# Requirements:
You will need:

1. a working PyProcGame game with the OSC mode from Brian.  Read more:
       http://www.pinballcontrollers.com/forum/index.php?topic=983.0

2. wxPython.  http://www.wxpython.org/download.php

