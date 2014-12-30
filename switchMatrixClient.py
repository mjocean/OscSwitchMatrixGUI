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
import random

try:
    if(wx.NullColor is None):
        wx.NullColor = wx.NullColour
except:
    wx.NullColor = wx.NullColour

states = {}
buttons = {}

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

parser.add_option("-i", "--image",
                                    action="store", type="string", 
                                    dest="bg_image", default=None,
                                    help="The file name for a playfield image.")

parser.add_option("-l", "--layout",
                                    action="store", type="string", 
                                    dest="layout_file", default=None,
                                    help="The file name for a playfield layout.  Disabled by default.")

(options, args) = parser.parse_args()
options = vars(options)

osc_client = OSC.OSCClient()
osc_client.connect((server_ip, options['server_port']))

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
class ButtonMaker(object):
    def __init__(self, frame):
        self.frame = frame
        self.buttonCounter = 0

    def onLeftButtonDOWN(self,event):
            sendOSC(event, True)
            print "LEFT Button  [%s] DOWN!" % event.EventObject.id

    def onLeftButtonUP(self,event):
            sendOSC(event, False)
            print "LEFT Button [%s] UP!" % event.EventObject.id

    def onRightButton(self,event):
        btn = event.EventObject
        print "RIGHT Button [%s] pressed!" % btn.id
        
        if(self.frame.layout_mode):
            self.frame.last_button_pressed_id = btn.id
            btn.SetBackgroundColour(wx.CYAN)
            self.frame.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
            print(self.frame.last_button_pressed_id)
        else:
            sendOSC(event, not(states[btn.id]))

    def makeButton(self, sname, switches, number=None):
        if(self.frame.graphical_mode):
            return self.makePFButton(sname, switches, number)
        else:
            return self.makeGridButton(sname, switches, number)        

    def makePFButton(self, sname, switches, number=None):
        if(number is None):
            number = switches[sname]['number']
        try:
            lbl = switches[sname]['label']
            #number = number + "\n" + lbl
        except Exception, e:
            lbl = sname
            pass

        btnlocation = find_key_in_list_of_dicts(sname, self.frame.layout_data['button_locations'])
        if sname in switches and (btnlocation is not None):
            y = btnlocation[sname]['y']
            x = btnlocation[sname]['x']
            pass
        else:
            x = int(self.buttonCounter/8)*25
            y = (self.buttonCounter%8)*20
            self.buttonCounter = self.buttonCounter+1
        #button = wx.Button(frame, pos=(x,y), size=(20,20), label='%s' % sname)
        button = wx.Button(self.frame, pos=(x,y), size=(25,20), label='%s' % number)

        button.SetWindowVariant(wx.WINDOW_VARIANT_MINI)

        button.SetToolTipString(lbl)

        button.id = sname
        states[button.id] = False
        buttons[button.id] = button

        button.Bind(wx.EVT_LEFT_DOWN, self.onLeftButtonDOWN)
        button.Bind(wx.EVT_LEFT_UP, self.onLeftButtonUP)
        button.Bind(wx.EVT_RIGHT_DOWN, self.onRightButton)

        button.SetBackgroundColour(wx.NullColor)
        button.ClearBackground()

        return button

    def makeGridButton(self, sname, switches, number=None, forced_frame=None):
        if(number is None):
            number = switches[sname]['number']
        try:
            lbl = switches[sname]['label']

        except Exception, e:
            lbl = sname
            pass

        if(forced_frame is None):
            frame = self.frame
        else:
            frame = forced_frame

        button = wx.Button(frame, label='%s\n%s' % (sname, number))

        button.SetToolTipString(lbl)
        button.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
        button.id = sname
        states[button.id] = False

        if(forced_frame is None):
            button.Bind(wx.EVT_LEFT_DOWN, self.onLeftButtonDOWN)
            button.Bind(wx.EVT_LEFT_UP, self.onLeftButtonUP)
            button.Bind(wx.EVT_RIGHT_DOWN, self.onRightButton)
        else:
            button.Bind(wx.EVT_LEFT_DOWN, self.onRightButton)
            # button.Bind(wx.EVT_LEFT_UP, self.onLeftButtonUP)
            # button.Bind(wx.EVT_RIGHT_DOWN, self.onRightButton)

        button.SetBackgroundColour(wx.NullColor)
        button.ClearBackground()

        return button


