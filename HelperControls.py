#!/usr/bin/python
# 
# Copyright (c) 2017 Michael Ocean
#
# Licence: The MIT License (MIT)
#
# Written by Michael Ocean 
#   Some reusable classes to make common GUI tasks easier in wxPython 
#   (http://www.wxpython.org/download.php) 
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

import os
import sys
import wx

class OrderedListPanel(wx.Panel):
    def __init__(self, parent, contents, callback_fn, insert_callback, preview_cb, title=""):
        self.frame = wx.Frame(parent, -1, title, wx.DefaultPosition, (400, 400))

        super(OrderedListPanel, self).__init__(self.frame, -1, wx.DefaultPosition, wx.DefaultSize)

        self.cb_fn = callback_fn
        self.insert_cb = insert_callback
        self.contents = contents
        self.preview_cb = preview_cb

        h = 40

        b = 5
        w = 50
        # lblSizeX = wx.StaticText(self, -1, 'width:', (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        # txtSizeX = wx.TextCtrl(self, -1, '', (-1, -1), (-1, -1))
        # sizerXSize = wx.BoxSizer(wx.HORIZONTAL)
        # sizerXSize.Add(lblSizeX, 0, wx.RIGHT, b)
        # sizerXSize.Add(txtSizeX, 1, wx.GROW, b)
        # sizerXSize.SetItemMinSize(lblSizeX, (w, -1))

        # lblSizeY = wx.StaticText(self, -1, 'height:', (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        # txtSizeY = wx.TextCtrl(self, -1, '', (-1, -1), (-1, -1))
        # sizerYSize = wx.BoxSizer(wx.HORIZONTAL)
        # sizerYSize.Add(lblSizeY, 0, wx.RIGHT, b)
        # sizerYSize.Add(txtSizeY, 1, wx.GROW, b)
        # sizerYSize.SetItemMinSize(lblSizeY, (w, -1))

        # lblOffsetX = wx.StaticText(self, -1, 'x-offset:', (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        # txtOffsetX = wx.TextCtrl(self, -1, '', (-1, -1), (-1, -1))
        # sizerOffsetX = wx.BoxSizer(wx.HORIZONTAL)
        # sizerOffsetX.Add(lblOffsetX, 0, wx.RIGHT, b)
        # sizerOffsetX.Add(txtOffsetX, 1, wx.GROW, b)
        # sizerOffsetX.SetItemMinSize(lblOffsetX, (w, -1))

        # lblOffsetY = wx.StaticText(self, -1, 'y-offset:', (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        # txtOffsetY = wx.TextCtrl(self, -1, '', (-1, -1), (-1, -1))
        # sizerOffsetY = wx.BoxSizer(wx.HORIZONTAL)
        # sizerOffsetY.Add(lblOffsetY, 0, wx.RIGHT, b)
        # sizerOffsetY.Add(txtOffsetY, 1, wx.GROW, b)
        # sizerOffsetY.SetItemMinSize(lblOffsetY, (w, -1))

        # sizerOffsets = wx.BoxSizer(wx.VERTICAL)
        # sizerOffsets.Add(sizerOffsetX, 1, wx.ALL, 5)
        # sizerOffsets.Add(sizerOffsetY, 1, wx.ALL, 5)

        # sizerScales = wx.BoxSizer(wx.VERTICAL)
        # sizerScales.Add(sizerXSize, 1, wx.ALL, 5)
        # sizerScales.Add(sizerYSize, 1, wx.ALL, 5)

        # hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # hsizer1.Add(sizerOffsets, 1, wx.ALL, 5)
        # hsizer1.Add(sizerScales, 1, wx.ALL, 5)

        hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        btnSave = wx.Button(self, wx.NewId(), 'SAVE', (-1, -1), (-1, h))
        btnCancel = wx.Button(self, wx.NewId(), 'CANEL', (-1, -1), (-1, h))
        hsizer3.Add(btnSave, -1, wx.ALL, 5)
        hsizer3.Add(btnCancel, -1, wx.ALL, 5)

        self.list=wx.ListBox(self,-1,style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_NO_HEADER)
        
        self.list.Show(True)

        self.Bind(wx.EVT_LISTBOX, self.previewFrame, self.list)

        # self.list.InsertColumn(0,"Frames", width=self.list.GetSize()[0]-1)

        self.list.SetItems(contents)
        # 0 will insert at the start of the list
        # for item in contents:
        #     self.list.InsertStringItem(0,item)

        w = 120
        btnTop = wx.Button(self, wx.NewId(), 'Move to &Top', (-1, -1), (w,-1))
        btnUp = wx.Button(self, wx.NewId(), 'Move &Up', (-1, -1), (w,-1))
        btnDown = wx.Button(self, wx.NewId(), 'Move &Down', (-1, -1), (w,-1))
        btnBottom = wx.Button(self, wx.NewId(), 'Move to &Bottom', (-1, -1), (w,-1))

        self.Bind(wx.EVT_BUTTON, self.MoveUp, btnUp)
        self.Bind(wx.EVT_BUTTON, self.MoveDown, btnDown)
        self.Bind(wx.EVT_BUTTON, self.MoveToTop, btnTop)
        self.Bind(wx.EVT_BUTTON, self.MoveToBottom, btnBottom)

        self.Bind(wx.EVT_BUTTON, self.OnOK, btnSave)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btnCancel)

        hsizerM = wx.BoxSizer(wx.HORIZONTAL)        
        btnIns = wx.Button(self, wx.NewId(), '+', (-1, -1), (w/4, -1))
        btnDel = wx.Button(self, wx.NewId(), '-', (-1, -1), (w/4, -1))
        hsizerM.Add((-1, -1), 1)
        hsizerM.Add(btnIns, 1, wx.ALIGN_LEFT, 1)
        hsizerM.Add(btnDel, 1, wx.ALIGN_RIGHT, 1)
        hsizerM.Add((-1, -1), 1)

        self.Bind(wx.EVT_BUTTON, self.InsertItems, btnIns)
        self.Bind(wx.EVT_BUTTON, self.DeleteItem, btnDel)


        b = 0
        vsizer2 = wx.BoxSizer(wx.VERTICAL)
        vsizer2.Add(btnTop, 0, wx.ALL, b)
        vsizer2.Add((-1, -1), 1)
        vsizer2.Add(btnUp, 0, wx.ALL, b)
        vsizer2.Add((-1, -1), 1)

        vsizer2.Add(hsizerM, 0, wx.ALL, b)
        
        vsizer2.Add((-1, -1), 1)
        vsizer2.Add(btnDown, 0, wx.ALL, b)
        vsizer2.Add((-1, -1), 1)
        vsizer2.Add(btnBottom, 0, wx.ALL, b)

        b = 5
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(vsizer2, 0, wx.EXPAND | wx.ALL, b)
        hsizer2.Add(self.list, 1, wx.EXPAND | wx.ALL, b)

        b = 5
        vsizer1 = wx.BoxSizer(wx.VERTICAL)
        vsizer1.Add(hsizer2, 1, wx.ALL | wx.EXPAND, b)

        # TODO: decide if I *really* want to support this...
        # vsizer1.Add(hsizer1, 0, wx.EXPAND, b)
        vsizer1.Add(hsizer3, 0, wx.ALL | wx.EXPAND, b)

        self.SetSizer(vsizer1)

    def resizeRgbFrames(self, evt):
        pass

    def previewFrame(self, evt):
        f = self.list.GetStringSelection()
        if(f is not None and f!=""):
            self.preview_cb(f, True)

    def MoveUp(self, evt):
        d = self.list.GetSelection()
        if(d<1):
            return
        l = self.list.GetItems()
        t = l[d-1]
        l[d-1] = l[d]
        l[d] = t
        self.list.SetItems(l)
        self.list.Select(d-1)

    def MoveDown(self, evt):
        d = self.list.GetSelection()
        if(d>=self.list.GetCount()-1):
            return
        l = self.list.GetItems() 
        t = l[d+1]
        l[d+1] = l[d]
        l[d] = t
        self.list.SetItems(l)
        self.list.Select(d+1)

    def MoveToTop(self, evt):
        d = self.list.GetSelection()
        if(d<1):
            return
        l = self.list.GetItems()
        l = l[d:d+1] + l[0:d] + l[d+1:]
        self.list.SetItems(l)
        self.list.Select(0)

    def MoveToBottom(self, evt):
        d = self.list.GetSelection()
        n = self.list.GetCount() -1
        if(d>=n):
            return
        l = self.list.GetItems()
        l = l[0:d] + l[d+1:] + l[d:d+1]
        self.list.SetItems(l)
        self.list.Select(n)
         # l[0:d-1] + l[d:d+1] + l[d-1:d] + l[d+1:]

    def DeleteItem(self, evt):
        d = self.list.GetSelection()
        if(d>=0):
            self.list.Delete(d)

    def InsertItems(self, event):
        d = self.list.GetSelection()
        if(d<0):
            d = self.list.GetCount()
        items = self.insert_cb()
        if(items is not None):
            self.list.InsertItems(items, d)
        self.Show()

    def SetList(self, option_list):
        self.list.Clear()
        self.list.SetItems(option_list)

    def Show(self, state=True):
        super(OrderedListPanel, self).Show(state)
        self.frame.Show(state)

    def OnOK(self, evt):
        self.Show(False)
        self.cb_fn(self.list.GetItems(), True)

    def OnCancel(self, evt):
        self.Show(False)
        self.cb_fn(None)

    def Close(self):
        self.frame.Close()


