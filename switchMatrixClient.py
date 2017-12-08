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
import socket
import threading
from optparse import OptionParser
import socket
import wx
import yaml
import random
import time
import sys
import math
from HelperControls import CheckListWindow, OrderedListPanel

try:
    if(wx.NullColor is None):
        wx.NullColor = wx.NullColour
except:
    wx.NullColor = wx.NullColour

states = {}
buttons = {}
dirty = False
lamps_dirty = False
frame = None
lamps_from_server = False
lamp_thread_wakeup = threading.Event()
server_ip = socket.gethostbyname(socket.gethostname())
parser = OptionParser()
lamp_delay = 16

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
                                    dest="yaml_file", default=None,
                                    help="The yaml file name for the machine definition.  Default is 'game.yaml' (if present).")

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

################# SERVER LAMP SUPPORT ################33

# def PromptForLampInfo(self):
#     dlg = LampProperties(self)
#     if dlg.ShowModal() == wx.ID_OK:
#         # save changes in lamp_list
#         pass


def my_message_receiver(addr, tags, data, client_address):
    """ receives OSC messages and acts on them by setting switches."""
    #print("recvd OSC message: " + str(addr) + str(data))
    # need to add supprt for "sync" instruction which we'll call when switching tabs in touchOSC
    global lamp_list
    global lamps_dirty

    msg = addr.split("/")
    if(msg[1] == "lamps"):
        if(msg[2] in lamp_list):
            #print data
            # print msg[2]
            # print data
            # print lamp_list[msg[2]].color_on
            if len(data)==3:  #RGB DATA
                if data==[0,0,0]:
                    lamp_list[msg[2]].color= lamp_list[msg[2]].color_off
                else:
                    lamp_list[msg[2]].color = (data[0],data[1], data[2])
            else:
                if(int(data[0]) == 1):
                    lamp_list[msg[2]].color = lamp_list[msg[2]].color_on
                else:
                    lamp_list[msg[2]].color = lamp_list[msg[2]].color_off
        else:
            print("Lamp '%s' not found in list" % msg[2] )
        lamps_dirty = True
    else:
        #strip out the switch name
        switchname = addr.split("/")[-1]  # This is the OSC address, not the IP address. Strip out the characters after the final "/"


running = True

local_ip = socket.gethostbyname(socket.gethostname())
receive_address = (local_ip, 8000)  # create a tuple from the IP & UDP port
server = OSC.OSCServer(receive_address)
server.addDefaultHandlers()
server.addMsgHandler("default", my_message_receiver)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()


################# SERVER LAMP SUPPORT ################33

def lamp_updater():
    global lamps_dirty
    global frame
    print("Lamp Updater thread initialized.")
    while(running):
        lamp_thread_wakeup.wait()
        if(lamps_dirty):
            frame.doRefresh()
            #print("------------LAMP UPDATER Req Refresh--------------------")
        sendOSCLampReq(None)
        #print("------------LAMP UPDATER Snding Lamp Req--------------------")
        time.sleep(1.0/lamp_delay)
        #print("sleeping for %f" % (1.0/lamp_delay) )
    print("Lamp Updater thread done.")

lamp_thread = threading.Thread(target=lamp_updater)

def sendOSCLampReq(event):
        addr = '/lamps/get'
        osc_msg = OSC.OSCMessage(addr)
        #print("SENDING: %s" % str(osc_msg))
        osc_client.send(osc_msg)

def sendOSC(evt_src, new_state=None):
        btn = evt_src.EventObject
        addr = '/sw/%s' % btn.id
        # addr = '/sw/%s' % btn.GetLabel()
        osc_msg = OSC.OSCMessage(addr)
        if(states[btn.id]==False and new_state==True):
                btn.SetBackgroundColour(wx.GREEN)
                states[btn.id]=True
                osc_msg.append(1.0)
                print('%s %s' % (addr, 1) )
        elif(states[btn.id]==True and new_state==False):
                btn.SetBackgroundColour(wx.NullColor)
                states[btn.id]=False
                osc_msg.append(0.0)
                print('%s %s' % (addr, 0) )
        else:
                print("click ignored")
        osc_client.send(osc_msg)
        btn.ClearBackground()
        #sendOSCLampReq()