class MyFrame(wx.Frame):
    def __init__(self,  parent, id=-1, title="", 
            pos=wx.DefaultPosition, size=wx.DefaultSize, 
            style=wx.DEFAULT_FRAME_STYLE, name=""):
        super(MyFrame,self).__init__(parent, id, title, pos, size, style, name)

        self.layout_mode = False
        self.graphical_mode = False
        self.layout_data = {}

        self.layout_data['button_locations'] = []
        if(options['layout_file'] is not None):
            self.graphical_mode = True
            self.loadLayoutInfo(None)
        elif(options['bg_image'] is not None):
            self.graphical_mode = True

        if(self.graphical_mode):
            self.addImage()


    def addImage(self):
        if(options['bg_image'] is not None):
            # use this first
            bgfile = options['bg_image']
        elif('bg_image' in self.layout_data):
            bgfile = self.layout_data['bg_image']
        else:
            # why are we adding an image when none exists!?
            raise ValueError("Trying to add an image but the program is not in graphica mode!?")

        self.bmp = wx.Bitmap(bgfile)
        self.SetClientSizeWH(self.bmp.GetWidth(), self.bmp.GetHeight())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_LEFT_DOWN, self.LeftButtonDOWN)
        # more features to come...
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        editMenu = wx.Menu()

        saveLayoutMenu = fileMenu.Append(wx.NewId(), "Save Layout",
                                       "Saves the layout")

        exitMenuItem = fileMenu.Append(wx.NewId(), "Exit",
                                       "Exit the application")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")

        #oadLayoutMenu = wx.Menu()
        #self.Bind(wx.EVT_MENU, self.loadImage, loadImageMenu)
        self.Bind(wx.EVT_MENU, self.dumpLayoutInfo, saveLayoutMenu)
        

        self.Bind(wx.EVT_MENU, self.OnCloseFrame, exitMenuItem)

        self.toggleLayoutMode = editMenu.Append(wx.NewId(), 'Layout Mode', 
            'Right click switches to move them', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleEditMode, self.toggleLayoutMode)
            
        editMenu.Check(self.toggleLayoutMode.GetId(), False)

        self.SetMenuBar(menuBar)
        if(self.graphical_mode):
            self.newWin = wx.Frame(None, -1,'Switch Layout Pallete (click to place)', size=(400,300))
            self.newWin.Show(False)
            self.newWin.Bind(wx.EVT_CLOSE, self.hideSubWin)
        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

    def hideSubWin(self, event):
        self.newWin.Show(False)
        event.StopPropagation()

    #----------------------------------------------------------------------
    # Destroys the main frame which quits the wxPython application
    def OnExitApp(self, event):
        if(self.graphical_mode):
            self.newWin.Destroy()
        self.Destroy()


    # Makes sure the user was intending to quit the application
    def OnCloseFrame(self, event):
        dialog = wx.MessageDialog(self, message = "Are you sure you want to quit?", caption = "Quit?", style = wx.YES_NO, pos = wx.DefaultPosition)
        response = dialog.ShowModal()

        if (response == wx.ID_YES):
            self.OnExitApp(event)
        else:
            event.StopPropagation()



    def LeftButtonDOWN(self, event):
        if(self.layout_mode and self.last_button_pressed_id is not None):
            (x,y) = event.GetPositionTuple()
            bTmp = buttons[self.last_button_pressed_id]
            (w,h) = bTmp.GetClientSizeTuple()
            x = x - w/2
            y = y - h/2
            bTmp.MoveXY(x,y)
            bTmp.SetBackgroundColour(wx.NullColor)
            print("moved %s to (%d,%d)" % (self.last_button_pressed_id,x,y))
            bTmp = None
            self.last_button_pressed_id = None
            # self.SetCursor(wx.StockCursor(wx.CURSOR_STANDARD))
            
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

    def ToggleEditMode(self, state):
        self.layout_mode = self.toggleLayoutMode.IsChecked()
        self.last_button_pressed_id = None
        print(self.layout_mode)
        if(self.layout_mode == True):
            self.newWin.Show(True)
            wx.Frame.CenterOnScreen(self.newWin)
        else:
            self.newWin.Show(False)
        pass

    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        # yanked from ColourDB.py
        dc = evt.GetDC()
     
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.bmp, 0, 0)
        # alpha does NOT work on windows... blah.
        # dc.SetBrush(wx.Brush(wx.Colour(225,0,128,42)))
        # dc.DrawCircle(170, 230, 35)

    def dumpLayoutInfo(self, event):
        if(event is not None):
            saveFileDialog = wx.FileDialog(self, "Save As", "", "", 
                                          "Layout files (*.layout)|*.layout", 
                                          wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            saveFileDialog.ShowModal()
            fname = saveFileDialog.GetPath()
            saveFileDialog.Destroy()
            print("FILENAME='%s'" % fname)
            if(fname!=""):
                dest_file  = open(fname,'w')
            else:
                dest_file = None
        else:
            dest_file = None

        self.layout_data = {}
        self.layout_data['bg_image'] = 'playfield.jpg'
        window_size = self.GetClientSizeTuple()
        self.layout_data['window_size'] = {'width':window_size[0], 'height':window_size[1]}
        self.layout_data['button_locations'] = []

        for bID,btn in buttons.iteritems():
            (x,y) = btn.GetPositionTuple()
            btndata = {}
            btndata[bID]={'x':x, 'y':y}
            # btndata['x']=x 
            # btndata['y']=y
            self.layout_data['button_locations'].append(btndata)

        if(dest_file is not None):
            yaml.dump(self.layout_data, stream=dest_file, default_flow_style=False)
        else:
            print(yaml.dump(self.layout_data, default_flow_style=False))

    def loadLayoutInfo(self, event):
        self.layout_data = yaml.load(file(options['layout_file']))
        
        #self.bg_image = self.layout_data['bg_image']
        print(self.layout_data)
        print("w=%d, h=%d" % (self.layout_data['window_size']['width'], self.layout_data['window_size']['height']))
        self.SetClientSizeWH(self.layout_data['window_size']['width'], self.layout_data['window_size']['height'])
        
        # self.layout_data['button_locations'] = []

##############################################
# main()
##############################################

def main():
        # make the GUI components
        app = wx.App(redirect=False)
        frame = MyFrame(None, -1, 'OSC Switch Matrix for PyProcGame', pos=wx.DefaultPosition, size=wx.Size(600,400))

        gs = wx.GridSizer(9, 8, 2, 2) # rows, cols, gap
        buttonMaker = ButtonMaker(frame)
 
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

        frame.PDB_switches = yaml_data['PRGame']['machineType'] == "pdb"
        if(frame.PDB_switches):
            print("Using PDB style switch numbering.  Trying to order switches...")
            for c in range(0,8):
                    for r in range(0,16):
                            switch_code = '%s/%s' % (c,r)
                            try:
                                sname = game_switches[switch_code]
                                button = buttonMaker.makeButton(sname, switches)
                                if(frame.graphical_mode is False):
                                    gs.Add(button, 0, wx.EXPAND)
                                else:
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, forced_frame=frame.newWin)
                                    gs.Add(buttonMV, 0, wx.EXPAND)

                                # remove the switch from the to-do list
                                del game_switches[switch_code]
                            except Exception, e:
                                print "Warning: didn't find a definition for switch at location (%d,%d)'" % (c,r)

        else:
            print("Using Williams/Stern style switch numbering.  Trying to order switches...")
            for r in range(0,8):
                    for c in range(0,8):
                            switch_code = 'S%s%s' % (c+1, r+1)
                            
                            if switch_code in game_switches:
                                sname = game_switches[switch_code]
                                button = buttonMaker.makeButton(sname, switches)
                                # remove the switch from the to-do list
                                del game_switches[switch_code]
                                if(frame.graphical_mode is False):
                                    gs.Add(button, 0, wx.EXPAND)
                                else:
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.newWin)
                                    gs.Add(buttonMV, 0, wx.EXPAND)
                            else:
                                print "Warning: didn't find a definition for switch at location (%d,%d)'" % (c+1,r+1)
                                # print e
                                sname = "N/A"
                                if(frame.graphical_mode is False):
                                    button = buttonMaker.makeButton(sname, switches,switch_code)
                                    gs.Add(button, 0, wx.EXPAND)
                                    button.Enabled = False
                                else:
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.newWin)
                                    buttonMV.Enabled = False
                                    gs.Add(buttonMV, 0, wx.EXPAND)
                                pass
        # go through the matrix trying to find switches from the yaml

        print "Adding remaining dedicated switches..."
        print game_switches

        # anything left in that dict wasn't in the matrix (i.e., a dedicated switch)

        for i in range(0,32):
            switch_code = "SD%s" % i
            if(switch_code in game_switches):
                sname = game_switches[switch_code]
                button = buttonMaker.makeButton(sname, switches)
                if(frame.graphical_mode is False):
                    gs.Add(button, 0, wx.EXPAND)
                else:
                    buttonMV = buttonMaker.makeGridButton(sname, switches, forced_frame=frame.newWin)
                    gs.Add(buttonMV, 0, wx.EXPAND)

        if(frame.graphical_mode is False):
            frame.SetSizer(gs)
        else:
            frame.newWin.SetSizer(gs)
        
        frame.Show()
        #wx.SetCursor(wx.CURSOR_BULLSEYE)
        frame.dumpLayoutInfo(None)
        app.MainLoop()

        # END main()

def find_key_in_list_of_dicts(key, list):
    found_item = next((tmpItem for tmpItem in list if key in tmpItem), None)
    return found_item

if __name__ == '__main__':
        main()
