import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from back.respuestas import Status
from back.statistic.statistic import StatisticTest
from back.saver import Saver
from front.IO.IOManage import IOManage
from ...plots import plot_2d,plot_3d,plot_hist, plot_regression,plot_boxplot,plot_correlation_matrix,plot_countplot,plot_histogram_grouped, plot_general_group,plot_covariance_matrix
import numpy as np
import copy
import math
import threading
import time
import re
from ..functions import validate_name,validate_range
from ...constants import WILDCARD_DATA_FILE,WILDCARD_TEXT_FILE
from ..dialogs.dialogs_general import HelpDialog

class MappingDialog(wx.Dialog):
    def __init__(self,parent, bins,variable):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Mapping dialog")
        self.SetFont(parent.GetFont())
        self.bins=bins
        self.variable=variable
        self.bins[self.variable]={'auto':True,'custom':False,'n_bins':None,'names_bins':[],'ranges':[]}
        self.names=[]
        self.ranges=[]

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        self.notebook_1 = wx.Notebook(self, wx.ID_ANY)
        sizer_3.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 10)

        self.notebook_1.SetBackgroundColour(wx.Colour(240,240,240,255))

        self.ntb_automatic = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.ntb_automatic, "Auto")

        sizer_4 = wx.BoxSizer(wx.VERTICAL)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.cb_automatic = wx.CheckBox(self.ntb_automatic, wx.ID_ANY, "Automatic number of bins")
        sizer_5.Add(self.cb_automatic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.ntb_automatic, wx.ID_ANY, "Custom bins"), wx.HORIZONTAL)
        sizer_4.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 10)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self.ntb_automatic, wx.ID_ANY, "Number of bins")
        sizer_8.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.ctrl_number_bins = wx.SpinCtrl(self.ntb_automatic, wx.ID_ANY, "0", min=0, max=100)
        sizer_8.Add(self.ctrl_number_bins, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_9, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self.ntb_automatic, wx.ID_ANY, "Names for the bins")
        sizer_9.Add(label_3, 0, wx.ALL, 5)

        self.list_box_names = wx.ListBox(self.ntb_automatic, wx.ID_ANY, choices=[],style=wx.LB_MULTIPLE)
        sizer_9.Add(self.list_box_names, 1, wx.ALL | wx.EXPAND, 5)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 0, wx.EXPAND, 0)

        self.button_add_name = wx.Button(self.ntb_automatic, wx.ID_ANY, "Add")
        sizer_10.Add(self.button_add_name, 0, wx.ALL, 5)

        self.button_remove_name = wx.Button(self.ntb_automatic, wx.ID_ANY, "Remove")
        sizer_10.Add(self.button_remove_name, 0, wx.ALL, 5)

        self.ntb_custom = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.ntb_custom, "Custom")

        sizer_11 = wx.BoxSizer(wx.VERTICAL)

        sizer_12 = wx.StaticBoxSizer(wx.StaticBox(self.ntb_custom, wx.ID_ANY, "New map"), wx.HORIZONTAL)
        sizer_11.Add(sizer_12, 0, wx.ALL | wx.EXPAND, 10)

        sizer_14 = wx.BoxSizer(wx.VERTICAL)
        sizer_12.Add(sizer_14, 1, wx.EXPAND, 0)

        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14.Add(sizer_15, 0, wx.EXPAND, 0)

        label_range = wx.StaticText(self.ntb_custom, wx.ID_ANY, "Range")
        sizer_15.Add(label_range, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.ctrl_range = wx.TextCtrl(self.ntb_custom, wx.ID_ANY, "")
        sizer_15.Add(self.ctrl_range, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14.Add(sizer_16, 0, wx.EXPAND, 0)

        label_new_value = wx.StaticText(self.ntb_custom, wx.ID_ANY, "Value")
        sizer_16.Add(label_new_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)

        self.ctrl_new_value = wx.TextCtrl(self.ntb_custom, wx.ID_ANY, "")
        sizer_16.Add(self.ctrl_new_value, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 7)

        sizer_13 = wx.StaticBoxSizer(wx.StaticBox(self.ntb_custom, wx.ID_ANY, "Mapping Rules"), wx.HORIZONTAL)
        sizer_11.Add(sizer_13, 1, wx.ALL | wx.EXPAND, 10)

        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_13.Add(sizer_17, 1, wx.EXPAND, 0)

        self.lb_rules = wx.ListBox(self.ntb_custom, wx.ID_ANY, choices=[],style=wx.LB_MULTIPLE)
        sizer_17.Add(self.lb_rules, 1, wx.ALL | wx.EXPAND, 5)

        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17.Add(sizer_18, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.button_add_custom_rule = wx.Button(self.ntb_custom, wx.ID_ANY, "Add")
        sizer_18.Add(self.button_add_custom_rule, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.button_remove_custom_rule = wx.Button(self.ntb_custom, wx.ID_ANY, "Remove")
        sizer_18.Add(self.button_remove_custom_rule, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.ntb_custom.SetSizer(sizer_11)

        self.ntb_automatic.SetSizer(sizer_4)

        self.cb_automatic.SetValue(True)
        self._enable_custom_bins(False)

        self.Bind(wx.EVT_CHECKBOX,self.OnSelectAutomatic,self.cb_automatic)
        self.Bind(wx.EVT_BUTTON,self.OnAddVarName,self.button_add_name)
        self.Bind(wx.EVT_BUTTON,self.OnDeleteVarName,self.button_remove_name)
        self.Bind(wx.EVT_BUTTON,self.OnAddRule,self.button_add_custom_rule)
        self.Bind(wx.EVT_BUTTON,self.OnDeleteRule,self.button_remove_custom_rule)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnChangePage,self.notebook_1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
    
    def OnChangePage(self,evt):
        if self.ntb_automatic.IsShown():
            self.button_add_name.SetDefault()
        else:
            self.button_add_custom_rule.SetDefault()
            
    def OnApply(self,evt):
        if self.ntb_automatic.IsShown():
            names=self.list_box_names.GetStrings()        
            bins=self.ctrl_number_bins.GetValue()

            if not self.cb_automatic.IsChecked() and bins <= 0:
                wx.MessageBox("Invalid number of bins","Error",wx.ICON_ERROR)
            else:

                if not self.cb_automatic.IsChecked() and len(names)!=bins:
                    wx.MessageBox("Inconsistent number of bins and names","Error",wx.ICON_ERROR)
                else:
                    self.bins[self.variable]['n_bins']=bins
                    self.bins[self.variable]['names_bins']=names
                    self.EndModal(wx.ID_APPLY)
        else:
            self.bins[self.variable]['auto']=False
            self.bins[self.variable]['custom']=True
            self.bins[self.variable]['names_bins']=self.names
            self.bins[self.variable]['ranges']=self._sort_intervals(self.ranges)
            self.EndModal(wx.ID_APPLY)
            #wx.MessageBox("This function is not implementend yet.","Info")

    def _sort_intervals(self,intervals):
        def interval_to_tuple(interval):
            
            pattern_left_bound=r"^[\(\[]"
            pattern_right_bound=r"[\)\]]$"
            pattern = r"[-+]?\d+(\.\d+)?"
            numbers = [float(match.group()) for match in re.finditer(pattern, interval)]
            left_bound=re.search(pattern_left_bound, interval).group(0)
            
            right_bound=re.search(pattern_right_bound,interval).group(0)
            
            left=numbers[0]
            right=numbers[1]
            return (left,right),left_bound,right_bound

        interval_tuples={}
        for interval in intervals:
            result=interval_to_tuple(interval)
            interval_tuples[result[0]]={'left':result[1],'right':result[2]}

        sorted_tuples = sorted(list(interval_tuples.keys()))

        def tuple_to_interval(t,left,right): 
            return f"{left}{t[0]},{t[1]}{right}"

        sorted_intervals={}
        for i in range(len(sorted_tuples)):
            t=sorted_tuples[i]
            sorted_intervals[i]={'left_bound':interval_tuples[t]['left'],'left_value':t[0],'right_value':t[1],'right_bound':interval_tuples[t]['right']}
        #sorted_intervals = [tuple_to_interval(t,interval_tuples[t]['left'],interval_tuples[t]['right']) for t in sorted_tuples]

        return sorted_intervals
    
    def _sort_ranges(self):

        sorted=["pos" for i in range(len(self.ranges))]
        min_val=-np.inf
        max_val=np.inf

        for ran in self.ranges:
            pattern = r"[-+]?\d+(\.\d+)?"
            numbers = [float(match.group()) for match in re.finditer(pattern, ran)]
            left=numbers[0]
            right=numbers[1]

            if right<min_val:
                sorted

    def _enable_custom_bins(self,value):
        self.ctrl_number_bins.Enable(value)
        self.button_add_name.Enable(value)
        self.button_remove_name.Enable(value) 

    def OnSelectAutomatic(self,evt):
        
        value=evt.IsChecked()

        if value:
            self._enable_custom_bins(False)
            self.bins[self.variable]={'auto':True,'custom':False,'n_bins':None,'names_bins':[],'ranges':[]}
        else:
            self._enable_custom_bins(True)
            self.bins[self.variable]={'auto':False,'custom':False,'n_bins':self.ctrl_number_bins.GetValue(),'names_bins':self.list_box_names.GetStrings(),'ranges':[]}
    
    def OnAddVarName(self,evt):

        dialog=wx.TextEntryDialog(self,"New name","Enter new name for bin")
        code=dialog.ShowModal()

        if code==wx.ID_OK:
            name=dialog.GetValue()
            names=self.list_box_names.GetStrings()
            if validate_name(name) and not name in names:
                self.list_box_names.Append([name])
            else:
                wx.MessageBox("Not a valid name","Error",wx.ICON_ERROR)
    
    def OnDeleteVarName(self,evt):
        selections=self.list_box_names.GetSelections()
        toDel=[]
        names=self.list_box_names.GetStrings()

        for sel in selections:
            toDel.append(names[sel])
        
        for element in toDel:
            names.remove(element)
        
        self.list_box_names.Clear()
        if len(names)!=0:
            self.list_box_names.Append(names)
            
    def OnAddRule(self,evt):
        name=self.ctrl_new_value.GetValue()
        range=self.ctrl_range.GetValue()

        if validate_name(name) and validate_range(range):
            rule=" range "+range+" -> new value "+name+""
            
            self.names.append(name)
            self.ranges.append(range)

            self.ctrl_new_value.SetLabelText("")
            self.lb_rules.Append(rule)

        else:
            wx.MessageBox("Either name or value do not have the corret format","Error",wx.ICON_WARNING)
        
    def OnDeleteRule(self,evt):
        selections=self.lb_rules.GetSelections()
        toDel=[]
        
        rules=self.lb_rules.GetStrings()

        for sel in selections:
            toDel.append(rules[sel])
            
        #pattern = r"range\((.*?)\) -> new value\((.*?)\)"
        pattern = r"range (.*?) -> new value (.*?)"
       

        for element in toDel:

            match=re.search(pattern, element)
            self.names.remove(match.group(2))
            self.ranges.remove(match.group(1))
            
            rules.remove(element)

        self.lb_rules.Clear()
        if len(rules)!=0:
            self.lb_rules.Append(rules)
    
    def OnChangeNumberBins(self,evt):
        if not self.cb_automatic.IsChecked():
            self.bins[self.variable]['auto']=True

class TransformDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(TransformDialog, self).__init__(parent)
        self.SetTitle("Transform")
        self.SetFont(parent.GetFont())
        self.names=["All"]
        self.controller=parent.controller
        for name in parent.names:
            if not name in parent.identifier_cols:
                self.names.append(name)
        
        self.string_variables=parent.string_variable_names
        self.changes=False
        self.data_preprocess={}
        self.data_preprocess['All']={'apply':True,'numerical':'None','categorical':'None'}   
        self.progressbar=None

        self.bins={}

        for variable in parent.names:
            self.data_preprocess[variable]={'transformation':'None','keep_original':True,'params':None} 

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Apply to"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_variable = wx.ComboBox(self, wx.ID_ANY, choices=self.names,value="All", style=wx.CB_DROPDOWN | wx.CB_READONLY)
        sizer_4.Add(self.combo_box_variable, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.notebook_1 = wx.Notebook(self, wx.ID_ANY)
        sizer_3.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 10)

        self.notebook_1.SetBackgroundColour(wx.Colour(240,240,240,255))
        
        self.notebook_numerical = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.notebook_numerical, "Numerical")

        sizer_11 = wx.BoxSizer(wx.VERTICAL)

        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_11.Add(sizer_5, 1, wx.EXPAND | wx.ALL, 10)

        self.radio_box_numerical = wx.RadioBox(self.notebook_numerical, wx.ID_ANY, "Transformation", choices=["None","Normalization (MinMax)", "Quantile Scaler", "Robust Scaler", "Discretize"], majorDimension=2, style=wx.RA_SPECIFY_COLS)
        self.radio_box_numerical.SetSelection(0)
        sizer_5.Add(self.radio_box_numerical, 1, wx.EXPAND|wx.ALL, 5)

        self.button_select_bins = wx.Button(self.notebook_numerical, wx.ID_ANY, "Select bins")
        sizer_5.Add(self.button_select_bins, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        self.button_select_bins.Enable(False)

        self.notebook_categorical = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.notebook_categorical, "Categorical")

        sizer_14 = wx.BoxSizer(wx.VERTICAL)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_14.Add(sizer_6, 0, wx.EXPAND | wx.ALL, 10)

        self.radio_box_categorical = wx.RadioBox(self.notebook_categorical, wx.ID_ANY, "Transformation", choices=["None","One hot encoding", "Label encoding",], majorDimension=2, style=wx.RA_SPECIFY_COLS)
        self.radio_box_categorical.SetSelection(0)
        sizer_6.Add(self.radio_box_categorical, 1, wx.EXPAND | wx.ALL, 5)

        #self.button_mapping_options = wx.Button(self.notebook_categorical, wx.ID_ANY, "Mapping")
        #sizer_6.Add(self.button_mapping_options, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self._enable_mapping(False)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_8, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 12)

        self.checkbox_keep = wx.CheckBox(self, wx.ID_ANY, "Keep original variables")
        sizer_8.Add(self.checkbox_keep, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.notebook_categorical.SetSizer(sizer_14)
        self.notebook_numerical.SetSizer(sizer_11)


        self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box_variable)
        self.Bind(wx.EVT_RADIOBOX,lambda event: self.OnChangeRadioBox(event,True),self.radio_box_numerical)
        self.Bind(wx.EVT_RADIOBOX,lambda event: self.OnChangeRadioBox(event,False),self.radio_box_categorical)
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeCheck,self.checkbox_keep)
        self.Bind(wx.EVT_BUTTON,self.OnSelectBins,self.button_select_bins)
        #self.Bind(wx.EVT_BUTTON,self.OnClose,self.button_CANCEL)
        #self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        #self.SetSize(300,440)

        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()


    def OnSelectBins(self,evt):
        variable=self.combo_box_variable.GetValue()
        dialog=MappingDialog(self,self.bins,variable)
        
        code=dialog.ShowModal()

        if code==wx.ID_APPLY:
            self.data_preprocess[variable]['params']=self.bins[variable]

    def OnChangeCheck(self,evt):
        
        variable=self.names[self.combo_box_variable.GetSelection()]

        if variable!="All":
            self.data_preprocess[variable]['keep_original']=self.checkbox_keep.GetValue()
        else:
            for var in self.names:
                if var!="All":
                    self.data_preprocess[var]['keep_original']=self.checkbox_keep.GetValue()
        
    def OnChangeRadioBox(self,evt,numerical):
       
        variable=self.names[self.combo_box_variable.GetSelection()]
        
        if variable=="All":
            self.data_preprocess['All']['apply']=True
            if numerical:
                selection=self.radio_box_numerical.GetStrings()[self.radio_box_numerical.GetSelection()]
                
                self.data_preprocess[variable]['numerical']=selection
            else:
                self.data_preprocess[variable]['categorical']=self.radio_box_categorical.GetStrings()[self.radio_box_categorical.GetSelection()]

            for var in self.names:
                if var!="All":
                    if var in self.string_variables:
                        self.data_preprocess[var]['transformation']=self.radio_box_categorical.GetStrings()[self.radio_box_categorical.GetSelection()]
                    else:
                        
                        selection=self.radio_box_numerical.GetStrings()[self.radio_box_numerical.GetSelection()]
                        
                        self.data_preprocess[var]['transformation']=selection
                    
                    self.data_preprocess[var]['keep_original']=self.checkbox_keep.GetValue()
        else:

            selection=self.radio_box_numerical.GetStrings()[self.radio_box_numerical.GetSelection()]
            if selection=="Discretize":
                self.button_select_bins.Enable(True)
                self.data_preprocess[variable]['params']={'auto':True,'custom':False,'n_bins':None,'names_bins':[],'ranges':[]}
            else:
                self.button_select_bins.Enable(False)

            self.data_preprocess['All']['apply']=False
            self.data_preprocess[variable]['transformation']=evt.GetString()
            self.data_preprocess[variable]['keep_original']=self.checkbox_keep.GetValue()


    def OnApply(self,evt):
        self.button_APPLY.Disable()

        self.progressbar = wx.ProgressDialog("Applying cleanse", "Please, wait...", maximum=100, parent=self)

        thread = threading.Thread(target=self.execute_thread)
        thread.start()
        
                
    def update_progress(self, value):
        self.progressbar.Update(value,"Progress...")

    def execute_thread(self):
        process=True
        i=0
        shift=100/len(self.names)
        for variable in self.names:
            if variable!="All":
                result=self.controller.apply_preprocess(variable).get_response()
                
                if result['status']!=Status.OK:
                    wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)
                    process=False
                

                time.sleep(0.001)
                wx.CallAfter(self.update_progress, int(i))
                i+=shift

        wx.CallAfter(self.progressbar.Update,self.progressbar.GetRange())
    
        if process:
            wx.CallAfter(wx.MessageBox,"Transformations succesfully applied","Info",wx.OK|wx.ICON_INFORMATION)
            self.changes=True
            wx.CallAfter(self.EndModal,wx.OK)
            wx.CallAfter(self.Destroy)
                    
    def OnSave(self,evt):
        
        process=True
        for variable in self.names:
            result=self.controller.set_preprocess_option(variable,self.data_preprocess[variable]).get_response()

            if result['status']!=Status.OK:
                wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)
                process=False
        
        if process:
            wx.MessageBox("Succesfully saved","Info",wx.OK|wx.ICON_INFORMATION)
            

    def OnChangeVariable(self,evt):
        
        variable=self.names[self.combo_box_variable.GetSelection()]
        
        if variable=="All":
            self._enable_categorical(True)
            self._enable_numerical(True)
            self._enable_mapping(False)
        
        elif variable in self.string_variables:
            self._enable_categorical(True)
            self._enable_numerical(False)
        else:
            self._enable_categorical(False)
            self._enable_numerical(True)
    
    def _enable_numerical(self,val):
        self.notebook_numerical.Enable(val)
        #self.button_select_bins.Enable(val)
        self.radio_box_numerical.Enable(val)
        self.radio_box_numerical.EnableItem(self.radio_box_numerical.GetCount()-1,val)

    def _enable_categorical(self,val):
        self.notebook_categorical.Enable(val)
        #self.button_mapping_options.Enable(val)
        self.radio_box_categorical.Enable(val)
        self.radio_box_categorical.EnableItem(self.radio_box_categorical.GetCount()-1,val)
    
    def _enable_mapping(self,val):
        #self.radio_box_categorical.EnableItem(self.radio_box_categorical.GetCount()-1,val)
        #self.button_mapping_options.Enable(val)

        self.radio_box_numerical.EnableItem(self.radio_box_numerical.GetCount()-1,val)
        self.button_select_bins.Enable(val)

class PreprocessDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(PreprocessDialog, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Preprocess")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Options"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 5)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 1, wx.EXPAND, 0)

        self.radio_btn_1 = wx.RadioButton(self, wx.ID_ANY, "Principal Component Analysis")
        sizer_6.Add(self.radio_btn_1, 0, wx.ALL, 5)

        self.radio_btn_2 = wx.RadioButton(self, wx.ID_ANY, "Rebalance data")
        sizer_6.Add(self.radio_btn_2, 0, wx.ALL, 5)

        self.radio_btn_clustering = wx.RadioButton(self, wx.ID_ANY, "Clustering")
        sizer_6.Add(self.radio_btn_clustering, 0, wx.ALL, 5)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, " PCA"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 10)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7.Add(sizer_9, 1, wx.EXPAND, 0)

        sizer_10 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)

        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10.Add(sizer_11, 1, wx.ALL, 5)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Number of principal components")
        sizer_11.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.spin_ctrl_1 = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0, max=100)
        sizer_11.Add(self.spin_ctrl_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Rebalance data"), wx.HORIZONTAL)
        sizer_3.Add(sizer_8, 0, wx.ALL | wx.EXPAND, 10)

        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_8.Add(sizer_12, 1, wx.ALL | wx.EXPAND, 5)

        sizer_13 = wx.BoxSizer(wx.VERTICAL)
        sizer_12.Add(sizer_13, 1, wx.ALL | wx.EXPAND, 5)

        self.radio_btn_3 = wx.RadioButton(self, wx.ID_ANY, "Oversampling")
        sizer_13.Add(self.radio_btn_3, 0, wx.ALL, 5)

        self.radio_btn_4 = wx.RadioButton(self, wx.ID_ANY, "Undersampling")
        sizer_13.Add(self.radio_btn_4, 0, wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()

class AutomaticTest(wx.Dialog):
    def __init__(self,parent):
        
        super(AutomaticTest, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Automatic test result")
        self.controller=parent.controller
        result=parent.controller.automatic_statistic_test().get_response()

        normal_variables=["None"]
        self.grouped_different_variables=["None"]
        correlation=["None"]
        directly=[]
        inverse=[]
        self.covariance_list=[]
        differences_in_groups=[]
        
        names=parent.names

        if result['status']==Status.OK:
            
            normal_variables=result['data']['normal_variables']
            correlation=result['data']['correlation']
            differences_in_groups=result['data']['differences']

            for pair in correlation['directly']:
                directly.append(str(pair['variables'] +" - "+" directly"))

            for pair in correlation['inverse']:
                inverse.append(str(pair['variables'] +" - "+" inverse"))

            self.covariance_list=directly+inverse

            for entry in differences_in_groups:
                self.grouped_different_variables=[]
                self.grouped_different_variables.append(str(entry['variable']+" shows differences in "+entry['groupby']+" between "+entry['pair']))
            
        else:
            wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)
            self.Destroy()
            
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        margin=10

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Normality"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, margin)

        self.normal_variables=normal_variables
        self.list_box_normal = wx.ListBox(self, wx.ID_ANY, choices=normal_variables)
        sizer_4.Add(self.list_box_normal, 1, wx.ALL | wx.EXPAND, 10)

        sizer_4b = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Correlation"), wx.HORIZONTAL)

        sizer_filter_covariance=wx.BoxSizer(wx.VERTICAL)

        label_filter=wx.StaticText(self,wx.ID_ANY,label="Filter by")
        sizer_filter_covariance.Add(label_filter,0,wx.ALL,0)

        self.combobox_filter_covariance=wx.ComboBox(self,choices=names,style=wx.CB_READONLY)
        sizer_filter_covariance.Add(self.combobox_filter_covariance,0,wx.ALL,0)

        
        sizer_3.Add(sizer_4b, 1, wx.ALL | wx.EXPAND, margin)

        sizer_4b.Add(sizer_filter_covariance, 0, wx.ALL | wx.EXPAND, margin)

        self.list_box_covariance = wx.ListBox(self, wx.ID_ANY, choices=self.covariance_list)
        sizer_4b.Add(self.list_box_covariance, 1, wx.ALL | wx.EXPAND, 10)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Statistical differences by group"), wx.HORIZONTAL)
        sizer_3.Add(sizer_6, 0, wx.ALL | wx.EXPAND, margin)

        self.list_box_differences = wx.ListBox(self, wx.ID_ANY, choices=self.grouped_different_variables)
        sizer_6.Add(self.list_box_differences, 1, wx.ALL | wx.EXPAND, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        sizer_2.AddButton(self.button_CLOSE)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_COMBOBOX,self.OnChangeCovarianceFilter,self.combobox_filter_covariance)
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Center()
        self.Layout()

    def OnSave(self,evt):
        content="Results:\n"
        content+="Normal variables:"

        for elem in self.normal_variables:
            content+=str(elem)
            if elem!=self.normal_variables[-1]:  
                content+=','
        
        content+="\n\nCorrelations: \n"
        for elem in self.covariance_list:
            content+=elem+"\n"
        content+="\n\nStatistical differences: \n"
        for elem in self.grouped_different_variables:
            content+=elem+"\n"

        response=IOManage.GetPath(self,"Save file",wildcard=WILDCARD_TEXT_FILE,default_name="statistics").get_response()
        
        if response['status']==Status.OK:
            path=response['data']
            response=self.controller.save_file(content,path).get_response()

            if response['status']==Status.OK:
                wx.MessageBox("File Succesfully saved in "+path,"Info")
            else:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
        

    def OnChangeCovarianceFilter(self,evt):
        filter=self.combobox_filter_covariance.GetValue()
        filtered=[value for value in self.covariance_list if (str(filter) in value)]
        if len(filtered)==0:
            filtered.append("None")
        self.list_box_covariance.Clear()
        self.list_box_covariance.InsertItems(filtered,0)

class SingleSummaryDialog(wx.Dialog):
    def __init__(self, parent,variable,group,numeric=True):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Summary")
        self.SetFont(parent.GetFont())
        self.parent=parent
        self.variable=variable
        self.group=group
        self.numeric=numeric
        isGrouped=True
        message=str(variable+" grouped by "+group)
        label="Group"
        plottable=True
        
        if group=="None" or not numeric:
            group=None
            isGrouped=False
            message=variable
            label="Name"
            if numeric:
                plottable=False

        response=parent.controller.get_variable_summary(variable,group).get_response()
        
        data=None
        
        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
        else:
            data=response['data']           
            

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        label_variable = wx.StaticText(self, wx.ID_ANY,message)
        label_variable.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_3.Add(label_variable, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY)
        
        self.grid_1=self.createDataGrid(self.grid_1,data,variable,isGrouped and numeric)
    
        self.grid_1.SetColLabelValue(0, label)
        self.grid_1.SetColLabelValue(1, "count")

        if numeric:    
            self.grid_1.SetColLabelValue(2, "mean")
            self.grid_1.SetColLabelValue(3, "std")
            self.grid_1.SetColLabelValue(4, "min")
            self.grid_1.SetColLabelValue(5, "25%")
            self.grid_1.SetColLabelValue(6, "50%")
            self.grid_1.SetColLabelValue(7, "75%")
            self.grid_1.SetColLabelValue(8, "max")
        else:
            self.grid_1.SetColLabelValue(2, "unique")
            self.grid_1.SetColLabelValue(3, "top")
            self.grid_1.SetColLabelValue(4, "freq")

        
        sizer_3.Add(self.grid_1, 0, wx.ALL | wx.EXPAND, 20)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)
       
        if plottable:
            self.button_plot = wx.Button(self, wx.ID_APPLY, "Plot")
            sizer_2.AddButton(self.button_plot)
            self.Bind(wx.EVT_BUTTON,self.plot_histogram,self.button_plot)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        
        self.Center()
        self.Layout()
    

    def plot_histogram(self,evt):
            
        response=self.parent.controller.get_column(list(self.parent.names).index(self.variable)).get_response()
        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
        else:
            x=response['data']
            
            if self.numeric:
                response=self.parent.controller.get_column(list(self.parent.names).index(self.group)).get_response()
                if response['status']!=Status.OK:
                    wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
                else:
                    g=response['data']
                    
                    plot_histogram_grouped(pd.DataFrame({self.variable:x,self.group:g}),self.variable,self.group)
            else:
                plot_countplot(x)
                

    def createDataGrid(self,grid,data,variable,group):

        i=0
        j=0

        if group==False:
            
            grid.CreateGrid(1,data.shape[0]+1)
            grid.SetColMinimalWidth(0,30)
            grid.SetCellValue(i,j,str(variable))
            grid.SetReadOnly(i,j,True)
            grid.SetCellAlignment(i, j, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            j+=1
            for index in data.index:
                value=data.loc[index]
                if self.numeric:
                    value=round(value,2)
                grid.SetCellValue(i,j," "+str(value)+" ")
                grid.SetReadOnly(i,j,True)
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                j+=1        
            i+=1

        else:
            
            grid.CreateGrid(data.shape[0],9)
            grid.SetColMinimalWidth(0,30)
            
            for group in data.index:
                j=0
                grid.SetCellValue(i,j,str(group))
                
                for value in data.loc[group]:
                    j+=1
                    val=""
                    if not math.isnan(value):
                        val=str(round(value,2))
                    else:
                        val=str(value)
                    
                    grid.SetCellValue(i,j," "+val+" ")
                    grid.SetReadOnly(i,j,True)
                    
                    
                i+=1

        grid.SetRowLabelSize(0)
        grid.ShowScrollbars(wx.SHOW_SB_NEVER,wx.SHOW_SB_NEVER)

        return grid

class SummaryPickDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Summary pick")
        self.SetFont(parent.GetFont())
        self.parent=parent
        names=parent.names
        self.nominal_variables=parent.string_variable_names
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Variable"), wx.VERTICAL)
        sizer_4.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 5)

        self.combo_box__variable = wx.ComboBox(self, wx.ID_ANY, choices=names, style=wx.CB_READONLY)
        sizer_5.Add(self.combo_box__variable, 0, wx.ALL, 5)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Group by"), wx.VERTICAL)
        sizer_4.Add(sizer_6, 0, wx.ALL | wx.EXPAND, 5)

        groupby_variables=copy.deepcopy(self.parent.string_variable_names)
        
        groupby_variables.append("None")
        self.combo_box_group = wx.ComboBox(self, wx.ID_ANY, choices=groupby_variables,value="None", style=wx.CB_READONLY)
        if len(groupby_variables)==1:
            self.combo_box_group.Enable(False)

        sizer_6.Add(self.combo_box_group, 0, wx.ALL, 5)

        self.checkbox_all_variable = wx.CheckBox(self, wx.ID_ANY, "Show all variables summary")
        sizer_3.Add(self.checkbox_all_variable, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_OK)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeAllVariables,self.checkbox_all_variable)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box__variable)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
    
    def OnChangeVariable(self,evt):
        variable=self.combo_box__variable.GetValue()

        if variable in self.nominal_variables:
            self.combo_box_group.Enable(False)
        else:
            self.combo_box_group.Enable(True)
        
    def OnChangeAllVariables(self,evt):
        all_variables=self.checkbox_all_variable.GetValue()

        if all_variables:
            self.combo_box__variable.Enable(False)
            self.combo_box_group.Enable(False)
        else:
            self.combo_box__variable.Enable(True)
            self.combo_box_group.Enable(True)

    def OnApply(self,evt):
        all_variables=self.checkbox_all_variable.GetValue()
        
        if all_variables:
            dialog=SummaryDialog(self.parent)
            dialog.ShowModal()
            
        else:
            variable=self.combo_box__variable.GetValue()
            group=self.combo_box_group.GetValue()

            if variable=="":
                wx.MessageBox("You must select a variable","Error",wx.OK|wx.ICON_EXCLAMATION)
            else:
                dialog=SingleSummaryDialog(self.parent,variable,group,not variable in self.nominal_variables)
                dialog.ShowModal()