class GameLamp(object):
    def __init__(self, name, yaml_number, lamplocdata):
        ld = lamplocdata[name] if lamplocdata is not None else None
        if (ld is not None):
            y = ld['y']
            x = ld['x']
            on = ( ld['color_on']['r'] , ld['color_on']['g'], ld['color_on']['b'] )
            off = ( ld['color_off']['r'] , ld['color_off']['g'], ld['color_off']['b'] )
            hide = ld['hide'] if('hide' in ld) else False
        else:
            x = 0
            y = 0
            on = (0,255,255)
            off = (0,0,0)
            dirty = True
            hide = False
        self.name = name
        self.yaml_number = yaml_number
        self.x = x
        self.y = y
        self.color_on = on
        self.color_off = off
        self.color = off
        self.size = 10
        self.opacity = 128
        self.hidden = hide

    def getColorAsHex(self, r, g, b):
        return "%02x%02x%02x" % ((r,g,b))

    def off(self):
        self.color = self.color_off

    def on(self):
        self.color = self.color_on

    def setColor(self, r, g, b, opacity=128):
        self.color = (r, g, b, opacity)

    def getColor(self):
        return (r, g, b)

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

        hidden = False
        btnlocation = find_key_in_list_of_dicts(sname, self.frame.layout_data['button_locations'])
        if sname in switches and (btnlocation is not None):
            y = btnlocation[sname]['y']
            x = btnlocation[sname]['x']
            if('hide' in btnlocation[sname]):
                hidden = btnlocation[sname]['hide']
            pass
        else:
            x = int(self.buttonCounter/8)*25
            y = (self.buttonCounter%8)*20
            self.buttonCounter = self.buttonCounter+1
        #button = wx.Button(frame, pos=(x,y), size=(20,20), label='%s' % sname)
        button = wx.Button(self.frame, pos=(x,y), size=(25,20), label='%s' % number)

        button.SetWindowVariant(wx.WINDOW_VARIANT_MINI)

        button.SetToolTipString(lbl)

        button.hidden = hidden
        if(hidden):
            button.Hide()
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

    def onLampClick(self,event):
        btn = event.EventObject
        print "Lamp move '%s' requested!" % btn.id

        if(self.frame.layout_mode):
            self.frame.last_lamp_pressed = btn.id
            btn.SetBackgroundColour(wx.CYAN)
            self.frame.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
            print(self.frame.last_lamp_pressed)
        else:
            pass # not sure how someone would click a lamp when they aren't visible...


    def makeLampMoveButton(self, lname, lamps, number=None):
        if(number is None):
            number = lamps[lname].yaml_number

        lbl = lname

        button = wx.Button(self.frame.winLampLayoutPalette, label='%s\n%s' % (lname, number))

        button.SetToolTipString(lbl)
        button.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
        button.id = lname

        button.Bind(wx.EVT_LEFT_DOWN, self.onLampClick)

        return button