class CheckListWindow(wx.Panel):
    """ a class that encapsulates a multi-option checkbox with Ok/Cancel buttons
    Sample usage:  
        clw = CheckListWindow(None, ["A", "B", "C", "D", "E", "F"], ["B", "C", "D"], self.Answered)

    Calling clw.Show(true) will show the window.  When the user dismisses the window,
    self.Answered will be called with a list of items, or None if Cancel was pressed

    Dismissing the window does not destroy it.  It still exists.
    .Show(True) will bring it back
    .SetLists() to adjust the contents and reuse the same window instance
    .Close() will destroy the window (as you would expect)
    """

    def __init__(self, parent, option_list, selected_list, callback_fn, title=""):
        self.frame = wx.Frame(parent, -1, title, wx.DefaultPosition, (400, 300))
        
        super(CheckListWindow, self).__init__(self.frame, -1, wx.DefaultPosition, wx.DefaultSize)

        self.cb_fn = callback_fn
        self.clb = wx.CheckListBox(self, -1, wx.DefaultPosition, wx.DefaultSize, 
            choices=option_list, 
            style=wx.LB_SINGLE, 
            validator=wx.DefaultValidator, 
            name="") 

        self.clb.SetCheckedStrings(selected_list)

        btnOK = wx.Button(self, wx.NewId(), '&OK', (-1, -1), wx.DefaultSize)
        btnCancel = wx.Button(self, wx.NewId(), '&Cancel', (-1, -1), wx.DefaultSize)
        self.Bind(wx.EVT_BUTTON, self.OnOK, btnOK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btnCancel)
        
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtons.Add(btnOK, proportion=0)

        # 10px between the two buttons
        sizerButtons.Add(btnCancel, proportion=0, flag=wx.LEFT, 
            border=10)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # use a 5px border around all size of the CheckListBox 
        border = 5
        mainSizer.Add(self.clb, 1, wx.EXPAND | wx.ALL, border)
        # but only put the 5px border on LEFT, RIGHT, and BOTTOM of
        # button area to avoid double padding between the controls
        mainSizer.Add(sizerButtons, 0, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border)

        self.SetSizer(mainSizer)

    def Show(self, state=True):
        super(CheckListWindow, self).Show(state)
        self.frame.Show(state)

    def SetLists(self, option_list, selected_list):
        self.clb.Clear()
        self.clb.SetItems(option_list)
        self.clb.SetCheckedStrings(selected_list)

    def OnOK(self, evt):
        self.Show(False)
        self.cb_fn(self.clb.GetCheckedStrings())

    def OnCancel(self, evt):
        self.Show(False)
        self.cb_fn(None)

    def Close(self):
        self.frame.Close()

class TestAppOLF(wx.App):
    olw = None

    def Answered(self, arg):
        print("got: %s" % str(arg))
        self.olw.Close()

    def Insert(self):
        return  [chr(random.randint(ord('A'),ord('Z')))]

    def OnInit(self):
        # frame = wx.Frame(None, -1, "Test OLF", wx.DefaultPosition, (400, 300))
        # frame.panel = OrderedListPanel(frame, ["a","b","d","f"])
        # frame.Show(True)
        # self.SetTopWindow(frame)
        self.olw = OrderedListPanel(None, [chr(i) for i in range(ord('a'),ord('z')+1)], self.Answered, self.Insert, "test win")
        self.olw.Show(True)
        return True    

class TestAppCLW(wx.App):
    clw = None

    def Answered(self, arg):
        print("got: %s" % str(arg))
        self.clw.Close()

    def OnInit(self):
        self.clw = CheckListWindow(None, ["A", "B", "C", "D", "E", "F"], ["B", "C", "D"], self.Answered)
        self.clw.Show()
        return True

def main():
    app = TestAppOLF(False)
    app.MainLoop()

if __name__ == "__main__" :
    import random
    main()