class TestResultDialog(wx.Dialog):
    def __init__(self,parent,name,result,explanation,lower=True):
        
        super(TestResultDialog, self).__init__(parent)
        self.SetTitle(name)
        self.SetFont(parent.GetFont())
        self.result=result

        self.image="./front/resources/img/x.png"
        self.header="Unsuccesful"
        pvalues=self.result['pvalue']
        self.single_result=len(pvalues)==1

        if self.single_result:
            pvalue=np.round(self.result['pvalue'][0],5)
            
            if (lower and pvalue>0.05) or (lower==False and pvalue<0.05):
                self.image="./front/resources/img/ok.png"
                self.header="Succesful"

                explanation="\nThere is significicant statistical evidence "+explanation
            else:
                explanation="\nThere is NO significicant statistical evidence "+explanation
        else:
            
            for pvalue in pvalues:
                if (lower and pvalue>0.05) or (lower==False and pvalue<0.05):
                    self.image="./front/resources/img/ok.png"
                    self.header="Succesful"                    
                    break
            
            explanation="\nThere is significicant statistical evidence "+explanation
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY,self.header)
        label_1.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_4.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)

        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image, wx.BITMAP_TYPE_PNG))
        sizer_4.Add(bitmap_1, 0, wx.EXPAND, 30)

        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_5, 1, wx.ALL, 10)

        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(sizer_6, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        if self.single_result:
            label_2 = wx.StaticText(self, wx.ID_ANY, "p-value")
            sizer_6.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP, 10)

            self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, str(pvalue))
            self.text_ctrl_1.Enable(False)
            sizer_6.Add(self.text_ctrl_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Explanation"), wx.VERTICAL)
        sizer_5.Add(sizer_7, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        label_3 = wx.StaticText(self, wx.ID_ANY, explanation)
        sizer_7.Add(label_3, 1, wx.EXPAND, 20)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())

        self.Center()
        self.Layout()

class StatisticDialog(wx.Dialog):
    def __init__(self,parent, *args, **kwds):
        super(StatisticDialog, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Statistics")
        self.identifier_cols=parent.identifier_cols
        self.controller=parent.controller
        self.names=list(parent.names)
        self.grouping=parent.string_variable_names
        self.comparing=parent.float_variable_names+parent.int_variable_names
        self.one_variable_test=False
        test_placeholder=StatisticTest.get_placeholder()
        tests=StatisticTest.get_tests()
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "A "), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_A = wx.ComboBox(self, wx.ID_ANY, choices=self.comparing,value="First variable",style=wx.CB_READONLY)
        sizer_4.Add(self.combo_box_A, 1, wx.ALL, 5)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "B"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_B = wx.ComboBox(self, wx.ID_ANY, choices=self.names,value="Second variable (if needed)", style=wx.CB_READONLY)
        sizer_5.Add(self.combo_box_B, 1, wx.ALL, 5)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Test"), wx.HORIZONTAL)
        sizer_3.Add(sizer_6, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_test = wx.ComboBox(self, wx.ID_ANY, choices=test_placeholder,value="Test to apply", style=wx.CB_READONLY)
        sizer_6.Add(self.combo_box_test, 1, wx.ALL, 5)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Other options"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 10)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)

        self.checkbox_automatic_tests = wx.CheckBox(self, wx.ID_ANY, "Run automatic test")
        sizer_8.Add(self.checkbox_automatic_tests, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.checkbox_corr = wx.CheckBox(self, wx.ID_ANY, "Show global correlation matrix")
        sizer_8.Add(self.checkbox_corr, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.checkbox_covariance = wx.CheckBox(self, wx.ID_ANY, "Show global covariance matrix")
        sizer_8.Add(self.checkbox_covariance, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_OK = wx.Button(self, wx.ID_OK, "Run")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeTest,self.combo_box_test)
        self.Bind(wx.EVT_BUTTON,self.OnRun,self.button_OK)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeCorrCov,self.checkbox_corr)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeCorrCov,self.checkbox_covariance)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeCorrCov,self.checkbox_automatic_tests)
        self.Bind(wx.EVT_BUTTON,self.OnHelp,self.button_HELP)

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
                
    def OnHelp(self,evt):
        dialog=HelpDialog(self,file="./front/resources/help/statistics_help.json",title="Statisticts Help")
        dialog.ShowModal()

    def EnableComponents(self,val):
        self.combo_box_A.Enable(val)
        self.combo_box_B.Enable(val)
        self.combo_box_test.Enable(val)

    def OnChangeCorrCov(self,evt):
        if self.checkbox_automatic_tests.GetValue():
            self.EnableComponents(False)
            self.checkbox_corr.Enable(False)
            self.checkbox_covariance.Enable(False)
        elif self.checkbox_corr.GetValue() or self.checkbox_covariance.GetValue():
            self.EnableComponents(False)
            self.checkbox_corr.Enable(True)
            self.checkbox_covariance.Enable(True)
        else:
            self.EnableComponents(True)
            self.checkbox_corr.Enable(True)
            self.checkbox_covariance.Enable(True)

    def validate_choice(self,val):
        if val=="":
            return False
        return True        

    def OnRun(self,event):
        test=self.combo_box_test.GetValue()
        a=self.combo_box_A.GetValue()
        b=self.combo_box_B.GetValue()
        other_option=False
        
        if self.checkbox_automatic_tests.GetValue():
            shape=self.controller.get_data_shape().get_response()['data']
            code=wx.YES
            classes=self.controller.get_nominal_classes().get_response()['data']

            warning=False
            message="The following variables will be ignored because they have more than 5 groups: "
           
            for elem in classes:     
                if len(classes[elem])>5:
                    warning=True
                    message=message+" "+elem+","
                     

            if shape[0]>5000 and not warning:
                code=wx.MessageBox("The amount of data may be very high for the automatic tests, p-value may not be accurate for N > 5000. . You want to  continue anyway?","Warning",wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_WARNING)
            elif warning:
                wx.MessageBox(message,"Warning",wx.ICON_WARNING)

            if code==wx.YES:
                dialog=AutomaticTest(self)
                code=dialog.ShowModal()

        elif self.checkbox_corr.GetValue() or self.checkbox_covariance.GetValue():
            df=self.controller.get_data().get_response()['data']
            
            df=df.drop(self.identifier_cols,axis=1)
            if df.shape[1]>0:
                if self.checkbox_corr.GetValue():
                    plot_correlation_matrix(df)
                if self.checkbox_covariance.GetValue():
                    plot_covariance_matrix(df)
            else:
                wx.MessageBox("There is no available data to represent","Info")
            other_option=True
        else:

            if not self.validate_choice(test) and not other_option:
                wx.MessageBox("You need to select a test","Error",wx.OK|wx.ICON_ERROR)
            else:
                if not self.validate_choice(a):
                    wx.MessageBox("You have to select A variable","Error",wx.OK|wx.ICON_ERROR) 
                else:

                    index_b=None
                    y=None
                    complete=False
                    if not self.one_variable_test: 
                        if not self.validate_choice(b):
                            wx.MessageBox("You have to select B variable","Error",wx.OK|wx.ICON_ERROR)
                        else:
                            index_b=self.names.index(b)
                            y=self.controller.get_column(index_b).get_response()['data']
                            complete=True
                    
                    index_a=self.names.index(a)
                    x=self.controller.get_column(index_a).get_response()['data']
                    if 'Shapiro' in test:   
                        self.OnLaunchResulDialog(StatisticTest.shapiro_wilk,test,variables=[x],names=[a],condition=True,msg="to determine that this variable has a normal distribution")
                    elif 'ANOVA' in test and complete:
                        
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.ANOVA)
                    elif 'T Student' in test and complete:
                        
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.t_student)
                    elif 'Kruskal Wallis' in test and complete:
                        
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.kruskal_wallis)
                    elif 'Wilcoxon' in test and complete:
                        
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.wilcoxon)
                        
                    elif 'Pearson' in test and complete:
                        self.OnLaunchResulDialog(StatisticTest.pearson,test,variables=[x,y],names=[a,b],condition=False,msg="to determine that there is correlation between ")
                    
    def _differencesGroupTemplate(self,y,x,a,b,test,method):
        grouping_values=np.unique(y)

        if len(grouping_values)<5:
            dict_y={}
            for group in grouping_values:
                dict_y[group]=x[y==group]

            self.OnLaunchGroupingResultDialog(method,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
        else:
            wx.MessageBox("There is too many groups to perform the test.","Warning",wx.ICON_WARNING)

    def OnLaunchGroupingResultDialog(self,test,test_name,dict_y,groups,names,msg=""):
        i=0
        j=0
        different_pairs=[]
        not_different_pairs=[]
        pvalues=[]
        for i in range(0,len(groups)-1):
            for j in range(i+1,len(groups)):
                
                result=test(dict_y[groups[i]],dict_y[groups[j]])
                pvalues.append(np.round(result.pvalue,4))
                if result.pvalue<0.05:
                    different_pairs.append(str(groups[i]+" and "+groups[j]+" p-value ("+str(np.round(result.pvalue,4))+")"))
                else:
                    not_different_pairs.append(str(groups[i]+" and "+groups[j]+" p-value ("+str(np.round(result.pvalue,4))+")"))


        message=""
        title=test_name+" test on "+str(names[0])+" grouped by "+str(names[1])
        if len(different_pairs)==0:
            message=" to determine that there is differences between any groups "
        else:
            message=" to determine that there is differences between the groups:\n"
            i=0
            for pair in different_pairs:
                message=message+"\t"+pair+"\n "
            
            if len(not_different_pairs)!=0:
                message=message+"\nThe following groups didn't show any differences: \n"
                for pair in not_different_pairs:
                    message=message+"\t"+pair+"\n "
        
       
        dialog=TestResultDialog(self,title,{'pvalue':pvalues},message,False)
        dialog.ShowModal()

    def OnLaunchResulDialog(self,test,test_name,variables,names,condition=True,msg=""):
        
        try:
            title=""
            message=""
            if len(variables)==2:
                result=test(variables[0],variables[1])
                a=names[0]
                b=names[1]
                title=str("Test "+test_name+" on "+a+" and "+b)
                message=str(msg+a+" and "+b)
            else:
                result=test(variables[0])
                title="Test "+test_name+" on "+names[0]
                message=msg

            dialog=TestResultDialog(self,title,{'pvalue':[result.pvalue]},message,condition)
            dialog.ShowModal()
        except Exception as exc:
            wx.MessageBox(str(exc),"Error",wx.ICON_ERROR)
        
    def OnChangeTest(self,event):
        test=self.combo_box_test.GetValue()
        current_selection=self.combo_box_B.GetValue()

        if test in StatisticTest.SINGLE_VARIABLE():
            self.combo_box_B.Enable(False)
            self.one_variable_test=True
        else:
            self.combo_box_B.Enable(True)
            self.one_variable_test=False

        if test in StatisticTest.GROUPING_SAME_VARIABLE():
            self.combo_box_B.Clear()

            if len(self.grouping)==0:
                self.combo_box_B.Enable(False)
            else:
                self.combo_box_B.Enable(True)

            self.combo_box_B.AppendItems(self.grouping)

            if current_selection in self.grouping:
                self.combo_box_B.SetValue(current_selection)

        elif test in StatisticTest.COMPARING_DIFFERENT_VARIABLES():
            self.combo_box_B.Clear()
            if len(self.comparing)==0:
                self.combo_box_B.Enable(False)
            else:
                self.combo_box_B.Enable(True)
            self.combo_box_B.AppendItems(self.comparing)

            if current_selection in self.comparing:
                self.combo_box_B.SetValue(current_selection)

        else:
           
            self.combo_box_B.Clear()
            self.combo_box_B.AppendItems(self.names)
   
class CleanDataDialog(wx.Dialog):
    def __init__(self,parent):
        # begin wxGlade: CleanDataDialog.__init__
        super(CleanDataDialog, self).__init__(parent)
        self.SetTitle("Clean data")
        self.SetFont(parent.GetFont())
        self.parent=parent
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.TOP, 15)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Missing Values"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL| wx.EXPAND, 10)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND,10)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 5)

        self.checkbox_delete_missing = wx.CheckBox(self, wx.ID_ANY, "Delete rows with missing values")
       
        sizer_7.Add(self.checkbox_delete_missing, 1, wx.ALL, 5)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_8, 0, wx.ALL | wx.EXPAND, 5)

        self.label_2 = wx.StaticText(self, wx.ID_ANY, "Sustitution strategy")
        sizer_8.Add(self.label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.combo_box_missing_sustitution = wx.ComboBox(self, wx.ID_ANY, choices=["None","Mean", "Median"],style=wx.CB_READONLY,value="None")
        sizer_8.Add(self.combo_box_missing_sustitution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.combo_box_missing_sustitution.Enable(False)
        self.label_2.Enable(False)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Outliers"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL|wx.EXPAND,10)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_9, 1, wx.ALL | wx.EXPAND, 5)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_12, 1, wx.ALL | wx.EXPAND, 5)

        self.checkbox_delete_outliers = wx.CheckBox(self, wx.ID_ANY, "Delete rows with outliers")
        sizer_12.Add(self.checkbox_delete_outliers, 0, wx.ALL, 5)
        

        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_11, 1, wx.ALL | wx.EXPAND, 5)

        self.checkbox_highlight_outliers = wx.CheckBox(self, wx.ID_ANY, "Highlight outliers")
        sizer_11.Add(self.checkbox_highlight_outliers, 0, wx.ALL, 5)
        self.checkbox_delete_missing.SetValue(1)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 1, wx.ALL | wx.EXPAND, 5)

        self.label_3 = wx.StaticText(self, wx.ID_ANY, "Sustitution strategy")
        sizer_10.Add(self.label_3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.combo_box_outlier_sustitution = wx.ComboBox(self, wx.ID_ANY, choices=["None","Mean", "Median","Adjust closer"],style=wx.CB_READONLY,value="None")
        sizer_10.Add(self.combo_box_outlier_sustitution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        ####
        sizer_10b = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_10b, 1, wx.ALL | wx.EXPAND, 5)

        self.label_lower = wx.StaticText(self, wx.ID_ANY, "Lower bounds")
        sizer_10b.Add(self.label_lower, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.lower_bounds=wx.SpinCtrlDouble(self,wx.ID_ANY,initial=0.25,min=0.0,max=1.0,inc=0.05)
        sizer_10b.Add(self.lower_bounds, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_10c = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_10c, 1, wx.ALL | wx.EXPAND, 5)

        self.label_upper = wx.StaticText(self, wx.ID_ANY, "Upper bounds")
        sizer_10c.Add(self.label_upper, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.upper_bounds=wx.SpinCtrlDouble(self,wx.ID_ANY,initial=0.75,min=0.0,max=1.0,inc=0.05)
        sizer_10c.Add(self.upper_bounds, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        ###

        sizer_12 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Apply to"), wx.HORIZONTAL)
        sizer_3.Add(sizer_12, 0, wx.ALL| wx.EXPAND, 10)
        options=parent.controller.get_names().get_response()['data']
        self.names=options
        options=list(options)
        options.append("All")
        self.combo_box_variable = wx.ComboBox(self, wx.ID_ANY, choices=options,style=wx.CB_READONLY,value="All")
        sizer_12.Add(self.combo_box_variable, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.progressbar=None
        
        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)


        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)
        
        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "Save configuration")
        sizer_2.AddButton(self.button_SAVE)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "Close")
        sizer_2.AddButton(self.button_CANCEL)

        self.Bind(wx.EVT_CHECKBOX,self.OnCheckMissing,self.checkbox_delete_missing)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckDeleteOutliers,self.checkbox_delete_outliers)
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box_variable)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Center()
        self.Layout()
        # end wxGlade

    def OnChangeVariable(self,event):
        target=self.combo_box_variable.GetValue()
        if target != "All":
            options=self.parent.controller.get_cleanse().get_response()
            if options['status']==Status.OK:
                options=options['data'][target]
                
                delete_missing=options['delete_missing']
                self.checkbox_delete_missing.SetValue(delete_missing)
                self._enable_options_missing(not delete_missing)
                self.combo_box_missing_sustitution.SetValue(options['substitute_missing'])

                delete_outliers=options['delete_outliers']
                self.checkbox_delete_outliers.SetValue(delete_outliers)
                self._enable_options_outliers(not delete_outliers)
                self.combo_box_outlier_sustitution.SetValue(options['substitute_outliers'])
                self.checkbox_highlight_outliers.SetValue(options['highlight_outliers'])
                self.upper_bounds.SetValue(options['upper_bound'])
                self.lower_bounds.SetValue(options['lower_bound'])
                
            else:
                wx.MessageBox(options['data'],"Error",wx.OK|wx.ICON_ERROR)

    def _enable_options_outliers(self,val):
        self.combo_box_outlier_sustitution.Enable(val)
        self.checkbox_highlight_outliers.Enable(val)
        self.label_3.Enable(val)
        """
        self.upper_bounds.Enable(val)
        self.lower_bounds.Enable(val)
        self.label_upper.Enable(val)
        self.label_lower.Enable(val)
        """
        
        
    def _enable_options_missing(self,val):
            self.combo_box_missing_sustitution.Enable(val)
            self.label_2.Enable(val)

    def OnCheckDeleteOutliers(self,event):
        checked=self.checkbox_delete_outliers.GetValue()

        if checked:
            self._enable_options_outliers(False)
        else:
            self._enable_options_outliers(True)

    def OnCheckMissing(self,event):

        checked=self.checkbox_delete_missing.GetValue()
        #variable=self.combo_box_variable.GetValue()
        
        if checked:
            self._enable_options_missing(False)
        else:
            self._enable_options_missing(True)

    def OnSave(self,event):
        try:
            target=self.combo_box_variable.GetValue()
            dm=self.checkbox_delete_missing.GetValue()
            sm=self.combo_box_missing_sustitution.GetValue()
            do=self.checkbox_delete_outliers.GetValue()
            so=self.combo_box_outlier_sustitution.GetValue()
            ho=self.checkbox_highlight_outliers.GetValue()
            upper_bound=self.upper_bounds.GetValue()
            lower_bound=self.lower_bounds.GetValue()

            if target == "All":
                #Cambiar todos
                for variable in self.names:
                    result=self.parent.controller.set_cleanse_option(variable,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so,'upper_bound':upper_bound,'lower_bound':lower_bound}).get_response()
                    
            else:
                result=self.parent.controller.set_cleanse_option(target,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so,'upper_bound':upper_bound,'lower_bound':lower_bound}).get_response()
            
            if result['status']== Status.OK:
                wx.MessageBox("Configuration succesfully saved ")
        except Exception as exc:
            wx.MessageBox(str(exc),"Error",wx.OK|wx.ICON_ERROR)
                
    def OnApply(self,event):
        self.button_APPLY.Disable()

        self.progressbar = wx.ProgressDialog("Applying cleanse", "Please, wait...", maximum=100,parent=self)
        #self.execute_thread()
        thread = threading.Thread(target=self.execute_thread)
        thread.start()
        #thread.join()
        """
        options=self.parent.controller.get_cleanse().get_response()
        deleted=0
        modified=0
        if options['status']==Status.OK:
            #HERE

            for variable in options['data']:
                response=self.parent.controller.apply_cleanse(variable).get_response()
                
                if response['status']==Status.OK:
                    d=response['data']['deleted_rows']
                    m=response['data']['modified_rows']
                    deleted+=d
                    modified+=m
                else:
                    wx.MessageBox(str("A problem has ocurred with "+variable+" process"),"Error",wx.OK|wx.ICON_ERROR)
            
            wx.MessageBox(str(str(deleted)+" deleted and "+str(modified)+" modified rows."),"Info")
            self.EndModal(wx.ID_APPLY)

        else:
            wx.MessageBox(options['data'],"Error",wx.OK|wx.ICON_ERROR)
        """
        
            
    def execute_thread(self):
        options=self.parent.controller.get_cleanse().get_response()
        deleted=0
        modified=0
        if options['status']==Status.OK:
            #HERE
            i=0
            shift=100/len(options['data'])
            for variable in options['data']:
                response=self.parent.controller.apply_cleanse(variable).get_response()
                
                if response['status']==Status.OK:
                    d=response['data']['deleted_rows']
                    m=response['data']['modified_rows']
                    deleted+=d
                    modified+=m
                else:
                    wx.MessageBox(str("A problem has ocurred with "+variable+" process"),"Error",wx.OK|wx.ICON_ERROR)
                
                time.sleep(0.01)
                wx.CallAfter(self.update_progress, int(i))
                i+=shift

            wx.CallAfter(self.progressbar.Update,self.progressbar.GetRange())
        
            wx.CallAfter(self.parent.controller.confirm_delete)

            wx.CallAfter(wx.MessageBox,str(str(deleted)+" rows deleted and "+str(modified)+" cells modified."),"Info")
            
            wx.CallAfter(self.EndModal,wx.ID_APPLY)
            wx.CallAfter(self.Destroy)

        else:
            wx.MessageBox(options['data'],"Error",wx.OK|wx.ICON_ERROR)

    def update_progress(self, value):
        
        self.progressbar.Update(value,"Progress...")

