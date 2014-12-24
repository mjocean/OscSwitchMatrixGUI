#!/usr/bin/python
# 
# Copyright (c) 2014 Michael Ocean
#
# Licence: The MIT License (MIT)
#
#    ________  ______   __                        __   ____  _____ ______   _________            __     
#   / ____/ / / /  _/  / /_  ____ _________  ____/ /  / __ \/ ___// ____/  / ____/ (_)__  ____  / /_    
#  / / __/ / / // /   / __ \/ __ `/ ___/ _ \/ __  /  / / / /\__ \/ /      / /   / / / _ \/ __ \/ __/    
# / /_/ / /_/ // /   / /_/ / /_/ (__  )  __/ /_/ /  / /_/ /___/ / /___   / /___/ / /  __/ / / / /_      
# \____/\____/___/  /_.___/\__,_/____/\___/\__,_/   \____//____/\____/   \____/_/_/\___/_/ /_/\__/      
                                                                                                      
#     ____              ____        ____                  ______                                                                                                                                                                                                                                      
#    / __/___  _____   / __ \__  __/ __ \_________  _____/ ____/___ _____ ___  ___                                                                                                                                                                                                                    
#   / /_/ __ \/ ___/  / /_/ / / / / /_/ / ___/ __ \/ ___/ / __/ __ `/ __ `__ \/ _ \                                                                                                                                                                                                                   
#  / __/ /_/ / /     / ____/ /_/ / ____/ /  / /_/ / /__/ /_/ / /_/ / / / / / /  __/                                                                                                                                                                                                                   
# /_/  \____/_/     /_/    \__, /_/   /_/   \____/\___/\____/\__,_/_/ /_/ /_/\___/                                                                                                                                                                                                                    
#                         /____/                                                                                                                                                                                                                                                                      
#
# Written by Michael Ocean 
# a GUI-based switch matrix for use with the PyProcGame OSC game mode by Brian Madden; 
# this was "inspired by" Brian Madden's command-line OSC_Sender tool 
#   (read: I read his code so I didn't have to figure out how to send OSC messages)
#
# Requirements:
# You will need...
# 1) a working PyProcGame game with the OSC mode from Brian.  Read more:
#       http://www.pinballcontrollers.com/forum/index.php?topic=983.0
#
# 2) wxPython.  http://www.wxpython.org/download.php
#
# This has been tested with Williams machines and PDB boards.  
# Both switch number types are supported
#
# -------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import OSC
from optparse import OptionParser
import socket
import wx
import yaml

try:
  if(wx.NullColor is None):
    wx.NullColor = wx.NullColour
except:
  wx.NullColor = wx.NullColour


states = {}

server_ip = socket.gethostbyname(socket.gethostname())

parser = OptionParser()

parser.add_option("-s", "--address",
                  action="store", type="string", 
                  dest="server_ip", default=server_ip,
                  help="Address of server.  Default is %s." % server_ip)

parser.add_option("-p", "--port",
                  action="store", type="int", 
                  dest="server_port", default=9000,
                  help="Port on OSC server.  Default is 9000.")

parser.add_option("-y", "--yaml",
                  action="store", type="string", 
                  dest="yaml_file", default='game.yaml',
                  help="The yaml file name for the machine definition.  Default is 'game.yaml'.")

(options, args) = parser.parse_args()
options = vars(options)

osc_client = OSC.OSCClient()
osc_client.connect((server_ip, options['server_port']))

##############################################
# GUI Event Handlers
##############################################
                                                                                                                                                                                                                                                                                        
def onLeftButtonDOWN(event):
    sendOSC(event, True)
    print "LEFT Button  [%s] DOWN!" % event.EventObject.id

def onLeftButtonUP(event):
    sendOSC(event, False)
    print "LEFT Button [%s] UP!" % event.EventObject.id

def onRightButton(event):
    btn = event.EventObject
    sendOSC(event, not(states[btn.id]))
    print "RIGHT Button [%s] pressed!" % btn.id

def sendOSC(evt_src, new_state=None):
    btn = evt_src.EventObject
    addr = '/sw/%s' % btn.id
    # addr = '/sw/%s' % btn.GetLabel()
    osc_msg = OSC.OSCMessage(addr)
    if(states[btn.id]==False and new_state==True):
        btn.SetBackgroundColour(wx.GREEN)
        states[btn.id]=True
        osc_msg.append(1)
        print('%s %s' % (addr, 1) )
    elif(states[btn.id]==True and new_state==False):
        btn.SetBackgroundColour(wx.NullColor)
        states[btn.id]=False        
        osc_msg.append(0)
        print('%s %s' % (addr, 0) )
    else:
        print("click ignored")
    osc_client.send(osc_msg)
    btn.ClearBackground()