class DialogChangeLampRate(wx.Dialog):
    # http://zetcode.com/wxpython/dialogs/
    def __init__(self, *args, **kw):
        super(DialogChangeLampRate, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Set Lamp Update Rate")
        self.value = None

    def EvtRadioBox(self, event):
        print('EvtRadioBox: %d %s\n' % (event.GetInt(), event.GetString()))
        self.value = event.GetString()

    def InitUI(self):

        vbox = wx.BoxSizer(wx.VERTICAL)

        radioList = ['32','24','16','8','4']

        rb = wx.RadioBox(self, label="Lamp refresh rate (requests/second)", choices=radioList,  majorDimension=5, style=wx.RA_SPECIFY_ROWS)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)

        rb.SetSelection(radioList.index(str(lamp_delay)))
        self.value = rb.GetStringSelection()

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(rb, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2,
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnOK(self, e):
        global lamp_delay
        lamp_delay = int(self.value)
        self.Destroy()
        return wx.ID_OK

    def OnClose(self, e):
        self.Destroy()


class SelectItemsWindow(wx.Frame):
    def __init__(self,  parent, id=-1, title="",
            pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.DEFAULT_FRAME_STYLE, name=""):
        super(SelectItemsWindow,self).__init__(parent, id, title, pos, size, style, name)
        gs = wx.GridSizer(rows=1) # rows, cols, gap
        # add controls

        self.clb = wx.CheckListBox(self, -1, wx.DefaultPosition, wx.DefaultSize,
            choices=["a","b"],
            style=0,
            validator=wx.DefaultValidator,
            name="")
        self.Bind(wx.EVT_CHECKLISTBOX, self.onSelect)
        gs.Add(self.clb, 0, wx.EXPAND)
        self.SetSizer(gs)

    def onSelect(self, event):
        n = event.GetInt()
        print(n)
        print(self.clb.GetString(n))
        print(self.clb.IsChecked(n))

class MainWindow(wx.Frame):
    def __init__(self,  parent, id=-1, title="",
            pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.DEFAULT_FRAME_STYLE, name=""):
        super(MainWindow,self).__init__(parent, id, title, pos, size, style, name)

        self.lampCustomizer = CheckListWindow(self, ["A", "B", "C", "D", "E", "F"], ["B", "C", "D"], self.lampListCustomized, "Uncheck items to hide them")
        self.lampCustomizer.Show(False)

        self.switchCustomizer = CheckListWindow(self, ["A", "B", "C", "D", "E", "F"], ["B", "C", "D"], self.switchListCustomized, "Uncheck items to hide them")
        self.switchCustomizer.Show(False)

        self.RgbCustomizerWindow = OrderedListPanel(self, ["a"], self.makeRgbShow, self.addRgbFile, self.previewRgbFrame, "RGB Show")

        self.layout_mode = False
        self.graphical_mode = False
        self.layout_data = {}

        self.layout_data['button_locations'] = []
        self.layout_data['lamp_locations'] = []

        self.lamp_show_img = None

        if(options['layout_file'] is not None):
            self.graphical_mode = True
            self.loadLayoutInfo(None)
        elif(options['bg_image'] is not None):
            self.graphical_mode = True

        if(self.graphical_mode):
            self.initGraphicalMode()

        global yaml_data
        yaml_file_name = "game.yaml"
        if(options['yaml_file'] is not None):
            yaml_file_name = options['yaml_file']
        elif('yaml_file' in self.layout_data):
            yaml_file_name = self.layout_data['yaml_file']
        else: # no layout data...
            parser.print_help()
            print "Failed to find yaml file parameter or in layout file; trying default 'game.yaml'"
        try:
            yaml_data = yaml.load(open(yaml_file_name, 'r'))
        except Exception, e:
            print "Failed to load machine yaml file '%s' file was missing or invalid." % yaml_file_name
            kill_threads()
            raise
        self.layout_data['yaml_file'] = yaml_file_name

    def initGraphicalMode(self):
        if(options['bg_image'] is not None):
            # use this first
            bgfile = options['bg_image']
            self.layout_data['bg_image'] = options['bg_image']
        elif('bg_image' in self.layout_data):
            bgfile = self.layout_data['bg_image']
        else:
            # why are we adding an image when none exists!?
            raise ValueError("Trying to add an image but the program is not in graphical mode!?")

        self.bmp = wx.Bitmap(bgfile)
        # self.SetClientSizeWH(self.bmp.GetWidth(), self.bmp.GetHeight())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackgroundDummy)
        self.Bind(wx.EVT_PAINT, self.OnEraseBackground)

        self.Bind(wx.EVT_LEFT_DOWN, self.LeftButtonDOWN)
        self.Bind(wx.EVT_RIGHT_DOWN, self.RightButtonDOWN)
        # more features to come...
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        editMenu = wx.Menu()
        viewMenu = wx.Menu()
        lampMenu = wx.Menu()

        mnuSave = fileMenu.Append(wx.NewId(), "Save Layout",
                                       "Saves the layout")

        mnuLEDexport = lampMenu.Append(wx.NewId(), "Export LED MAP",
                                       "Exports a LED Map")

        mnuLampshowTemplateExport = lampMenu.Append(wx.NewId(), "Export blank lampshow template",
                                       "Exports blank lampshow")

        mnuRgbShowExport = lampMenu.Append(wx.NewId(), "Create an RGB Show (experimental!)",
                                       "Create RGB Show")

        mnuExit = fileMenu.Append(wx.NewId(), "Exit",
                                       "Exit the application")

        mnuWhichLamps = viewMenu.Append( wx.NewId(), "Hide/Show Specific Lamps", "Customize which lamps are shown/hidden")
        mnuWhichSwitches  = viewMenu.Append( wx.NewId(), "Hide/Show Specific Switches", "Customize which switches are shown/hidden")

        mnuScaleSwitchesX = editMenu.Append( wx.NewId(), "Scale switch/lamp locations horizontally", "scale switch/lamp locations horizontally")
        mnuScaleSwitchesY = editMenu.Append( wx.NewId(), "Scale switch/lamp locations vertically", "scale switch/lamp locations vertically")


        self.Bind(wx.EVT_MENU, self.scaleX, mnuScaleSwitchesX)
        self.Bind(wx.EVT_MENU, self.scaleY, mnuScaleSwitchesY)

        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(lampMenu, "&Lampshows")
        menuBar.Append(viewMenu, "&View")

        #oadLayoutMenu = wx.Menu()
        #self.Bind(wx.EVT_MENU, self.loadImage, loadImageMenu)
        self.Bind(wx.EVT_MENU, self.dumpLayoutInfo, mnuSave)

        self.Bind(wx.EVT_MENU, self.exportRgbShow, mnuRgbShowExport)

        self.Bind(wx.EVT_MENU, self.dumpLEDMap, mnuLEDexport)
        self.Bind(wx.EVT_MENU, self.dumpLampShowTemplate, mnuLampshowTemplateExport)

        self.Bind(wx.EVT_MENU, self.toggleLamps, mnuWhichLamps)
        self.Bind(wx.EVT_MENU, self.toggleSwitches, mnuWhichSwitches)

        self.Bind(wx.EVT_MENU, self.OnCloseFrame, mnuExit)

        self.toggleLayoutMode = editMenu.Append(wx.NewId(), 'Layout Mode',
            'Right click switches to move them', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleEditMode, self.toggleLayoutMode)

        editMenu.Check(self.toggleLayoutMode.GetId(), False)

        self.toggleLampRender = viewMenu.Append(wx.NewId(), 'Update Lamps',
            'Periodically sends requests for lamp info to the OSC server', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleLampOSC, self.toggleLampRender)

        viewMenu.Check(self.toggleLampRender.GetId(), False)

        self.toggleStatusBar = viewMenu.Append(wx.NewId(), 'Show Status Bar',
            'Show the status bar', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, self.toggleStatusBar)
        viewMenu.Check(self.toggleStatusBar.GetId(), True)


        lampRateMenuItem = viewMenu.Append(wx.NewId(), "Change Lamp update rate",
                                       "Adjust the lamp refresh rate")
        self.Bind(wx.EVT_MENU, self.PromptForLampRate, lampRateMenuItem)

        self.status_bar = self.CreateStatusBar()

        self.SetMenuBar(menuBar)
        if(self.graphical_mode):
            self.winButtonLayoutPalette = wx.Frame(None, -1,'Switch Layout Pallete (click to place)', size=(400,300))
            self.winButtonLayoutPalette.Show(False)
            self.winButtonLayoutPalette.Bind(wx.EVT_CLOSE, self.hideSubWin)

            self.winLampLayoutPalette = wx.Frame(None, -1,'Lamp Layout Pallete (click to place)', size=(400,300))
            self.winLampLayoutPalette.Show(False)
            self.winLampLayoutPalette.Bind(wx.EVT_CLOSE, self.hideSubWin)

        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        self.updateStatusBar()

    def scaleX(self, event):
        dlg = wx.TextEntryDialog(self, "adjust on X axis", "100%")
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()

        if(result.endswith("%")):
            result = float(result[0:-1])/100

            for lamp in lamp_list.values():
                lamp.x = lamp.x * result
            # for switch in buttons.values():
            #     switch.x = switch.x * result
        else:
            result = int(result)
            for lamp in lamp_list.values():
                lamp.x = lamp.x + result
            # for switch in buttons.values():
            #     switch.x = switch.x + result

        self.doRefresh()

    def scaleY(self, event):
        dlg = wx.TextEntryDialog(self, "adjust on Y axis", "100%")
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()

        if(result.endswith("%")):
            result = float(result[0:-1])/100
            for lamp in lamp_list.values():
                lamp.y = lamp.y * result
            # for switch in buttons.values():
            #     switch.y = switch.y * result
        else:
            result = int(result)
            for lamp in lamp_list.values():
                lamp.y = lamp.y + result
            # for switch in buttons.values():
            #     switch.y = switch.y + result

        self.doRefresh()


    def lampListCustomized(self, selected_items):
        """ this is the method called when the switch/lamp list customization is complete """
        global lamp_list
        if(selected_items is None):
            return

        for i,l in lamp_list.iteritems():
            if(l.name in selected_items):
                lamp_list[i].hidden = False
                # print("show %s" % lamp_list[i].name)
            else:
                lamp_list[i].hidden = True
                # print("hide %s" % lamp_list[i].name)
        self.doRefresh()
        pass

    def switchListCustomized(self, selected_items):
        """ this is the method called when the switch/lamp list customization is complete """
        global buttons
        if(selected_items is None):
            return

        for i,b in buttons.iteritems():
            if(b.id in selected_items):
                buttons[i].hidden = False
                buttons[i].Show()
            else:
                buttons[i].hidden = True
                buttons[i].Hide()
                # print("hide %s" % lamp_list[i].name)
        self.doRefresh()
        pass

    def toggleSwitches(self, event):
        global buttons
        all_buttons = [l for l in buttons.keys()]
        visible_buttons = [l.id for l in buttons.values() if not l.hidden]

        self.switchCustomizer.SetLists(all_buttons, visible_buttons)
        self.switchCustomizer.Show(True)
        pass

    def toggleLamps(self, event):
        global lamp_list
        all_lamps = [l.name for l in lamp_list.values()]
        visible_lamps = [l.name for l in lamp_list.values() if not l.hidden]

        self.lampCustomizer.SetLists(all_lamps, visible_lamps)
        self.lampCustomizer.Show(True)
        pass

    def exportRgbShow(self, event):
        if(event is None):
            return

        frame_files = None
        loadFileDialog = wx.FileDialog(self, "Open images", "", "",
                                      "Image sequence (*.png)|*.png",
                                      wx.FD_OPEN | wx.FD_MULTIPLE )
        loadFileDialog.ShowModal()
        frame_files = loadFileDialog.GetPaths()
        loadFileDialog.Destroy()
        # print("frame_files='%s'" % frame_files)

        if(frame_files is None):
            return

        self.RgbCustomizerWindow.SetList(frame_files)
        self.RgbCustomizerWindow.Show(True)

    def addRgbFile(self):
        frame_files = None
        loadFileDialog = wx.FileDialog(self, "Open images", "", "",
                                      "Image sequence (*.png)|*.png",
                                      wx.FD_OPEN | wx.FD_MULTIPLE )
        loadFileDialog.ShowModal()
        frame_files = loadFileDialog.GetPaths()
        loadFileDialog.Destroy()
        # print("frame_files='%s'" % frame_files)

        return frame_files

    def previewRgbFrame(self, fname, scale_to_playfield=False):
        global lamp_list
        bmp = wx.Bitmap(fname)
        img = bmp.ConvertToImage()

        if(scale_to_playfield):
            (w,h) = (self.bmp.GetWidth(), self.bmp.GetHeight())
            img.Rescale(w, h, wx.IMAGE_QUALITY_NEAREST)
            bmp = wx.BitmapFromImage(img)

        (w,h) = (bmp.GetWidth(), bmp.GetHeight())
        self.lamp_show_img = bmp

        # img = None
        # wx.Quantize.Quantize(img, img, 64)

        for i,lamp in lamp_list.iteritems():
            (x,y) = lamp_list[i].x, lamp_list[i].y
            if (x < w and y < h):
                r = img.GetRed(x,y)
                g = img.GetGreen(x,y)
                b = img.GetBlue(x,y)
            else:
                r = 0
                g = 0
                b = 0

            lamp_list[i].setColor(r, g, b, 255 )

        self.doRefresh()



    def makeRgbShow(self, frame_list, scale_to_playfield=False):
        # print("done")

        self.lamp_show_img = None
        self.doRefresh()

        if(frame_list is None):
            return

        saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                      "RgbShow file (*.rgbshow)|*.rgbshow",
                                      wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        saveFileDialog.ShowModal()
        fname = saveFileDialog.GetPath()
        saveFileDialog.Destroy()

        # print("FILENAME='%s'" % fname)
        if(fname!=""):
            dest_file  = open(fname,'w')
        else:
            dest_file = None

        if(dest_file is None):
            return

        global lamp_list

        # frame_files = [fname]
        color_map = {}
        lamp_sequences = {}

        # list of frames
        for lamp in lamp_list:
            lamp_sequences[lamp] = []

        # for every frame in the animation
        for fname in frame_list:
            bmp = wx.Bitmap(fname)
            img = bmp.ConvertToImage()

            if(scale_to_playfield):
                (w,h) = (self.bmp.GetWidth(), self.bmp.GetHeight())
                img.Rescale(w, h, wx.IMAGE_QUALITY_NEAREST)
                bmp = wx.BitmapFromImage(img)
            else:
                (w,h) = (bmp.GetWidth(), bmp.GetHeight())

            for i,lamp in lamp_list.iteritems():
                (x,y) = lamp_list[i].x, lamp_list[i].y

                if (x < w and y < h):
                    r = img.GetRed(x,y)
                    g = img.GetGreen(x,y)
                    b = img.GetBlue(x,y)
                else:
                    r = 0
                    g = 0
                    b = 0

                lamp_list[i].off()
                hex_color = lamp_list[i].getColorAsHex(r,g,b)

                color_char = "_"
                if(hex_color not in color_map):
                    map_size = len(color_map.keys())
                    if(map_size < 26):
                        color_char = chr(map_size + ord("A"))
                    elif(map_size < 52):
                        color_char = chr(map_size-26 + ord("a"))
                    elif(map_size < 62):
                        color_char = chr(map_size-52 + ord("0"))
                    else:
                        dialog = wx.MessageDialog(self, message = "The frame sequence has too many unique colors\n in it for the current (indexed) color model supported by this tool.", caption = "Generation Problem", style = wx.OK | wx.ICON_EXCLAMATION, pos = wx.DefaultPosition)
                        return
                    color_map[hex_color] = color_char
                    # print("mapping %s %s" % (color_char, hex_color))
                else:
                    color_char = color_map[hex_color]

                lamp_sequences[lamp_list[i].name].append(color_char)

        # store the sequence file:
        dest_file.write("##############################\n\
# Generated RgbShow file\n\
##############################\n\
# => defines a color to change immediately (on first occurance)\n\
# ~> defines a fade into color --fade will be completed on the LAST occurance\n\
##############################\n\
# COLOR MAP:\n\
##############################\n");
        for (k,v) in color_map.iteritems():
            dest_file.write("! %s => %s\n" % (v, k))
        dest_file.write("###########################################\n")
        for (k,v) in lamp_sequences.iteritems():
            dest_file.write("%25s | %s\n" % (k,"".join(v)))
        dest_file.write("###########################################\n")
        dest_file.close()
        self.doRefresh()

    def hideSubWin(self, event):
        self.winButtonLayoutPalette.Show(False)
        self.winLampLayoutPalette.Show(False)
        event.StopPropagation()

    #----------------------------------------------------------------------
    # Destroys the main frame which quits the wxPython application
    def OnExitApp(self, event):
        if(self.graphical_mode):
            self.winButtonLayoutPalette.Destroy()
            self.winLampLayoutPalette.Destroy()
        self.Destroy()

        """Shuts down the OSC Server thread. If you don't do this python will hang when you exit the game."""
        server.close()
        print("Waiting for the OSC Server thread to finish")
        server_thread.join()
        print("OSC Server thread is done.")
        global running
        running = False
        lamp_thread_wakeup.set()
        lamp_thread.join()


    # Makes sure the user was intending to quit the application
    def OnCloseFrame(self, event):
        if(dirty):
            dialog = wx.MessageDialog(self, message = "Are you sure you want to quit?", caption = "Quit?", style = wx.YES_NO, pos = wx.DefaultPosition)
            response = dialog.ShowModal()

            if (response == wx.ID_YES):
                self.OnExitApp(event)
            else:
                event.StopPropagation()
        else:
            self.OnExitApp(event)

    def RightButtonDOWN(self, event):
        (x,y) = event.GetPositionTuple()
        print("right click at (%d,%d)" % (x,y))

    def __getDistance(self, x1, y1, x2, y2):
        dx = math.pow(x2-x1, 2)
        dy = math.pow(y2-y1, 2)
        return math.sqrt(dx+dy)

    def LeftButtonDOWN(self, event):
        global dirty
        global lamp_list
        if(self.layout_mode and self.last_button_pressed_id is not None):
            dirty = True
            (x,y) = event.GetPositionTuple()
            bTmp = buttons[self.last_button_pressed_id]
            try:
                (w,h) = bTmp.GetClientSizeTuple()
            except Exception, e:
                (w,h) = bTmp.GetClientSize()

            x = x - w/2
            y = y - h/2
            bTmp.MoveXY(x,y)
            bTmp.SetBackgroundColour(wx.NullColor)
            print("moved %s to (%d,%d)" % (self.last_button_pressed_id,x,y))
            bTmp = None
            self.last_button_pressed_id = None
            # self.SetCursor(wx.StockCursor(wx.CURSOR_STANDARD))

            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        elif(self.layout_mode and self.last_lamp_pressed is not None):
            dirty = True
            (x,y) = event.GetPositionTuple()
            # (w,h) = bTmp.GetClientSizeTuple()
            # x = x - w/2
            # y = y - h/2
            lamp_list[self.last_lamp_pressed].x = x
            lamp_list[self.last_lamp_pressed].y = y
            # bTmp.SetBackgroundColour(wx.NullColor)
            print("moved %s to (%d,%d)" % (self.last_lamp_pressed,x,y))
            self.last_lamp_pressed = None
            # self.SetCursor(wx.StockCursor(wx.CURSOR_STANDARD))

            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            self.doRefresh()
        elif(self.layout_mode):
            # search and see if click is inside a lamp
            closest_lamp = None
            min_distance = 1000
            (ex,ey) = event.GetPositionTuple()

            for l in lamp_list.values():
                 d = self.__getDistance(ex,ey,l.x, l.y)
                 if(d < min_distance):
                    closest_lamp = l
                    min_distance = d
            print("closest lamp to click was: %s" % closest_lamp.name)

    def doRefresh(self):
        global lamps_dirty
        #print "Refresh!!!"
        try:
            (w,h) = self.GetClientSizeTuple()
        except Exception, e:
            (w,h) = self.GetClientSize()
        self.RefreshRect(rect=(0,0,w,h), eraseBackground=True)
        lamps_dirty = False

    def updateStatusBar(self):
        if(self.layout_mode == True):
            self.status_bar.SetStatusText("Layout Mode")
        else:
            if(self.toggleLampRender.IsChecked()):
                global lamp_delay
                self.status_bar.SetStatusText("Interactive Mode  / Lamp Updates ON / %dfps" % lamp_delay)
            else:
                self.status_bar.SetStatusText("Interactive Mode  / Lamp Updates OFF ")

    def ToggleStatusBar(self, state):
        if(self.toggleStatusBar.IsChecked()):
            self.status_bar.Show()
        else:
            self.status_bar.Hide()

    def ToggleEditMode(self, state):
        self.layout_mode = self.toggleLayoutMode.IsChecked()
        self.last_button_pressed_id = None
        self.last_lamp_pressed = None

        if(self.layout_mode == True):
            self.winButtonLayoutPalette.Show(True)
            self.winLampLayoutPalette.Show(True)
            wx.Frame.CenterOnScreen(self.winButtonLayoutPalette)
        else:
            self.winLampLayoutPalette.Show(False)
            self.winButtonLayoutPalette.Show(False)
        pass
        self.updateStatusBar()

    def ToggleLampOSC(self, state):
        global lamps_from_server
        global running
        lamps_from_server = self.toggleLampRender.IsChecked()
        if(lamps_from_server):
            print("starting")
            lamp_thread_wakeup.set()
        else:
            print("pausing")
            lamp_thread_wakeup.clear()
        self.updateStatusBar()

    def PromptForLampRate(self, evt):
        dLampRate = DialogChangeLampRate(None)
        dLampRate.ShowModal()
        dLampRate.Destroy()
        self.updateStatusBar()

    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        #print("PAINT:")
        # yanked from ColourDB.py
        global lamp_list
        #dc = evt.GetDC()
        dc = wx.BufferedPaintDC(self)
        dc = wx.GCDC(dc)

        # if not dc:
        #     dc = wx.ClientDC(self)
        #     rect = self.GetUpdateRegion().GetBox()
        #     dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.bmp, 0, 0)

        if(self.lamp_show_img is not None):
            dc.DrawBitmap(self.lamp_show_img, 0, 0)

        # alpha does NOT work on windows... blah.
        for n,lamp in lamp_list.iteritems():
            # print("Drawing lamp '%s' at (%d,%d) in color (%s)" % (lamp.name, lamp.x, lamp.y, lamp.color))
            if(not lamp.hidden):
                dc.SetBrush(wx.Brush(wx.Colour(lamp.color[0],lamp.color[1],lamp.color[2],lamp.opacity)))
                dc.SetPen(wx.Pen(wx.Colour(255,255,192), 1, wx.SOLID))
                dc.DrawCircle(lamp.x, lamp.y, lamp.size)


    def OnEraseBackgroundDummy(self, event):
        """ Handles the wx.EVT_ERASE_BACKGROUND event for CustomCheckBox. """

        # This is intentionally empty, because we are using the combination
        # of wx.BufferedPaintDC + an empty OnEraseBackground event to
        # reduce flicker
        pass

    def dumpLEDMap(self, event):
        if(event is not None):
            saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                          "LEDMap file (*.txt)|*.txt",
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

        if(dest_file is None):
            return

        # led_map_file['bg_image'] = 'playfield.jpg'
        my_img_size = self.bmp.GetSize()

        print("image size: %f, %f" % (my_img_size.x, my_img_size.y))

        #print("KNOWN LAMP COUNT %d" % len(lamp_list))
        for idx,(lamp_id,lamp) in enumerate(lamp_list.iteritems()):
            if(lamp.hidden):
                continue

            # convert the location
            scaled_x = float(lamp.x) / my_img_size.x
            scaled_y = float(lamp.y) / my_img_size.y

            x = scaled_x * float(250)#219)
            y = scaled_y * float(505) + 25 #498)

            sLine = "%6s = %03d %03d %s\n" % ("led_" + str(idx), x, y, "-"*64)
            print(sLine)

            dest_file.write(sLine)

        dest_file.close()


    def dumpLayoutInfo(self, event):
        if(event is not None):
            saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                          "Layout files (*.layout)|*.layout",
                                          wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            saveFileDialog.ShowModal()
            fname = saveFileDialog.GetPath()
            saveFileDialog.Destroy()
            print("Saving to filename '%s'" % fname)
            if(fname!=""):
                dest_file  = open(fname,'w')
            else:
                dest_file = None
        else:
            dest_file = None
        window_size = None
        try:
            window_size = self.GetClientSizeTuple()
        except Exception, e:
            window_size = self.GetClientSize()

        self.layout_data['window_size'] = {'width':window_size[0], 'height':window_size[1]}
        self.layout_data['window_pos'] = {'x':self.GetPositionTuple()[0], 'y':self.GetPositionTuple()[1]}
        self.layout_data['button_locations'] = []
        self.layout_data['lamp_locations'] = []

        for bID,btn in buttons.iteritems():
            (x,y) = btn.GetPositionTuple()
            btndata = {}
            btndata[bID]={'x':x, 'y':y, 'hide':btn.hidden}

            # btndata['x']=x
            # btndata['y']=y
            self.layout_data['button_locations'].append(btndata)

        #print("KNOWN LAMP COUNT %d" % len(lamp_list))
        for lID,lamp in lamp_list.iteritems():
            lampdata = {}
            lampdata[lID]={'x':lamp.x, 'y':lamp.y, 'color_off':{'r':lamp.color_off[0], 'g':lamp.color_off[1],'b':lamp.color_off[2]}, 'color_on':{'r':lamp.color_on[0], 'g':lamp.color_on[1],'b':lamp.color_on[2]}, 'hide':lamp.hidden}
            # btndata['x']=x
            # btndata['y']=y
            self.layout_data['lamp_locations'].append(lampdata)

        if(dest_file is not None):
            yaml.dump(self.layout_data, stream=dest_file, default_flow_style=False)
        else:
            pass
            # print(yaml.dump(self.layout_data, default_flow_style=False))
        global dirty
        dirty = False


    def loadLayoutInfo(self, event):
        self.layout_data = yaml.load(file(options['layout_file']))

        #self.bg_image = self.layout_data['bg_image']
        #print(self.layout_data)
        #print("w=%d, h=%d" % (self.layout_data['window_size']['width'], self.layout_data['window_size']['height']))
        try:
            self.SetClientSizeWH(self.layout_data['window_size']['width'], self.layout_data['window_size']['height'])
        except Exception, e:
            self.SetClientSize(self.layout_data['window_size']['width'], self.layout_data['window_size']['height'])

        window_pos = (0,0)
        if 'window_pos' in self.layout_data: window_pos = self.layout_data['window_pos']
        if(isinstance(window_pos,tuple)):
            self.SetPosition(window_pos)
        else:
            self.SetPosition((window_pos['x'],window_pos['y']))
        global dirty
        dirty = False
        # self.layout_data['button_locations'] = []

    def dumpLampShowTemplate(self, event):
        if(event is not None):
            saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                          "Lampshow file (*.lampshow)|*.lampshow",
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

        if(dest_file is None):
            return

        dest_file.write("##############################################################################################################\n\
# Lightshow: attract_show_1\n\
# Type: simple\n\
# Length: 64 frames / 2 seconds\n\
##############################################################################################################\n\
# Markers:                                  |        8      16      24      32      40      48      56      64\n\
# Frames:                                   | 1234567812345678123456781234567812345678123456781234567812345678\n")

        for idx,(lamp_id,lamp) in enumerate(lamp_list.iteritems()):
            if(lamp.hidden):
                continue
            sLamp = "lamp:%s" % lamp_id
            sLine = sLamp + ' '*(44-len(sLamp)) + '|\n'
            dest_file.write(sLine)

        dest_file.close()


##############################################
# main()
##############################################

def main():
        global lamp_list
        global dirty

        global yaml_data
        yaml_data = {}
        lamp_list = {}

        # make the GUI components
        app = wx.App(redirect=False)
        global frame
        frame = MainWindow(None, -1, 'PyProcGame GUI Tool', pos=wx.DefaultPosition, size=wx.Size(600,400))

        gs = wx.GridSizer(9) # rows, cols, gap
        gsLamps = wx.GridSizer(9)
        buttonMaker = ButtonMaker(frame)

        # hold all the switches so we can know which
        # ones are outside the matrix
        game_switches = {}
        game_lamps = {}

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
            raise

        if 'PRLamps' in yaml_data:
            lamps = yaml_data['PRLamps']

            for name in lamps:
                item_dict = lamps[name]
                yaml_number = str(item_dict['number'])

                game_lamps[yaml_number] = name

                lamplocation = find_key_in_list_of_dicts(name, frame.layout_data['lamp_locations'])
                lamp = GameLamp(name, yaml_number, lamplocation)
                lamp_list[name] = lamp

        if 'WsRGBs' in yaml_data:
            lamps = yaml_data['WsRGBs']

            for name in lamps:
                item_dict = lamps[name]
                yaml_number = str(item_dict['number'])

                game_lamps[yaml_number] = name

                lamplocation = find_key_in_list_of_dicts(name, frame.layout_data['lamp_locations'])
                lamp = GameLamp(name, yaml_number, lamplocation)
                lamp_list[name] = lamp

        if 'PRLEDs' in yaml_data:
            lamps = yaml_data['PRLEDs']

            for name in lamps:
                item_dict = lamps[name]
                yaml_number = str(item_dict['number'])

                game_lamps[yaml_number] = name

                lamplocation = find_key_in_list_of_dicts(name, frame.layout_data['lamp_locations'])
                lamp = GameLamp(name, yaml_number, lamplocation)
                lamp_list[name] = lamp

        if(len(lamp_list)==0):
            print("PRLamps, PRLEDS, wsRGBs section(s) NOT found in specified yaml file '%s'.\nExiting..." % options['yaml_file'])
            print "----"
            raise
        print("PROCESSED %d LAMPS" % len(lamp_list))

        if(frame.graphical_mode is True):
            for r in range(0,8):
                for c in range(0,8):
                    lamp_code = 'L%s%s' % (c+1, r+1)

                    if lamp_code in game_lamps:
                        sname = game_lamps.pop(lamp_code)
                        bL = buttonMaker.makeLampMoveButton(sname, lamp_list)
                    else:
                        sname = "N/A"
                        bL = buttonMaker.makeLampMoveButton(sname, lamp_list, lamp_code)
                        bL.Enabled = False

                    gsLamps.Add(bL, 0, wx.EXPAND)

            for lRemaining in game_lamps.iteritems():
                bL = buttonMaker.makeLampMoveButton(lRemaining[1], lamp_list, lRemaining[0])
                gsLamps.Add(bL, 0, wx.EXPAND)

            # print("learning lamp '%s' at (%d,%d) in color (%s)" % (lamp.name, lamp.x, lamp.y, lamp.color))


        frame.switch_style = yaml_data['PRGame']['machineType']
        if(frame.switch_style == "pdb"):
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
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, forced_frame=frame.winButtonLayoutPalette)
                                    gs.Add(buttonMV, 0, wx.EXPAND)

                                # remove the switch from the to-do list
                                del game_switches[switch_code]
                            except Exception, e:
                                print "Warning: didn't find a definition for switch at location (%d,%d)'" % (c,r)

        elif(frame.switch_style == "sternSAM"):
            print("Using SternSAM style switch numbering.  Trying to order switches...")
            for r in range(0,64):
                switch_code = 'S%02d' % r

                if switch_code in game_switches:
                    sname = game_switches[switch_code]
                    button = buttonMaker.makeButton(sname, switches)
                    # remove the switch from the to-do list
                    del game_switches[switch_code]
                    if(frame.graphical_mode is False):
                        gs.Add(button, 0, wx.EXPAND)
                    else:
                        buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.winButtonLayoutPalette)
                        gs.Add(buttonMV, 0, wx.EXPAND)
                else:
                    print "Warning: didn't find a definition for switch at location (%s)'" % switch_code
                    # print e
                    sname = "N/A"
                    if(frame.graphical_mode is False):
                        button = buttonMaker.makeButton(sname, switches,switch_code)
                        gs.Add(button, 0, wx.EXPAND)
                        button.Enabled = False
                    else:
                        buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.winButtonLayoutPalette)
                        buttonMV.Enabled = False
                        gs.Add(buttonMV, 0, wx.EXPAND)
                    pass
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
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.winButtonLayoutPalette)
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
                                    buttonMV = buttonMaker.makeGridButton(sname, switches, switch_code, forced_frame=frame.winButtonLayoutPalette)
                                    buttonMV.Enabled = False
                                    gs.Add(buttonMV, 0, wx.EXPAND)
                                pass
        # go through the matrix trying to find switches from the yaml

        print "Adding remaining dedicated switches..."
        print game_switches

        # anything left in that dict wasn't in the matrix (i.e., a dedicated switch)

        for i in range(0,80):
            switch_code = "SD%s" % i
            if(switch_code in game_switches):
                sname = game_switches[switch_code]
                button = buttonMaker.makeButton(sname, switches)
                if(frame.graphical_mode is False):
                    gs.Add(button, 0, wx.EXPAND)
                else:
                    buttonMV = buttonMaker.makeGridButton(sname, switches, forced_frame=frame.winButtonLayoutPalette)
                    gs.Add(buttonMV, 0, wx.EXPAND)

        if(frame.graphical_mode is False):
            frame.SetSizer(gs)
        else:
            frame.winButtonLayoutPalette.SetSizer(gs)
            frame.winLampLayoutPalette.SetSizer(gsLamps)

        # button = wx.Button(frame, pos=(200,200), size=(40,20), label='GET LAMPS')
        # button.SetWindowVariant(wx.WINDOW_VARIANT_MINI)
        # button.Bind(wx.EVT_LEFT_DOWN, sendOSCLampReq)

        running = True
        lamp_thread.start()

        frame.Show()
        #wx.SetCursor(wx.CURSOR_BULLSEYE)
        frame.dumpLayoutInfo(None)
        app.MainLoop()
        # END main()

def find_key_in_list_of_dicts(key, list):
    found_item = next((tmpItem for tmpItem in list if key in tmpItem), None)
    return found_item

def kill_threads():
    """Shuts down the OSC Server thread. If you don't do this python will hang when you exit the game."""
    server.close()
    # print("Waiting for the OSC Server thread to finish")
    try:
        server_thread.join()
    except Exception, eT:
        pass

    running = False
    lamp_thread_wakeup.set()

    try:
        lamp_thread.join()
    except Exception, eT:
        pass


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print "Exception encountered: %s" % str(e)
        # backup the exception info...
        exc_info = sys.exc_info()

        kill_threads()

        raise exc_info[0], exc_info[1], exc_info[2]