class GraphDialog(wx.Dialog):
    def __init__(self,parent):

        super(GraphDialog, self).__init__(parent)
        self.SetTitle("Graph")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller

        resp=self.controller.get_names().get_response()
        self.string_variable=parent.string_variable_names

        if resp['status'] == Status.OK:
            names=resp['data']
            names=list(names)
        else:
            wx.MessageBox("A problem has occurred")
            self.Close()
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 5)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "X Axis")
        sizer_6.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.listbox_x_axis = wx.ListBox(self, wx.ID_ANY, choices=names)
        sizer_6.Add(self.listbox_x_axis, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_7, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Left Y Axis")
        sizer_7.Add(label_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.listbox_y_axis = wx.ListBox(self, wx.ID_ANY, choices=names)
        sizer_7.Add(self.listbox_y_axis, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        ##

        sizer_7b = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_7b, 1, wx.EXPAND, 0)

        label_2b = wx.StaticText(self, wx.ID_ANY, "Right Y Axis")
        sizer_7b.Add(label_2b, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.listbox_yb_axis = wx.ListBox(self, wx.ID_ANY, choices=names)
        sizer_7b.Add(self.listbox_yb_axis, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.listbox_yb_axis.Enable(False)
        ##
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_8, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Z Axis")
        sizer_8.Add(label_3, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.listbox_z_axis = wx.ListBox(self, wx.ID_ANY, choices=names)
        sizer_8.Add(self.listbox_z_axis, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_9, 0, wx.EXPAND, 0)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Type"), wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_11 = wx.GridBagSizer(0, 0)
        sizer_10.Add(sizer_11, 1, wx.ALL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 10)

        self.radio_btn_2d_graph = wx.RadioButton(self, wx.ID_ANY, "2D Graph")
        sizer_11.Add(self.radio_btn_2d_graph, (0, 0), (1, 1), wx.ALL, 5)
        
        self.radio_btn_3d_graph = wx.RadioButton(self, wx.ID_ANY, "3D Graph")
        sizer_11.Add(self.radio_btn_3d_graph, (0, 1), (1, 1), wx.ALL, 5)
        self.radio_btn_3d_graph.SetValue(1)

        self.radio_btn_frequency = wx.RadioButton(self, wx.ID_ANY, "Histogram")
        sizer_11.Add(self.radio_btn_frequency, (0, 2), (1, 1), wx.ALL, 5)

        self.radio_btn_box_plot = wx.RadioButton(self, wx.ID_ANY, "Box plot")
        sizer_11.Add(self.radio_btn_box_plot, (0, 3), (1, 1), wx.ALL, 5)

        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(sizer_12, 1, wx.ALL | wx.EXPAND, 10)

        self.checkbox_regression_line = wx.CheckBox(self, wx.ID_ANY, "Show Linear Regression Fit Line")
        sizer_12.Add(self.checkbox_regression_line, 1, wx.ALL | wx.EXPAND, 10)
        self.checkbox_regression_line.Enable(False)

        sizer_13 = wx.GridBagSizer(0, 0)
        sizer_12.Add(sizer_13, 1, wx.ALL | wx.EXPAND, 5)

        label_number_bins = wx.StaticText(self, wx.ID_ANY, "Number of Bins")
        sizer_13.Add(label_number_bins, (0, 0), (1, 1), wx.ALL, 10)

        self.input_number_bins = wx.SpinCtrl(self, wx.ID_ANY, min=0, max=100,initial=10)
        sizer_13.Add(self.input_number_bins, (0, 1), (1, 1), wx.ALL | wx.EXPAND, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_OK = wx.Button(self, wx.ID_OK, "Plot")
        #self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)


        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_frequency)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_3d_graph)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_2d_graph)
        self.Bind(wx.EVT_BUTTON,self.OnHelp,self.button_HELP)
        self.Bind(wx.EVT_BUTTON,self.generate_graph,self.button_OK)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()

    def OnHelp(self,evt):
        dialog=HelpDialog(self,"./front/resources/help/plot_help.json","Plot functions help")
        dialog.ShowModal()
        
    def OnChangeType(self,evt):
        
        if self.radio_btn_frequency.GetValue():
            
            self.listbox_y_axis.Enable(False)
            self.listbox_z_axis.Enable(False)
            self.listbox_yb_axis.Enable(False)
            self.checkbox_regression_line.Enable(False)

        elif self.radio_btn_2d_graph.GetValue():
            
            self.listbox_y_axis.Enable(True)
            self.listbox_yb_axis.Enable(True)
            self.listbox_z_axis.Enable(False)
            self.checkbox_regression_line.Enable(True)
        else:
            
            self.listbox_y_axis.Enable(True)
            self.listbox_yb_axis.Enable(False)
            self.listbox_z_axis.Enable(True)
            self.checkbox_regression_line.Enable(False)

    def _validate_selection(self,value,name):
        if value=="":
            return False
        else:
            return True
    def generate_graph(self,evt):
        data=self.controller.get_data().get_response()
        if data['status']==Status.OK:
            data=data['data']
        else:
            wx.MessageBox("An error has ocurred","Error",wx.OK|wx.ICON_ERROR)
        x=self.listbox_x_axis.GetStringSelection()
        y=self.listbox_y_axis.GetStringSelection()
        y_right=self.listbox_yb_axis.GetStringSelection()
        z=self.listbox_z_axis.GetStringSelection()

        entered_x=self._validate_selection(x,"x")
        if not entered_x:
            wx.MessageBox("You must be select X axis variable","Error",wx.OK|wx.ICON_ERROR)
        else:
            if self.radio_btn_2d_graph.GetValue():
                
                options={}
                arg={'x':{'name':x,'data':data[x]},'y':{'name':'','data':''},
                            'y_right':{'name':'','data':''}}
                
                entered_y=self._validate_selection(y,"left y")
                if entered_y:
                    arg['y']['name']=y
                    arg['y']['data']=data[y]

                entered_y_right=self._validate_selection(y_right,"right y")
                if entered_y_right:
                    arg['y_right']['name']=y_right
                    arg['y_right']['data']=data[y_right]

                if not entered_y and not entered_y_right:
                    wx.MessageBox(str("You must be select either left or right Y axis variable"),"Error",wx.OK|wx.ICON_ERROR)
                else:
                    plot_2d(arg)
                    if self.checkbox_regression_line.GetValue():
                        if self._validate_selection(y,"left y"):
                            plot_regression({'x':{'name':x,'data':data[x]},'y':{'name':y,'data':data[y]}})
                        if self._validate_selection(y_right,"right y"):
                            plot_regression({'x':{'name':x,'data':data[x]},'y':{'name':y_right,'data':data[y_right]}})

            if self.radio_btn_3d_graph.GetValue():
                
                if y==z or y==x or z==x:
                    wx.MessageBox("The same variable can not be selected for various axis","Error",wx.OK|wx.ICON_ERROR)
                elif x in self.string_variable or y in self.string_variable or z in self.string_variable:
                    wx.MessageBox("A nomial variable can not be selected for 3D graph","Error",wx.OK|wx.ICON_ERROR)
                else:
                    if self._validate_selection(y,"left y") and self._validate_selection(z,"z"):
                        
                        plot_3d({'x':{'name':x,'data':data[x]},'y':{'name':y,'data':data[y]},'z':{'name':z,'data':data[z]}})
                    else:
                        wx.MessageBox("You must select Y and Z axis","Error",wx.OK|wx.ICON_ERROR)
            if self.radio_btn_frequency.GetValue():
                bins=self.input_number_bins.GetValue()
                if bins<1:
                    wx.MessageBox("Invalid number of bins","Error",wx.OK|wx.ICON_ERROR)
                else:
                    options={'bins':bins}

                    plot_hist({'x':{'name':x,'data':data[x]}},options)

            if self.radio_btn_box_plot.GetValue():
                if x in self.string_variable:
                    wx.MessageBox("Could not generate box plot for a nominal variable","Warning",wx.ICON_WARNING)
                else:   
                    plot_boxplot({'x':{'name':x,'data':data[x]}})

class SummaryDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(SummaryDialog, self).__init__(parent)
        self.SetSize((900,530))
        self.SetFont(parent.GetFont())
        self.SetTitle("Summary")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.parent=parent
        self.IO=parent.IO
        self.names=parent.names
        self.summary=parent.controller.get_summary().get_response()
        
        if self.summary['status']== Status.OK:
            self.names=self.names
            self.summary=self.summary['data']
        else:
            wx.MessageBox("A problem has occurred")


        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Statistics"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 10)
        
        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_1=self.createDataGrid(self.grid_1,len(self.names))
        
        sizer_3.Add(self.grid_1, 1, wx.ALL | wx.EXPAND, 5)

        sizer_1_groupby = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Plot"), wx.HORIZONTAL)
        sizer_1.Add(sizer_1_groupby, 0,wx.ALL | wx.EXPAND, 10)

        sizer_2_groupby = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1_groupby.Add(sizer_2_groupby, 1, wx.EXPAND, 0)

        sizer_groupby = wx.BoxSizer(wx.VERTICAL)
        sizer_2_groupby.Add(sizer_groupby, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        label_group_by = wx.StaticText(self, wx.ID_ANY, "Group by")
        sizer_groupby.Add(label_group_by, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.combo_box_group = wx.ComboBox(self, wx.ID_ANY, choices=self.parent.string_variable_names,value="None", style=wx.CB_READONLY)
        sizer_groupby.Add(self.combo_box_group, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        if len(self.parent.string_variable_names)==0:
            self.combo_box_group.Enable(False)

        self.numeric_variables=self.parent.int_variable_names+self.parent.float_variable_names

        self.list_box_variables = wx.ListBox(self, wx.ID_ANY, choices=self.numeric_variables,style=wx.LB_MULTIPLE)
        sizer_2_groupby.Add(self.list_box_variables, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        self.button_plot = wx.Button(self, wx.ID_ANY, "Generate graph")
        sizer_2_groupby.Add(self.button_plot, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)


        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_OK = wx.Button(self, wx.ID_OK, "Save")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)


        self.Bind(wx.EVT_BUTTON,self.OnPlot,self.button_plot)
        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_OK)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        

    def OnPlot(self,event):
        group=self.combo_box_group.GetValue()
        variables=self.list_box_variables.GetSelections()
        indexes=[]
        
        for i in variables:
            name=self.numeric_variables[i]
            indexes.append(list(self.parent.names).index(name))
        
        
        if len(variables)==0:
            wx.MessageBox("You must select variables","Warning",wx.OK|wx.ICON_WARNING)
        else:
            if group!="":
                indexes.append(list(self.parent.names).index(group))

            code=wx.OK
            if len(indexes)>5:
                code=wx.MessageBox(str("You have selected "+str(len(indexes)-1)+" variables this will create a hard to read plot and could take a few minutes to generate"),"Warning",wx.OK|wx.CANCEL|wx.ICON_WARNING)
            
            if code==wx.OK:
                response=self.parent.controller.get_data().get_response()

                if response['status']!=Status.OK:
                    wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
                else:
                    data=response['data']
                    plot_general_group(data.iloc[:,indexes],group)
        

    def OnSave(self,event):
        result=self.IO.GetPath(self,message="Save summary",wildcard=WILDCARD_DATA_FILE).get_response()
        
        if result['status'] == Status.OK:
            path=result['data']
            
            Saver(path,self.summary,True).save()
            cadena=str("File saved succesfully in "+path)
            wx.MessageBox(cadena,"Info")
        elif result['status'] != Status.CANCEL:
            wx.MessageBox("A problem has occurred","Error",wx.OK|wx.ICON_ERROR)


    def createDataGrid(self,myGrid,rows):
        
        myGrid.CreateGrid(rows,9)
        myGrid.SetRowLabelSize(0)
        col=0
        
        myGrid.SetColLabelValue(col,'Variable')
        col+=1
        names=self.names

        metrics=self.summary.index

        for index in metrics:
            myGrid.SetColLabelValue(col,index)
            col+=1

        i=0 
        j=0
        
        for variable in names:
            if not variable in self.parent.string_variable_names:
                j=0
                myGrid.SetCellValue(i,j,str(variable))
                j+=1
                #myGrid.SetCellBackgroundColour(i, j, wx.Colour('#2c8a45'))
                
                for index in self.summary.index:
                    value=self.summary[[variable]].loc[index]
                    
                    myGrid.SetCellValue(i,j," "+str(round(value.values[0],2))+" ")
                    myGrid.SetReadOnly(i,j,True)
                    j+=1        
                i+=1

        myGrid.AutoSizeColumn(0,True)

        return myGrid