##############################################
# GUI: Button Maker
##############################################
def makeButton(frame, sname, switches, number=None):
    if(number is None):
      number = switches[sname]['number']
    try:
      lbl = switches[sname]['label']
      #number = number + "\n" + lbl
    except Exception, e:
      lbl = sname
      pass

    button = wx.Button(frame, label='%s\n%s' % (sname, number))

    button.SetToolTipString(lbl)

    button.id = sname
    states[button.id] = False
    button.Bind(wx.EVT_LEFT_DOWN, onLeftButtonDOWN)
    button.Bind(wx.EVT_LEFT_UP, onLeftButtonUP)
    button.Bind(wx.EVT_RIGHT_DOWN, onRightButton)

    button.SetBackgroundColour(wx.NullColor)
    button.ClearBackground()

    return button

##############################################
# main()
##############################################

def main():
    # make the GUI components
    app = wx.App(redirect=False)
    frame = wx.Frame(None, -1, 'OSC Switch Matrix for PyProcGame', pos=wx.DefaultPosition, size=wx.Size(600,400))
    gs = wx.GridSizer(9, 8, 2, 2) # rows, cols, gap

    # more features to come...
    # menuBar = wx.MenuBar()
    # fileMenu = wx.Menu()
    # exitMenuItem = fileMenu.Append(wx.NewId(), "Exit",
    #                                "Exit the application")
    # menuBar.Append(fileMenu, "&File")
    # frame.Bind(wx.EVT_MENU, frame.Close, exitMenuItem)
    # frame.SetMenuBar(menuBar)
 
    # hold all the switches so we can know which 
    # ones are outside the matrix
    game_switches = {}

    # load the yaml file to find all the switches
    try:
      yaml_data = yaml.load(open(options['yaml_file'], 'r'))
    except Exception, e:
      print "Failed to find yaml file '%s' or yaml file was invalid." % options['yaml_file']
      print "----"
      print e
      return 0

    if 'PRSwitches' in yaml_data:
      switches = yaml_data['PRSwitches']
      for name in switches:
        item_dict = switches[name]
        yaml_number = str(item_dict['number'])
          
        if 'label' in item_dict:
          swlabel = item_dict['label']
        if 'type' in item_dict:
          swtype = item_dict['type']
        game_switches[yaml_number] = name
    else:
      print("PRSwitches section NOT found in specified yaml file '%s'.\nExiting..." % options['yaml_file'])
      print "----"
      print e
      return 0

    PDB_switches = yaml_data['PRGame']['machineType'] == "pdb"
    if(PDB_switches):
      print("Using PDB style switch numbering.  Trying to order switches...")
      for c in range(0,8):
          for r in range(0,16):
              switch_code = '%s/%s' % (c,r)
              try:
                sname = game_switches[switch_code]
                button = makeButton(frame, sname, switches)
                gs.Add(button, 0, wx.EXPAND)
                # remove the switch from the to-do list
                del game_switches[switch_code]
              except Exception, e:
                print "Warning: didn't find a definition for switch at location (%d,%d)'" % (c,r)

    else:
      print("Using Williams/Stern style switch numbering.  Trying to order switches...")
      for r in range(0,8):
          for c in range(0,8):
              switch_code = 'S%s%s' % (c+1, r+1)
              try:
                sname = game_switches[switch_code]
                button = makeButton(frame, sname, switches)
                # remove the switch from the to-do list
                del game_switches[switch_code]
              except Exception, e:
                print "Warning: didn't find a definition for switch at location (%d,%d)'" % (c+1,r+1)
                sname = "N/A"
                # print e                
                button = makeButton(frame, sname, switches,switch_code)
                button.Enabled = False
              gs.Add(button, 0, wx.EXPAND)

    # go through the matrix trying to find switches from the yaml

    print "Adding remaining dedicated switches..."
    print game_switches

    # anything left in that dict wasn't in the matrix (i.e., a dedicated switch)

    for i in range(0,32):
      switch_code = "SD%s" % i
      try:
        sname = game_switches[switch_code]
        button = makeButton(frame, sname, switches)
        gs.Add(button, 0, wx.EXPAND)
      except Exception, e:
        pass

    frame.SetSizer(gs)
    frame.Show()
    app.MainLoop()

    # END main()

if __name__ == '__main__':
    main()
