import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from front.IO.IOManage import IOManage
from back.data.contextData import ContextData
from back.respuestas import Status
from back.statistic.statistic import StatisticTest
from back.saver import Saver
from back.validation.validation import Validator
from back.tracer import Trace
from ..plots import plot_barplot_object,plot_barplot,plot_2d,plot_3d,plot_hist, plot_regression,plot_boxplot,plot_correlation_matrix,plot_countplot,plot_histogram_grouped, plot_general_group,plot_covariance_matrix
import numpy as np
import copy
import math
import threading
import time
import re
from wx.lib.stattext import GenStaticText
from ..constants import WILCARD_TASK,WILDCARD_DATA_FILE,WILDCARD_TEXT_FILE
from .functions import get_task_name,validate_name,validate_range
import sys
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx.html2 as wxhtml2
import json
import os 


class VariableTypeDialog(wx.Dialog):
    def __init__(self,parent):
        # begin wxGlade: VariableTypeDialog.__init__
        super(VariableTypeDialog, self).__init__(parent, size = (1000,1000)) 
        
        self.SetTitle("Select variables type")
        
        self.setting=parent.setting
        self.IO=IOManage()
        self.controller=parent.controller
        self.metrics=self.controller.get_summary().getResponse()['data']
        #Datos globales
        self.data=pd.DataFrame()

        self.remove_non_used_variables=False
        self.independent_variables=[]
        self.targets=[]
        self.names=self.controller.get_names().getResponse()['data']
        

        #contador de referencias para limpieza de memoria manual
        self.count=0
        self.object=None

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Select information for rules "), wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 20)

        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid=self.createDataGrid(self.grid,len(self.names))
        sizer_3.Add(self.grid, 1, wx.ALL | wx.CENTER, 10)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 15)

        #label_non_used_check_box = wx.StaticText(self, wx.ID_ANY, "Remove non used variables from sheet")
        #sizer_4.Add(label_non_used_check_box, 1, wx.ALL, 10)

        self.checkbox_1 = wx.CheckBox(self, wx.ID_ANY, "Remove non used variables from sheet")
        sizer_4.Add(self.checkbox_1, 1, wx.ALL, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,self.OnUpdateType)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        #self.Bind(wx.EVT_BUTTON,self.OnCancel,self.button_CANCEL)
       

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        #self.SetEscapeId(self.button_CANCEL.GetId())
        
        self.Center()
        self.Layout()
        # end wxGlade

    def ClearMemory(self):
        for ref in range(self.count):
            self.object.DecRef()

            
    def OnCancel(self,event):
        
        self.ClearMemory()
        self.Close(wx.CANCEL)


    def OnApply(self,event):
        if len(self.independent_variables)==0:
            wx.MessageBox('You must select one or more ingredients', 'Error', wx.OK | wx.ICON_WARNING)
        elif len(self.targets)==0:
            wx.MessageBox('You must select one or more properties', 'Error', wx.OK | wx.ICON_WARNING)
        else:
            self.controller.set_independent_variables(self.independent_variables)
            self.controller.set_targets(self.targets)
            
            self.ClearMemory()
            self.EndModal(wx.OK)
            self.Destroy()


    def OnUpdateType(self,event):
        row,col=event.GetRow(),event.GetCol()

        if col == self.grid.GetNumberCols()-1:
            val=self.grid.GetCellValue(row,col)

            if val=='Property':
                self.grid.SetCellBackgroundColour(row, col, wx.Colour('#ad9e72'))
                self.targets.append(row)
                if row in self.independent_variables:
                    self.independent_variables.remove(row)
                
            elif val=='Ingredient':
                self.grid.SetCellBackgroundColour(row, col, wx.Colour('#5a8f68'))
                self.independent_variables.append(row)
                if row in self.targets:
                    self.targets.remove(row)
            else:
                self.grid.SetCellBackgroundColour(row, col, wx.Colour('#ffffff'))
                if row in self.independent_variables:
                    self.independent_variables.remove(row)
                if row in self.targets:
                    self.targets.remove(row)


    def createDataGrid(self,myGrid,rows):
        
        try:
            myGrid.CreateGrid(rows,1)
            myGrid.SetRowLabelSize(0)
            
            names=self.controller.get_names().getResponse()['data']

            myGrid.SetColLabelValue(0,'Variable')
                
            i=0 
            j=0
            
            
            for variable in names:
                myGrid.SetCellValue(i,j,str(variable))
                i+=1
                    
            myGrid.AppendCols(1)
            myGrid.SetColLabelValue(myGrid.GetNumberCols() - 1," Type ")
            
            opciones_dropdown = ['Ignore','Property', 'Ingredient']

            
            
            editor_dropdown = gridlib.GridCellChoiceEditor(opciones_dropdown, allowOthers=False)
            self.object=editor_dropdown
            count=0
            for row in range(myGrid.GetNumberRows()):
                col = myGrid.GetNumberCols() - 1
                count+=1
                myGrid.SetCellEditor(row, col, editor_dropdown) ## LANZA EXCEPCION                
                myGrid.SetCellValue(row, col, opciones_dropdown[0])
                
            myGrid.AutoSize()
            myGrid.SetColSize(myGrid.GetNumberCols() - 1,100)
            myGrid.ShowScrollbars(wx.SHOW_SB_NEVER,wx.SHOW_SB_NEVER)

        except Exception as exc:
            print("Error"+str(exc))
        return myGrid


class RulesDialog(wx.Dialog):
    def __init__(self,parent,rules):
        
        super(RulesDialog, self).__init__(parent)
        self.SetTitle("Rules")
        
        self.SetSize((500,500))
        
        self.rules_to_string=""

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Generated Rules"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        self.rules_text_field = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer_3.Add(self.rules_text_field, 1, wx.ALL | wx.EXPAND, 5)
        self.writeRules(rules)
        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        
        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        
        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

    
        sizer_2.Realize()
        
        self.SetSizer(sizer_1)
        #sizer_1.Fit(self)

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        
        self.Center()
        self.Layout()
        

    def OnSave(self,event):
        
        
        result=IOManage.OnSaveAs(self,event,self.rules_to_string,message="Save rules",wildcard=".txt files (*.txt)|*.txt").getResponse()
        if result['status']:
            
            cadena=str("Archivo guardado con éxito en "+result['data'])
            
            wx.MessageBox(cadena,"Info")
            
        else:
            wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)

    def writeRules(self,rules):
        cadena="Rules:\n"
        for i in rules[0]:
            
            cadena=cadena+ i + "\n\n"
        
        self.rules_to_string=cadena
        self.rules_text_field.SetValue(cadena)
        

class CleanDataDialog(wx.Dialog):
    def __init__(self,parent,controller,settings):
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
        options=parent.controller.get_names().getResponse()['data']
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
            options=self.parent.controller.get_cleanse().getResponse()
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
                    result=self.parent.controller.set_cleanse_option(variable,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so,'upper_bound':upper_bound,'lower_bound':lower_bound}).getResponse()
                    
            else:
                result=self.parent.controller.set_cleanse_option(target,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so,'upper_bound':upper_bound,'lower_bound':lower_bound}).getResponse()
            
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
        options=self.parent.controller.get_cleanse().getResponse()
        deleted=0
        modified=0
        if options['status']==Status.OK:
            #HERE

            for variable in options['data']:
                response=self.parent.controller.apply_cleanse(variable).getResponse()
                
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
        options=self.parent.controller.get_cleanse().getResponse()
        deleted=0
        modified=0
        if options['status']==Status.OK:
            #HERE
            i=0
            shift=100/len(options['data'])
            for variable in options['data']:
                response=self.parent.controller.apply_cleanse(variable).getResponse()
                
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
        # begin wxGlade: GraphDialog.__init__


        super(GraphDialog, self).__init__(parent)
        self.SetTitle("Graph")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller

        resp=self.controller.get_names().getResponse()
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
        # end wxGlade

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
        data=self.controller.get_data().getResponse()
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
                    plot_2d(arg,options)
                    if self.checkbox_regression_line.GetValue():
                        if self._validate_selection(y,"left y"):
                            plot_regression({'x':{'name':x,'data':data[x]},'y':{'name':y,'data':data[y]}},options)
                        if self._validate_selection(y_right,"right y"):
                            plot_regression({'x':{'name':x,'data':data[x]},'y':{'name':y_right,'data':data[y_right]}},options)

            if self.radio_btn_3d_graph.GetValue():
                
                if y==z or y==x or z==x:
                    wx.MessageBox("The same variable can not be selected for various axis","Error",wx.OK|wx.ICON_ERROR)
                elif x in self.string_variable or y in self.string_variable or z in self.string_variable:
                    wx.MessageBox("A nomial variable can not be selected for 3D graph","Error",wx.OK|wx.ICON_ERROR)
                else:
                    if self._validate_selection(y,"left y") and self._validate_selection(z,"z"):
                        options={}
                        plot_3d({'x':{'name':x,'data':data[x]},'y':{'name':y,'data':data[y]},'z':{'name':z,'data':data[z]}},options)
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
                options={}
                if x in self.string_variable:
                    wx.MessageBox("Could not generate box plot for a nominal variable","Warning",wx.ICON_WARNING)
                else:   
                    plot_boxplot({'x':{'name':x,'data':data[x]}},options)



class SummaryDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(SummaryDialog, self).__init__(parent)
        self.SetSize((900,530))
        self.SetFont(parent.GetFont())
        self.SetTitle("Summary")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        
        self.parent=parent
        self.IO=parent.IO
        self.names=parent.names#parent.controller.get_names().getResponse()
        self.summary=parent.controller.get_summary().getResponse()
        
        if self.summary['status']== Status.OK:
            self.names=self.names#self.names['data']
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

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_OK)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade

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
                response=self.parent.controller.get_data().getResponse()

                if response['status']!=Status.OK:
                    wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
                else:
                    data=response['data']
                    plot_general_group(data.iloc[:,indexes],group)
        

    def OnSave(self,event):
        result=self.IO.OnSaveAs(self,message="Save summary",wildcard="(*.csv)|*.csv|(*.xlsx)|*.xlsx").getResponse()
        
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
               


class AboutUsDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(AboutUsDialog, self).__init__(parent)
        self.SetTitle("About us")
        self.SetFont(parent.GetFont())
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 50)

        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("./front/resources/img/logo_128x128.png", wx.BITMAP_TYPE_ANY))
        sizer_3.Add(bitmap_1, 0, wx.ALL | wx.EXPAND, 30)

        label_1 = wx.StaticText(self, wx.ID_ANY, "NeuroRule")
        label_1.SetFont(wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "V 1.0.0")
        label_2.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_3.Add(label_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

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
        # end wxGlade

class ShowHiddenDialog(wx.Dialog):
    def __init__(self,parent):
        # begin wxGlade: ShowHiddenDialog.__init__
        super(ShowHiddenDialog, self).__init__(parent)
        self.SetTitle("Show Hidden Columns")
        self.SetFont(parent.GetFont())
        self.parent=parent
        self.names=parent.names[parent.hidden_columns]
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Select hidden variables"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 10)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.names,style=wx.LB_MULTIPLE)
        sizer_3.Add(self.list_box_1, 1, wx.ALL | wx.EXPAND, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        # end wxGlade

    def OnApply(self,event):
        choices=self.list_box_1.GetSelections()
        if len(choices)==0:
            wx.MessageBox("You have not selected any variable","Info")
        else:
            self.parent.names_to_show=self.names[choices]
            
            self.EndModal(wx.OK)
            self.Destroy()

class ShowIdentifierColsDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(ShowIdentifierColsDialog, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Show identifier Columns")
        self.parent=parent
        self.names=copy.deepcopy(parent.identifier_cols)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Select columns"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 10)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.names,style=wx.LB_MULTIPLE)
        sizer_3.Add(self.list_box_1, 1, wx.ALL | wx.EXPAND, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "Unset")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        

    def OnApply(self,event):
        choices=self.list_box_1.GetSelections()
        if len(choices)==0:
            wx.MessageBox("You have not selected any variable","Info")
        else: 
            for var in choices:
                self.parent.identifier_cols.remove(self.names[var])
            
            self.EndModal(wx.OK)
            self.Destroy()
        
            


class StatisticDialog(wx.Dialog):
    def __init__(self,parent, *args, **kwds):
        # begin wxGlade: StatisticDialog.__init__
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
        if self.checkbox_corr.GetValue() or self.checkbox_covariance.GetValue() or self.checkbox_automatic_tests.GetValue():
            self.EnableComponents(False)
        else:
            self.EnableComponents(True)

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
            shape=self.controller.get_data_shape().getResponse()['data']
            code=wx.YES
            classes=self.controller.get_nominal_classes().getResponse()['data']

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
            df=self.controller.get_data().getResponse()['data']
            
            df=df.drop(self.identifier_cols,axis=1)
            if self.checkbox_corr.GetValue():
                plot_correlation_matrix(df)
            if self.checkbox_covariance.GetValue():
                plot_covariance_matrix(df)

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
                            y=self.controller.get_column(index_b).getResponse()['data']
                            complete=True
                    
                    index_a=self.names.index(a)
                    x=self.controller.get_column(index_a).getResponse()['data']
                    if 'Shapiro' in test:   
                        self.OnLaunchResulDialog(StatisticTest.shapiro_wilk,test,variables=[x],names=[a],condition=True,msg="to determine that this variable has a normal distribution")
                    elif 'ANOVA' in test and complete:
                        """
                        
                        grouping_values=np.unique(y)
                        if len(grouping_values)<5:
                            dict_y={}
                            for group in grouping_values:
                                dict_y[group]=x[y==group]

                            self.OnLaunchGroupingResultDialog(StatisticTest.ANOVA,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
                        else:
                            wx.MessageBox("There is too many groups to perform the test.","Warning",wx.ICON_WARNING)
                        """
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.ANOVA)
                    elif 'T Student' in test and complete:
                        """
                        grouping_values=np.unique(y)
                        if len(grouping_values)<5:
                            dict_y={}
                            for group in grouping_values:
                                dict_y[group]=x[y==group]

                            self.OnLaunchGroupingResultDialog(StatisticTest.t_student,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
                        else:
                            wx.MessageBox("There is too many groups to perform the test.","Warning",wx.ICON_WARNING)
                        """
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.t_student)
                    elif 'Kruskal Wallis' in test and complete:
                        """
                        grouping_values=np.unique(y)
                        if len(grouping_values)<5:
                            dict_y={}
                            for group in grouping_values:
                                dict_y[group]=x[y==group]

                            self.OnLaunchGroupingResultDialog(StatisticTest.kruskal_wallis,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
                        else:
                            wx.MessageBox("There is too many groups to perform the test.","Warning",wx.ICON_WARNING)
                        """
                        self._differencesGroupTemplate(y,x,a,b,test,StatisticTest.kruskal_wallis)
                    elif 'Wilcoxon' in test and complete:
                        """
                        
                        grouping_values=np.unique(y)

                        if len(grouping_values)<5:
                            dict_y={}
                            for group in grouping_values:
                                dict_y[group]=x[y==group]

                            self.OnLaunchGroupingResultDialog(StatisticTest.wilcoxon,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
                        else:
                            wx.MessageBox("There is too many groups to perform the test.","Warning",wx.ICON_WARNING)
                        """
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
            #self.text_ctrl_1.SetMinSize((70, 23))
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

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_OK)
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeAllVariables,self.checkbox_all_variable)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box__variable)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade
    
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
                



class SingleSummaryDialog(wx.Dialog):
    def __init__(self, parent,variable,group,numeric=True):
        # begin wxGlade: SingleSummaryDialog.__init__
        
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
        #Obtain summary
        if group=="None" or not numeric:
            group=None
            isGrouped=False
            message=variable
            label="Name"
            if numeric:
                plottable=False

        response=parent.controller.get_variable_summary(variable,group).getResponse()
        
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
        # end wxGlade
    

    def plot_histogram(self,evt):
        
    
        response=self.parent.controller.get_column(list(self.parent.names).index(self.variable)).getResponse()
        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
        else:
            x=response['data']
            
            if self.numeric:
                response=self.parent.controller.get_column(list(self.parent.names).index(self.group)).getResponse()
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
            #grid.SetCellBackgroundColour(i,j,wx.Colour(176,181,177))
            j+=1
            #myGrid.SetCellBackgroundColour(i, j, wx.Colour('#2c8a45'))
            for index in data.index:
                value=data.loc[index]
                if self.numeric:
                    value=round(value,2)
                grid.SetCellValue(i,j," "+str(value)+" ")
                grid.SetReadOnly(i,j,True)
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                #grid.SetCellBackgroundColour(i,j,wx.Colour(176,181,177))
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
          
class CreateTaskDialog(wx.Dialog):
    def __init__(self,parent):
    
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Create task")
        self.SetFont(parent.GetFont())
        
        ##variables
        self.inputs=[]
        for index in parent.controller.get_independent_indexes().getResponse()['data']:
            self.inputs.append(parent.names[index])

        self.outputs=[]
        for index in parent.controller.get_target_indexes().getResponse()['data']:
            self.outputs.append(parent.names[index])        

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Variable information"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 5)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 5)

        label_inputs = wx.StaticText(self, wx.ID_ANY, "Inputs")
        sizer_6.Add(label_inputs, 0, 0, 0)

        self.list_box_inputs = wx.ListBox(self, wx.ID_ANY, choices=self.inputs)
        sizer_6.Add(self.list_box_inputs, 0, 0, 0)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 5)

        label_outputs = wx.StaticText(self, wx.ID_ANY, "Outputs")
        sizer_7.Add(label_outputs, 0, 0, 0)

        self.list_box_outputs = wx.ListBox(self, wx.ID_ANY, choices=self.outputs)
        sizer_7.Add(self.list_box_outputs, 0, 0, 0)
        
        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Apply to"), wx.HORIZONTAL)
        sizer_3.Add(sizer_8, 0, wx.ALL | wx.EXPAND, 10)

        self.variables_options=['All']+self.outputs
        self.choice_target = wx.Choice(self, wx.ID_ANY, choices=self.variables_options)
        self.choice_target.SetSelection(0)
        sizer_8.Add(self.choice_target, 1, wx.ALL, 5)

        self.notebook_1 = wx.Notebook(self, wx.ID_ANY)
        sizer_3.Add(self.notebook_1, 1, wx.EXPAND, 0)

        self.notebook_1.SetBackgroundColour(wx.Colour(240,240,240,255))

        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.notebook_1_pane_1, "Model")

        sizer_9 = wx.BoxSizer(wx.VERTICAL)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_1_pane_1, wx.ID_ANY, "Rule generating"), wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 0, wx.ALL | wx.EXPAND, 5)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10.Add(sizer_12, 1, wx.EXPAND, 0)

        self.radio_btn_generate_rules = wx.RadioButton(self.notebook_1_pane_1, wx.ID_ANY, "Generate rules")
        sizer_12.Add(self.radio_btn_generate_rules, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.options_neurofuzzy = wx.Button(self.notebook_1_pane_1, wx.ID_ANY, "Options")
        sizer_12.Add(self.options_neurofuzzy, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_11 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_1_pane_1, wx.ID_ANY, "Prediction"), wx.HORIZONTAL)
        sizer_9.Add(sizer_11, 0, wx.ALL | wx.EXPAND, 5)

        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(sizer_13, 0, wx.EXPAND, 0)

        self.radio_btn_prediction = wx.RadioButton(self.notebook_1_pane_1, wx.ID_ANY, "Generate prediction model")
        sizer_13.Add(self.radio_btn_prediction, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.options_models = wx.Button(self.notebook_1_pane_1, wx.ID_ANY, "Options")
        sizer_13.Add(self.options_models, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1.AddPage(self.notebook_1_pane_2, "Validation")

        sizer_14 = wx.BoxSizer(wx.VERTICAL)

        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14.Add(sizer_15, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)

        label_validation = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, "Method")
        sizer_15.Add(label_validation, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.choice_validation = wx.Choice(self.notebook_1_pane_2, wx.ID_ANY, choices=["Cross validation","CV - Leave one out","Structural RisK Minimization"])
        self.choice_validation.SetSelection(0)
        sizer_15.Add(self.choice_validation, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14.Add(sizer_16, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        sizer_17 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_1_pane_2, wx.ID_ANY, "SRM"), wx.VERTICAL)
        sizer_16.Add(sizer_17, 0, wx.ALL | wx.EXPAND, 10)

        sizer_20 = wx.BoxSizer(wx.VERTICAL)
        sizer_17.Add(sizer_20, 1, wx.EXPAND, 0)

        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20.Add(sizer_21, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        label_c1 = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, "C1")
        sizer_21.Add(label_c1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.spin_ctrl_C1 = wx.SpinCtrlDouble(self.notebook_1_pane_2, wx.ID_ANY, initial=1.5, min=0.0, max=100.0)
        self.spin_ctrl_C1.SetDigits(2)
        sizer_21.Add(self.spin_ctrl_C1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.checkbox_auto_scale = wx.CheckBox(self.notebook_1_pane_2, wx.ID_ANY, "Auto scale")
        sizer_20.Add(self.checkbox_auto_scale, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_18 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_1_pane_2, wx.ID_ANY, "CV"), wx.VERTICAL)
        sizer_16.Add(sizer_18, 0, wx.ALL | wx.EXPAND, 10)

        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18.Add(sizer_19, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        label_subset = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, "Subsets")
        sizer_19.Add(label_subset, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.spin_ctrl_cv_subset = wx.SpinCtrl(self.notebook_1_pane_2, wx.ID_ANY, "0",initial=10, min=0, max=100)
        sizer_19.Add(self.spin_ctrl_cv_subset, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_CREATE = wx.Button(self, wx.ID_OK, "")
        self.button_CREATE.SetDefault()
        sizer_2.AddButton(self.button_CREATE)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.notebook_1_pane_2.SetSizer(sizer_14)

        self.notebook_1_pane_1.SetSizer(sizer_9)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_CREATE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        #self.Bind(wx.EVT_BUTTON,lambda event: self.OnChangeInputsOutputs(event,parent),self.change_inputsOuputs)
        self.Bind(wx.EVT_BUTTON,self.OnRulesOptions,self.options_neurofuzzy)
       
        self.Center()
        self.Layout()
        # end wxGlade

    def OnChangeInputsOutputs(self,evt,parent):
        dialog=VariableTypeDialog(parent)
        dialog.Show()

    def OnRulesOptions(self,evt):
        options={}
        dialog=RulesOptionsDialog(self,options)
        code=dialog.ShowModal()

class RulesOptionsDialog(wx.Dialog):
    def __init__(self,parent,options):
        
        super(RulesOptionsDialog, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Rules generating options")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Neurofuzzy network"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 0, wx.ALL | wx.EXPAND, 10)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 0, wx.ALL, 10)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Input membership functions")
        sizer_5.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        self.input_memberships = wx.SpinCtrl(self, wx.ID_ANY, "2", min=2, max=4)
        self.input_memberships.SetMinSize((45, 23))
        sizer_5.Add(self.input_memberships, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2)

        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_6, 0, wx.ALL, 10)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Output membership functions")
        sizer_6.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        self.output_memberships = wx.SpinCtrl(self, wx.ID_ANY, "2", min=2, max=4)
        self.output_memberships.SetMinSize((45, 23))
        sizer_6.Add(self.output_memberships, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_7, 0, wx.ALL, 10)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Learning rate")
        sizer_7.Add(label_3, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        self.learning_rate_input = wx.SpinCtrlDouble(self, wx.ID_ANY, initial=0.05, min=0.0, max=10.0, style=wx.ALIGN_CENTRE_HORIZONTAL | wx.SP_ARROW_KEYS)
        self.learning_rate_input.SetIncrement(0.01)
        self.learning_rate_input.SetDigits(3)
        sizer_7.Add(self.learning_rate_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        sizer_2.AddButton(self.button_CLOSE)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Layout()



class AutomaticTest(wx.Dialog):
    def __init__(self,parent):
        
        super(AutomaticTest, self).__init__(parent)
        self.SetFont(parent.GetFont())
        self.SetTitle("Automatic test result")
        
        
        #LLAMADA A TEST AUTOMATICO 
        result=parent.controller.automatic_statistic_test().getResponse()

        normal_variables=["None"]
        self.grouped_different_variables=["None"]
        covariance=["None"]
        directly=[]
        inverse=[]
        self.covariance_list=[]
        differences_in_groups=[]
        
        names=parent.names


        if result['status']==Status.OK:
            
            normal_variables=result['data']['normal_variables']
            covariance=result['data']['covariance']
            differences_in_groups=result['data']['differences']

            for pair in covariance['directly']:
                directly.append(str(pair['variables'] +" - "+" directly"))

            for pair in covariance['inverse']:
                directly.append(str(pair['variables'] +" - "+" inverse"))

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

        self.list_box_normal = wx.ListBox(self, wx.ID_ANY, choices=normal_variables)
        sizer_4.Add(self.list_box_normal, 1, wx.ALL | wx.EXPAND, 10)

        sizer_4b = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Covariance"), wx.HORIZONTAL)

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
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Center()
        self.Layout()
        

    def OnChangeCovarianceFilter(self,evt):
        filter=self.combobox_filter_covariance.GetValue()
        filtered=[value for value in self.covariance_list if (str(filter) in value)]
        if len(filtered)==0:
            filtered.append("None")
        self.list_box_covariance.Clear()
        self.list_box_covariance.InsertItems(filtered,0)

class PickDialog(wx.Dialog):
    def __init__(self, parent,check_strings=False):
        
        super(PickDialog, self).__init__(parent)
        self.SetTitle("New task")

        self.SetFont(parent.GetFont())

        self.names=parent.names

        self.string_variables=parent.string_variable_names
        self.controller=parent.controller
        self.all_variables=list(copy.deepcopy(self.names))
        
        self.independent_variables=[]
        self.targets=[]

        self.not_check_strings=check_strings

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        label_variables = wx.StaticText(self, wx.ID_ANY, "Variables")
        sizer_4.Add(label_variables, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.list_box_all_variables = wx.ListBox(self, wx.ID_ANY, choices=self.all_variables,style=wx.LB_MULTIPLE)
        sizer_4.Add(self.list_box_all_variables, 1, wx.ALL | wx.EXPAND, 10)

        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_5, 1, wx.EXPAND, 0)

        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(sizer_6, 1, wx.EXPAND, 0)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)

        label_inputs = wx.StaticText(self, wx.ID_ANY, "Inputs")
        sizer_7.Add(label_inputs, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.list_box_inputs = wx.ListBox(self, wx.ID_ANY, choices=self.independent_variables,style=wx.LB_MULTIPLE)
        sizer_7.Add(self.list_box_inputs, 1,wx.EXPAND| wx.ALL, 5)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_6.Add(sizer_8, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.button_add_input = wx.Button(self, wx.ID_ANY, "Add")
        sizer_8.Add(self.button_add_input, 0, wx.ALL, 5)

        self.button_remove_input = wx.Button(self, wx.ID_ANY, "Remove")
        sizer_8.Add(self.button_remove_input, 0,wx.ALL, 5)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(sizer_9, 1, wx.EXPAND, 0)

        sizer_10 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(sizer_10, 1, wx.ALL|wx.EXPAND, 0)

        label_outputs = wx.StaticText(self, wx.ID_ANY, "Outputs")
        sizer_10.Add(label_outputs, 0, wx.LEFT | wx.RIGHT, 10)

        self.list_box_outputs = wx.ListBox(self, wx.ID_ANY, choices=self.targets,style=wx.LB_MULTIPLE)
        sizer_10.Add(self.list_box_outputs, 1, wx.ALL |wx.EXPAND, 5)

        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(sizer_11, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)

        self.button_add_output = wx.Button(self, wx.ID_ANY, "Add")
        sizer_11.Add(self.button_add_output, 0,wx.ALL, 5)

        self.button_remove_output = wx.Button(self, wx.ID_ANY, "Remove")
        sizer_11.Add(self.button_remove_output, 0, wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Bind(wx.EVT_BUTTON,self.OnAddInput,self.button_add_input)
        self.Bind(wx.EVT_BUTTON,self.OnAddOutput,self.button_add_output)
        self.Bind(wx.EVT_BUTTON,self.OnRemoveOutput,self.button_remove_output)
        self.Bind(wx.EVT_BUTTON,self.OnRemoveInput,self.button_remove_input)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)

        self.SetSize(550,450)
        
        self.Center()
        self.Layout()

    def OnApply(self,evt):

        if len(self.independent_variables)==0:
            wx.MessageBox('You must select one or more ingredients', 'Error', wx.OK | wx.ICON_WARNING)
        elif len(self.targets)==0:
            wx.MessageBox('You must select one or more properties', 'Error', wx.OK | wx.ICON_WARNING)
        else:
            toAdd=[]
            names=list(self.names)
            for independent in self.independent_variables:
                toAdd.append(names.index(independent))

            self.controller.set_independent_variables(toAdd)

            toAdd=[]
            names=list(self.names)
            for target in self.targets:
                toAdd.append(names.index(target))

            self.controller.set_targets(toAdd)

            del toAdd
            
            self.EndModal(wx.ID_APPLY)
            self.Destroy()

    def OnAddInput(self,evt):
        self.OnAdd(self.list_box_inputs,self.independent_variables,check_strings=self.not_check_strings)

    def OnAddOutput(self,evt):
        self.OnAdd(self.list_box_outputs,self.targets)

    def OnRemoveInput(self,evt):
        self.OnRemove(self.list_box_inputs,self.independent_variables)

    def OnRemoveOutput(self,evt):
        self.OnRemove(self.list_box_outputs,self.targets)

    def OnAdd(self,listbox,variables,check_strings=False):
        selection=self.list_box_all_variables.GetSelections()
        
        
        tmp_all=copy.deepcopy(self.all_variables)
        
        for pos in selection:
            do=True

            if check_strings:
                if tmp_all[pos] in self.string_variables:
                    wx.MessageBox(tmp_all[pos]+" is a nominal variable, it can not be used as input.","Warning",wx.ICON_WARNING)
                    do=False
        
            if not tmp_all[pos] in self.independent_variables and not tmp_all[pos] in self.targets and do:
                
                variables.append(tmp_all[pos])
                self.all_variables.remove(tmp_all[pos])

            self.list_box_all_variables.Deselect(pos)
        
        del tmp_all
        #update listbox
        
        self._update_listbox(listbox,variables)

    def OnRemove(self,listbox,variables):
        selection=listbox.GetSelections()

        tmp=copy.deepcopy(variables)
        for pos in selection:
            variables.remove(tmp[pos])
            self.all_variables.append(tmp[pos])
            #self.list_box_all_variables.Insert(tmp[pos],self.list_box_all_variables.GetTopItem()+1)

        del tmp
        #update listbox
        
        self._update_listbox(listbox,variables)
        
    def _update_listbox(self,listbox,variables):
        listbox.Clear()
        if len(variables)!=0:
            listbox.InsertItems(variables,0)

        self.list_box_all_variables.Clear()
        if len(self.all_variables)!=0:
            self.list_box_all_variables.InsertItems(self.all_variables,0)

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
                result=self.controller.apply_preprocess(variable).getResponse()
                
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
            result=self.controller.set_preprocess_option(variable,self.data_preprocess[variable]).getResponse()

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
    
    


class PredictionModelDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Prediction model")
        self.SetFont(parent.GetFont())
        #TO DO: LOAD ON CHANGE VARIABLE CURRENT SELECTIONS
        #TO DO: LOAD CONFIGURATION IF EXISTS
        #TO DO: VALIDATIONS (NSETS!=0 TEST SIZE!=0 AND !=1)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.shape=parent.controller.get_data_shape().getResponse()['data']
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        self.parent=parent
        self.names=["All"]
        self.display_list=["All"]
        self.controller=parent.controller
        self.variables=parent.names
        self.type_list=None
        self.regression_models=[]
        self.classification_models=[]
        self.model_selection={}
        self.regression_vars=[]
        self.validation={'method':"Train test split",'params':{'subsets':3,'test_size':0.3}}

        response=self.controller.get_target_process_type().getResponse()

        if response['status']==Status.OK:
            
            self.type_list=response['data']
            for variable in response['data']:
                self.names.append(variable)
                self.display_list.append(variable+" - "+response['data'][variable])
                if response['data'][variable]=="regression":
                    self.regression_vars.append(variable)
                self.model_selection[variable]={'model':'','params':''}
                
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)

        response=self.controller.get_available_models().getResponse()
        if response['status']==Status.OK:
            self.regression_models=response['data']['regression'] 
            self.classification_models=response['data']['classification']    
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)


        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Apply to"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_targets = wx.ComboBox(self, wx.ID_ANY, choices=self.display_list,value="All", style=wx.CB_DROPDOWN|wx.CB_READONLY)
        sizer_4.Add(self.combo_box_targets, 1, wx.ALL, 5)

        self.notebook_type = wx.Notebook(self, wx.ID_ANY)
        sizer_3.Add(self.notebook_type, 1, wx.ALL | wx.EXPAND, 10)
        self.notebook_type.SetBackgroundColour(wx.Colour(240,240,240,255))

        self.notebook_regression = wx.Panel(self.notebook_type, wx.ID_ANY)
        self.notebook_type.AddPage(self.notebook_regression, "Regression")

        
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)

        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_11.Add(sizer_12, 1, wx.ALL, 10)

        label_4 = wx.StaticText(self.notebook_regression, wx.ID_ANY, "Select Models")
        sizer_12.Add(label_4, 0, 0, 0)

        self.list_box_models_regression = wx.ListBox(self.notebook_regression, wx.ID_ANY, choices=self.regression_models)
        sizer_12.Add(self.list_box_models_regression, 1, wx.BOTTOM | wx.EXPAND, 5)

        self.checkbox_1 = wx.CheckBox(self.notebook_regression, wx.ID_ANY, "Automatic grid search")
        sizer_12.Add(self.checkbox_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)


        self.notebook_classification = wx.Panel(self.notebook_type, wx.ID_ANY)
        self.notebook_type.AddPage(self.notebook_classification, "Classification")

        sizer_11b = wx.BoxSizer(wx.HORIZONTAL)

        sizer_12b = wx.BoxSizer(wx.VERTICAL)
        sizer_11b.Add(sizer_12b, 1, wx.ALL, 10)

        label_4b = wx.StaticText(self.notebook_classification, wx.ID_ANY, "Select Models")
        sizer_12b.Add(label_4b, 0, 0, 0)

        self.list_box_models_classification = wx.ListBox(self.notebook_classification, wx.ID_ANY, choices=self.classification_models)
        sizer_12b.Add(self.list_box_models_classification, 1, wx.BOTTOM | wx.EXPAND, 5)

        self.checkbox_auto_grid_class = wx.CheckBox(self.notebook_classification, wx.ID_ANY, "Automatic grid search")
        sizer_12b.Add(self.checkbox_auto_grid_class, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)


        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Validation"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 0, wx.EXPAND, 0)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_6.Add(sizer_7, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Type")
        sizer_7.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL,10)

        self.combo_box_validation = wx.ComboBox(self, wx.ID_ANY,value="Train test split", choices=["Train test split","Cross Validation"], style=wx.CB_DROPDOWN |wx.CB_READONLY)
        sizer_7.Add(self.combo_box_validation, 0,0, 5)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_8, 1, wx.EXPAND, 0)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_8.Add(sizer_9, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        label_2 = wx.StaticText(self, wx.ID_ANY, u"Nº of sets")
        sizer_9.Add(label_2, 0, wx.RIGHT, 5)
        
        self.shape=self.controller.get_data_shape().getResponse()['data']

        self.spin_ctrl_sets = wx.SpinCtrl(self, wx.ID_ANY, "3", min=1, max=100)
        sizer_9.Add(self.spin_ctrl_sets, 0, 0, 0)

        sizer_10 = wx.BoxSizer(wx.VERTICAL)
        sizer_8.Add(sizer_10, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Test size")
        sizer_10.Add(label_3, 0, wx.BOTTOM | wx.RIGHT , 5)

        self.spin_ctrl_test_size = wx.SpinCtrlDouble(self, wx.ID_ANY, initial=0.3, min=0.0, max=1.0,inc=0.1)
        self.spin_ctrl_test_size.SetDigits(2)
        sizer_10.Add(self.spin_ctrl_test_size, 0, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "Continue")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        sizer_2.Realize()

        self.notebook_regression.SetSizer(sizer_11)
        self.notebook_classification.SetSizer(sizer_11b)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnContinue,self.button_OK)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeValidation,self.combo_box_validation)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckGrid,self.checkbox_1)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckGrid,self.checkbox_auto_grid_class)
        self.Bind(wx.EVT_SPINCTRL,self.OnChangeValidation,self.spin_ctrl_sets)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.OnChangeValidation,self.spin_ctrl_test_size)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeOutput,self.combo_box_targets)
        self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_classification)
        self.Bind(wx.EVT_BUTTON,self.OnHelp,self.button_HELP)
        #self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box_targets)
        self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_regression)
        #self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())


        self.Center()
        self.Layout()


    def OnHelp(self,evt):
        dialog=HelpDialog(self,file="./front/resources/help/prediction_dialog_help.json",title="Prediction Model")
        dialog.ShowModal()

    def _validation_params(self):
        ok=True
        #Validacion de sets y train test split
        if self.spin_ctrl_test_size.GetValue()<=0.0 or self.spin_ctrl_test_size.GetValue()>=1.0:
            ok=False
            wx.MessageBox("Test size can not be "+str(self.spin_ctrl_test_size.GetValue())+".","Error",wx.ICON_ERROR)
        
        if self.spin_ctrl_sets.GetValue()>=self.shape[0]:
            ok=False
            wx.MessageBox("The number of folders can not be higher than the number of rows.","Error",wx.ICON_ERROR)
        elif self.spin_ctrl_sets.GetValue()>=self.shape[0]/2:
            code=wx.MessageBox("The number of folders might be too high for the number of rows of the data. You want to continue anyway?","Warning",wx.ICON_WARNING|wx.NO|wx.NO_DEFAULT|wx.YES)
            
            if code==wx.NO:
                ok=False

        return ok
    
    def OnCheckGrid(self,evt):
        variable=self.combo_box_targets.GetString(self.combo_box_targets.GetSelection())
        variable=variable.split(" - ")[0]

        if variable=="All":
            if self.notebook_classification.IsShown():
                self._fill_param("classification",self.checkbox_auto_grid_class)
            
            elif self.notebook_regression.IsShown():
                self._fill_param("regression",self.checkbox_1)
        else:
            if self.notebook_classification.IsShown():
                self.model_selection[variable]['params']=self.checkbox_auto_grid_class.GetValue()
            elif self.notebook_regression.IsShown():
                self.model_selection[variable]['params']=self.checkbox_1.GetValue()

    def _fill_param(self,type,checkbox):
        for var in self.display_list:
            if var!="All":
                var_name=var.split(" - ")[0]
                var_type=var.split(" - ")[1]
                if var_type==type:
                    self.model_selection[var_name]['params']=checkbox.GetValue()

    def _enable_classification(self,val):
        self.notebook_classification.Enable(val)
        self.list_box_models_classification.Enable(val)
        self.checkbox_auto_grid_class.Enable(val)
    
    def _enable_regression(self,val):
        self.notebook_regression.Enable(val)
        self.list_box_models_regression.Enable(val)
        self.checkbox_1.Enable(val)
        

    def OnChangeOutput(self,evt):
        self.list_box_models_classification.Deselect(self.list_box_models_classification.GetSelection())
        self.list_box_models_regression.Deselect(self.list_box_models_regression.GetSelection())
        
        variable=evt.GetString()
        variable=variable.split(" - ")[0]
        
        
        if variable=="All":
            self._enable_classification(True)
            self._enable_regression(True)
        elif variable in self.regression_vars:
            self._enable_classification(False)
            self._enable_regression(True)
        else:
            self._enable_classification(True)
            self._enable_regression(False)



    def OnSelectModel(self,evt):
        
        variable=self.combo_box_targets.GetValue()
        variable=variable.split(" - ")[0]
        
        if variable!="All":
            grid=False
            if variable in self.regression_vars:
                model=self.list_box_models_regression.GetStringSelection()
                grid=self.checkbox_1.GetValue()
            else:
                model=self.list_box_models_classification.GetStringSelection()
                grid=self.checkbox_auto_grid_class.GetValue()

            self.model_selection[variable]['model']=[model]
            self.model_selection[variable]['params']=grid
        else:
            if self.notebook_regression.IsShown():
                model=self.list_box_models_regression.GetStringSelection()
                for variable in self.model_selection:
                    if variable in self.regression_vars:
                        self.model_selection[variable]['model']=[model]
                        self.model_selection[variable]['params']=self.checkbox_1.GetValue()

            elif self.notebook_classification.IsShown():
                model=self.list_box_models_classification.GetStringSelection()
                for variable in self.model_selection:
                    if not variable in self.regression_vars:
                        self.model_selection[variable]['model']=[model]
                        self.model_selection[variable]['params']=self.checkbox_auto_grid_class.GetValue()

    def OnChangeValidation(self,evt):
        method=self.combo_box_validation.GetValue()
        nsets=self.spin_ctrl_sets.GetValue()
        test_size=self.spin_ctrl_test_size.GetValue()
        
        self.validation['method']=method
        self.validation['params']['subsets']=nsets
        self.validation['params']['test_size']=test_size
        

    def OnContinue(self,evt):
        ok=True
        taskname=""
        cancel=False

        #validaciones 
        for variable in self.model_selection:
            model=self.model_selection[variable]
            
            if variable!="All" and model['model']=="":
                ok=False
                wx.MessageBox("You must select at leas one model for each variable","Error",wx.ICON_ERROR)
                break
        if ok:
            ok=self._validation_params()
           
        if ok:
            ok=False
            name,cancel=get_task_name(self)
            
            if not cancel:
                response=self.controller.create_task(name,self.model_selection,self.validation,False).getResponse()

                if response['status']==Status.OK:
                    #self.Parent.updateStatusTask(taskname)
                    self.Hide()
                    dialog=TaskReportDialog(self.parent)
                    code=dialog.ShowModal()

                    if code==wx.ID_CANCEL or code==wx.ID_ABORT:
                        self.Show()
                    else:
                        self.EndModal(wx.ID_OK)
                        self.Destroy()

                elif response['status']==Status.EXISTING_TASK:
                    wx.MessageBox("A task already exists","Warning",wx.ICON_WARNING)
                else:
                    wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)



class TaskReportDialog(wx.Dialog):
    def __init__(self,parent):

        wx.Dialog.__init__(self,parent)
        self.SetTitle("Task report")
        self.SetFont(parent.GetFont())
        self.parent=parent
        self.task_report=""
        self.controller=parent.controller
        self.task_report=self.controller.get_task_info().getResponse()['data']

        self.progressBar=None

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Task information"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 10)

        self.label_report = wx.StaticText(self, wx.ID_ANY,self.task_report)
        sizer_3.Add(self.label_report, 1, wx.ALL | wx.EXPAND, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)


        tooltip_bg=wx.ToolTip("You can see the progress of the training and the results inmediatly after.")
        self.button_train = wx.Button(self, wx.ID_OK, "Begin training")
        self.button_train.SetToolTip(tooltip_bg)
        self.button_train.SetDefault()
        sizer_2.AddButton(self.button_train)

        tooltip_bg=wx.ToolTip("The training is hidden and the results are stored in the file previously indicated.")
        self.button_train_background = wx.Button(self, wx.ID_CANCEL, "Train in background")
        self.button_train_background.SetToolTip(tooltip_bg)

        sizer_2.AddButton(self.button_train_background)


        tooltip_save=wx.ToolTip("Export the report to a text file")
        self.button_SAVE = wx.Button(self, wx.ID_APPLY, "Export to file")
        self.button_SAVE.SetToolTip(tooltip_save)

        sizer_2.AddButton(self.button_SAVE)

        self.button_CANCEL = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_train)
        self.Bind(wx.EVT_BUTTON,self.OnApplyBg,self.button_train_background)
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()

    def OnSave(self,evt):
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,defaultDir=self.parent.setting.GetPath()).getResponse()

        if path['status']==Status.OK:
            
            saver=Saver(path['data'],content=self.label_report.GetLabelText())
            saver.save()
            wx.MessageBox("File saved succesfully in "+path['data'],"Info")

    def OnApply(self,event):
        targets=self.controller.get_target_indexes().getResponse()['data']
        maximum=len(targets)*100
        
        self.progressBar = wx.ProgressDialog("Training in progress ... ", "Please, wait...",maximum=maximum,parent=self,style=wx.PD_APP_MODAL|wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
        #self.progressbar.Update(10,"Training in progress...")
        #self.execute_thread()
        thread = threading.Thread(target=self.execute_thread)
        thread.start()
    
    def OnApplyBg(self,evt):
        from plyer import notification
        pathname=IOManage.GetPath(self,"Select a path for the task",WILCARD_TASK,defaultDir=self.parent.setting.GetPath()).getResponse()

        notification.notify(title="Starting training",message="The training of the models is about to start.",timeout=1,app_name="NeuroRule",app_icon="./front/resources/img/logo_128x128.ico")
        time.sleep(1)
        try:

            if pathname['status']==Status.OK:
                self.Hide()
                self.Parent.Hide()
                self.execute_thread_bg(pathname['data'])
                notification.notify(title="Training finished",message="The training has finished succesfully and saved in "+pathname['data'],timeout=10,app_name="NueroRule",app_icon="./front/resources/img/logo_128x128.ico")
                sys.exit(0)
        except Exception as exc:
            notification.notify(title="Training stopped",message="There has been a mistake in the training",timeout=10,app_name="NueroRule",app_icon="./front/resources/img/logo_128x128.ico")

    
    def execute_thread_bg(self,pathname):
        response=self.controller.execute_task(None).getResponse()
        if response['status']==Status.OK:
            self.controller.save_task(pathname)

    def execute_thread(self):
        
        response=self.controller.execute_task(self.update_progress).getResponse()
     
        #wx.CallAfter(self.progressbar.Update,self.progressbar.GetRange())
        self.progressBar.Update(self.progressBar.GetRange())

        
        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
            
            self.EndModal(wx.ID_ABORT)
            self.Destroy()
        else:        
            
            wx.MessageBox("Training completed!","Info")
            
            self.EndModal(wx.ID_APPLY)
            self.Destroy()
            
    def update_progress(self, value):
        
        self.progressBar.Update(value,"Training in progress...")





class CrossValidationDialog(wx.Dialog):
    def __init__(self,parent,cross_validation,metric):
        
        wx.Dialog.__init__(self, parent)
        self.SetTitle("Cross validation")
        

        figure=plot_barplot_object(cross_validation,xtitle="Folds",ytitle=metric).gcf()
        self.canvas = FigureCanvas(self, -1, figure)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Cross Validation Report")
        label_1.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.grid_folds_result = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_folds_result.CreateGrid(1,len(cross_validation))
        i=0
        for key in cross_validation:
            self.grid_folds_result.SetColLabelValue(i,key)
            self.grid_folds_result.SetCellValue(0,i,str(np.round(cross_validation[key],2)))
            i+=1
       
        
        self.grid_folds_result.SetRowLabelValue(0,metric)
        sizer_3.Add(self.grid_folds_result, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)

        sizer_figure = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_figure, 1, wx.EXPAND, 0)

        sizer_figure.Add(self.canvas, 1, wx.EXPAND, 0)



        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        sizer_2.AddButton(self.button_CLOSE)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Layout()



class ResultsDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Results dialog")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.setting=parent.setting
        self.outputs=[]
        response=self.controller.get_target_process_type().getResponse()
        
        self.currentMetrics={}
        self.currentModel={}
        self.currentValidation=None
        
        if response['status']==Status.OK:
            self.outputs=list(response['data'].keys())
        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)


        self.models=self.controller.get_variable_models().getResponse()['data']

        self.cb_selections=[]

        self.saved=False
        self.path=""

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Results")
        label_1.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Outputs"), wx.VERTICAL)
        sizer_4.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        self.lb_outputs = wx.ListBox(self, wx.ID_ANY, choices=self.outputs)
        sizer_5.Add(self.lb_outputs, 1, 0, 5)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND, 0)

        sizer_9 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Model"), wx.HORIZONTAL)
        sizer_6.Add(sizer_9, 0, wx.ALL | wx.EXPAND, 10)

        self.cb_model = wx.ComboBox(self, wx.ID_ANY, choices=self.cb_selections, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        sizer_9.Add(self.cb_model, 1, wx.ALL, 5)

        self.cb_model.Enable(False)
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Metrics"), wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 10)


        #self.label_metrics = wx.StaticText(self, wx.ID_ANY,label="Select output")
        #sizer_7.Add(self.label_metrics, 1, wx.ALL | wx.EXPAND, 5)

        ##
        # Grid
        self.validation_grid=wx.grid.Grid(self, wx.ID_ANY)
        self.validation_grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.validation_grid.CreateGrid(4, 2)
        self.validation_grid.SetRowLabelValue(0, "")
        self.validation_grid.SetRowLabelValue(1, "")
        self.validation_grid.SetRowLabelValue(2, "")
        self.validation_grid.SetRowLabelValue(3, "")
        self.validation_grid.SetColLabelValue(0, "Testing")
        self.validation_grid.SetColLabelValue(1, "Training")
        #self.validation_grid.HideColLabels()

        sizer_7.Add(self.validation_grid, 0, wx.ALL, 10)
        ##


        sizer_plot=wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_plot,0,wx.EXPAND,10)

        self.button_plot_metrics=wx.Button(self,id=wx.ID_ANY,label="Plot testing metrics")
        sizer_plot.Add(self.button_plot_metrics,0,wx.ALL | wx.EXPAND,5)

        self.button_plot_metrics_trainings=wx.Button(self,id=wx.ID_ANY,label="Plot training metrics")
        sizer_plot.Add(self.button_plot_metrics_trainings,0,wx.ALL | wx.EXPAND,5)

        self.button_plot_precisewise=wx.Button(self,id=wx.ID_ANY,label="Plot output")
        sizer_plot.Add(self.button_plot_precisewise,0,wx.ALL | wx.EXPAND,5)

        self.button_plot_precisewise.Enable(False)
        self.button_plot_metrics.Enable(False)
        self.button_plot_metrics_trainings.Enable(False)

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Model Information"), wx.HORIZONTAL)
        sizer_6.Add(sizer_8, 1, wx.ALL | wx.EXPAND, 10)

        self.label_model_info = wx.StaticText(self, wx.ID_ANY, "Select output")
        sizer_8.Add(self.label_model_info, 1, wx.ALL | wx.EXPAND, 5)

        self.button_show_params=wx.Button(self,id=wx.ID_ANY,label="Show params")
        sizer_8.Add(self.button_show_params,0,wx.ALL,5)

        self.button_show_params.Enable(False)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Actions"), wx.HORIZONTAL)
        sizer_6.Add(sizer_10, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        grid_sizer_1 = wx.GridSizer(1, 2, 1, 1)
        sizer_10.Add(grid_sizer_1, 1, 0, 0)

        #self.button_plots = wx.Button(self, wx.ID_ANY, "Plots")
        #grid_sizer_1.Add(self.button_plots, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.button_predict = wx.Button(self, wx.ID_ANY, "Predict")
        grid_sizer_1.Add(self.button_predict, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.button_save_alone = wx.Button(self, wx.ID_ANY, "Export to file")
        grid_sizer_1.Add(self.button_save_alone, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        #self.button_details = wx.Button(self, wx.ID_ANY, "Details")
        #grid_sizer_1.Add(self.button_details, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "Save*")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)
        self._enableButtons(False)
        self.Bind(wx.EVT_LISTBOX,self.OnSelectOutput,self.lb_outputs)
        self.Bind(wx.EVT_COMBOBOX,self.OnSelectModel,self.cb_model)
        self.Bind(wx.EVT_BUTTON,self.OnPlotMetrics,self.button_plot_metrics)
        self.Bind(wx.EVT_BUTTON,self.OnPlotMetricsTraining,self.button_plot_metrics_trainings)
        self.Bind(wx.EVT_BUTTON,self.OnShowParams,self.button_show_params)
        self.Bind(wx.EVT_BUTTON,self.OnSaveTask,self.button_SAVE)
        self.Bind(wx.EVT_BUTTON,self.OnExportToFile,self.button_save_alone)
        self.Bind(wx.EVT_BUTTON,self.OnPredict,self.button_predict)
        self.Bind(wx.EVT_BUTTON,self.OnPlotPrecision,self.button_plot_precisewise)
        sizer_2.Realize()   

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        #self.SetSize(600,500)
        self.Center()
        self.Layout()
    
    def OnPlotPrecision(self,evt):
        model=self.cb_model.GetStringSelection()
        output=self.lb_outputs.GetStringSelection()

        response=self.controller.get_model_plot(output,model).getResponse()

        if response['status']==Status.OK:
            figure=response['data']
            figure.show()
        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
        

    def OnExportToFile(self,evt):
        index=self.lb_outputs.GetSelection()
        variable=self.lb_outputs.GetString(index)
        model=self.cb_model.GetValue()
        response=self.controller.get_text_reports(variable).getResponse()

        content=response['data'][model]
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,defaultDir=self.setting.GetPath(),defaultname=(model+"_"+variable)).getResponse()

        if path['status']==Status.OK:
            #save officialy
            path=path['data']
            response=self.controller.save_file(content,path).getResponse()
            if response['status']==Status.OK:
                wx.MessageBox("Filed saved in "+path)
            else:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)


    def OnPredict(self,evt):

        index=self.lb_outputs.GetSelection()
        if index==-1:
            wx.MessageBox("You have to select a variable","Error",wx.ICON_ERROR)
        else:
            model=self.cb_model.GetValue()
            if model=="":
                wx.MessageBox("You have to select a model","Error",wx.ICON_ERROR)
            else:
                variable=self.lb_outputs.GetString(index)
                inputs=self.controller.get_inputs_task().getResponse()['data']
                dialog=PredictDialog(self.Parent,variable,model,inputs)
                code=dialog.ShowModal()

    def OnSaveTask(self,evt):
        
        cancel=False
        taskname=self.controller.get_task_name().getResponse()
        if taskname['status']==Status.OK:
            taskname=taskname['data']

            if not self.saved:
                pathname=IOManage.GetPath(self,"Select a path",WILCARD_TASK,defaultDir=self.setting.GetPath(),defaultname=taskname).getResponse()
                
                if pathname['status']==Status.OK:
                    pathname=pathname['data']
                else:
                    cancel=True

            else:
                pathname=self.path

            if not cancel:
                response=self.controller.save_task(pathname).getResponse()

                if response['status']==Status.OK:
                    wx.MessageBox("Succesfully saved in "+pathname,"Info")
                    self.button_SAVE.SetLabel("Save")
                    self.saved=True
                    self.path=pathname
                else:
                    wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)

        else:
            wx.MessageBox(taskname['data'],"Error",wx.ICON_ERROR)

    def OnShowParams(self,evt):
        model_info=self.currentModel
        formated_model=""   
        for param in model_info:
            if str(model_info[param]) != "deprecated":
                formated_model=formated_model+param+" : "+str(model_info[param])+"\n "

        dialog=DisplayInfo(self,label="Params",content=formated_model)
        dialog.ShowModal()

    def OnPlotMetricsTraining(self,evt):
        model=self.cb_model.GetValue()
        variable=self.lb_outputs.GetString(self.lb_outputs.GetSelection())
        title=variable+" prediction with "+model+" training"

        if self.currentValidation=="Cross Validation":

            #DISPLAY NEW WINDOW
            
            title=variable+" prediction with "+model+" cross validation"

            keys=list(self.currentMetrics['training_validation'].keys())
            
            metric=keys[0].split("_")[1]
            data={}
            for i in range(len(self.currentMetrics['training_validation'][keys[1]])):
                data['fold'+str(i)]=self.currentMetrics['training_validation'][keys[1]][i]
            
            dialog=CrossValidationDialog(self,data,metric)
            dialog.ShowModal()
            #plot_barplot(data,title=title,xtitle="Folds",ytitle=metric)
        else:
            plot_barplot(self.currentMetrics['training_validation'],title=title,xtitle="Metrics",ytitle="Values")
        
    def OnPlotMetrics(self,evt):
        model=self.cb_model.GetValue()
        variable=self.lb_outputs.GetString(self.lb_outputs.GetSelection())
        title=variable+" prediction with "+model+" testing"
        plot_barplot(self.currentMetrics['test_validation'],title=title,xtitle="Metrics",ytitle="Values")

    def _enableButtons(self,val):
        #self.button_details.Enable(val)
        self.button_plot_metrics.Enable(val)
        self.button_plot_metrics_trainings.Enable(val)
        self.button_show_params.Enable(val)
        self.button_save_alone.Enable(val)
        self.button_predict.Enable(val)
        self.button_plot_precisewise.Enable(val)
        #self.button_plots.Enable(val)

    def OnSelectOutput(self,evt):
        self.ClearGrid()
        self._enableButtons(False)
        output=evt.GetString()
        self.cb_selections=[]
        self.cb_model.Enable(True)
        for model in self.models[output]:
            self.cb_selections.append(model.modelname)
        
        self.cb_model.Clear()
        self.cb_model.AppendItems(self.cb_selections)

        #self.label_metrics.SetLabelText("Select Model")
        self.label_model_info.SetLabelText("Select Model")
    

    def ClearGrid(self):

        for i in range(self.validation_grid.GetNumberCols()):
            for j in range(self.validation_grid.GetNumberRows()):
                self.validation_grid.SetCellValue(j,i,"")
                self.validation_grid.SetCellBackgroundColour(j,i,self.validation_grid.GetDefaultCellBackgroundColour())
                self.validation_grid.SetRowLabelValue(j,"")
            

    def OnSelectModel(self,evt):
        model=evt.GetString()
        output=self.lb_outputs.GetString(self.lb_outputs.GetSelection())
        
        response=self.controller.get_output_info(output).getResponse()
        
        if model!="":
            
            self._enableButtons(True)
        else:
            
            self._enableButtons(False)

        if response['status']==Status.OK:
            
            self._enableButtons(True)

            tmp=response['data'][model]

            metrics=tmp['metrics']
            model_info=tmp['options']['params']
            grid_search=tmp['options']['grid_search']
            validation=tmp['validation']

            self.currentMetrics=tmp['metrics']
            self.currentModel=model_info
            self.currentValidation=validation
            formated_metrics=""
            
            j=0
            for phase in metrics:
                i=0
                for metric in metrics[phase]:
                    name='r2'
                    metric_name=metric
                    if validation=="Cross Validation" and phase=='training_validation' and metric=="average_r2":
                        name='average_r2'
                        metric_name="r2"
                        self.button_plot_metrics_trainings.SetLabelText("View CV results")
                    elif validation=="Cross Validation" and phase=='training_validation' and metric=="average_accuracy":
                        metric_name="accuracy"
                        self.button_plot_metrics_trainings.SetLabelText("View CV results")

                    elif validation=="Cross Validation" and phase=='training_validation':
                        self.button_plot_metrics_trainings.SetLabelText("View CV results")
                        break
                    else:
                        
                        self.button_plot_metrics_trainings.SetLabelText("Plot training metrics")

                    self.validation_grid.SetRowLabelValue(i,metric_name)

                    value=np.round(metrics[phase][metric],3)
                    if metric==name:
                        if value < 0.5:
                            colour=wx.Colour('#e07453')
                        elif value < 0.7:
                            colour=wx.Colour('#c7a23e')
                        elif value < 9:
                            colour=wx.Colour('#6f9651')
                        else:
                            colour=wx.Colour('#19bf1c')
                        self.validation_grid.SetCellBackgroundColour(i,j,colour)

                    self.validation_grid.SetCellValue(i,j,str(value))
                
                    self.validation_grid.SetReadOnly(i,j,True)
                    i+=1
                j+=1

            """
            
            for moment in metrics:
                if 'test_validation'==moment:
                    formated_metrics=formated_metrics+"Test validation: "
                elif 'training_validation'==moment and validation!="Cross Validation":
                    formated_metrics=formated_metrics+"Train validation: "
                    self.button_plot_metrics_trainings.SetLabelText("Plot training metrics")
                else:
                    self.button_plot_metrics_trainings.SetLabelText("View CV results")

                if validation!="Cross Validation" or moment=='test_validation':
                    for metric in metrics[moment]:
                    
                        value=np.round(metrics[moment][metric],3)
                       
                        if "r2" in metric or "accuracy" in metric:
                            #formated_metrics=formated_metrics+metric+" : <font color='"+color+"'>"+str(value)+"</font>\n"
                            formated_metrics=formated_metrics+metric+" = "+str(value)+"\n"
            """
            if grid_search:
                formated_model="Grid Search applied"
            else:
                formated_model="Static parameters"
            #self.label_metrics.SetLabelText(formated_metrics)
            self.label_model_info.SetLabelText(formated_model)

        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)




class DisplayInfo(wx.Dialog):
    def __init__(self,parent,label,content):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Information")
        self.SetFont(parent.GetFont())
        sizer_1=wx.BoxSizer(wx.VERTICAL)

        sizer_2=wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, label), wx.HORIZONTAL)
        sizer_1.Add(sizer_2,1,wx.EXPAND|wx.ALL,10)

        self.content=wx.StaticText(self,label=content)
        sizer_2.Add(self.content,1,wx.EXPAND|wx.ALL,5)
        
        sizer_3 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_3, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "Close")
        sizer_3.AddButton(self.button_CANCEL)

        self.SetEscapeId(self.button_CANCEL.GetId())

        sizer_3.Realize()
        self.SetSizer(sizer_1)

        sizer_1.Fit(self)
        
        self.Center()
        self.Layout()



class RulePredictinglDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Rule generation model")
        self.SetFont(parent.GetFont())
        #T O DO: LOAD ON CHANGE VARIABLE CURRENT SELECTIONS
        #TO DO: LOAD CONFIGURATION IF EXISTS
        #TO DO: VALIDATIONS (NSETS!=0 TEST SIZE!=0 AND !=1)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.shape=parent.controller.get_data_shape().getResponse()['data']
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        self.parent=parent
        self.names=["All"]
        self.display_list=["All"]
        self.controller=parent.controller
        self.variables=parent.names
        self.type_list=None
        self.regression_models=[]
        self.classification_models=[]
        self.model_selection={}
        self.regression_vars=[]
        self.validation={'method':"Train test split",'params':{'subsets':3,'test_size':0.2}}

        response=self.controller.get_target_process_type().getResponse()

        if response['status']==Status.OK:
            
            self.type_list=response['data']
            for variable in response['data']:
                self.names.append(variable)
                self.display_list.append(variable+" - "+response['data'][variable])
                model="DecisionTree"
                if response['data'][variable]=="regression":
                    self.regression_vars.append(variable)
                    model="Neurofuzzy"
                self.model_selection[variable]={'model':[model],'params':''}
                
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)

        response=self.controller.get_available_models().getResponse()
        if response['status']==Status.OK:
            self.regression_models=response['data']['regression'] 
            self.classification_models=response['data']['classification']    
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)


        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Apply to"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_targets = wx.ComboBox(self, wx.ID_ANY, choices=self.display_list,value="All", style=wx.CB_DROPDOWN|wx.CB_READONLY)
        sizer_4.Add(self.combo_box_targets, 1, wx.ALL, 5)

        self.notebook_type = wx.Notebook(self, wx.ID_ANY)
        sizer_3.Add(self.notebook_type, 1, wx.ALL | wx.EXPAND, 10)
        self.notebook_type.SetBackgroundColour(wx.Colour(240,240,240,255))

        self.notebook_regression = wx.Panel(self.notebook_type, wx.ID_ANY)
        self.notebook_type.AddPage(self.notebook_regression, "Regression")

        
        self.notebook_classification = wx.Panel(self.notebook_type, wx.ID_ANY)
        self.notebook_type.AddPage(self.notebook_classification, "Classification")


        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "Continue")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_HELP = wx.Button(self, wx.ID_HELP, "")
        sizer_2.AddButton(self.button_HELP)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnContinue,self.button_OK)
        #self.Bind(wx.EVT_COMBOBOX,self.OnChangeValidation,self.combo_box_validation)
        #self.Bind(wx.EVT_COMBOBOX,self.OnChangeOutput,self.combo_box_targets)
        #self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_classification)
        #self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_regression)
        
        self.SetEscapeId(self.button_CANCEL.GetId())


        self.Center()
        self.Layout()

    def OnContinue(self,evt):
        
        name,cancel=get_task_name(self)

        if not cancel:
            response=self.controller.create_task(name,self.model_selection,self.validation,True).getResponse()
        
            if response['status']==Status.OK:        
                self.Hide()
                dialog=TaskReportDialog(self.parent)
                code=dialog.ShowModal()

                if code==wx.ID_CANCEL or code==wx.ID_ABORT:
                    self.Show()
                else:
                    self.EndModal(wx.ID_OK)
                    self.Destroy()

            elif response['status']==Status.EXISTING_TASK:
                wx.MessageBox("A task already exists","Warning",wx.ICON_WARNING)
            else:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)



class PredictDialog(wx.Dialog):
    def __init__(self,parent,variable,model,inputs):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Predictions on "+variable)
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.nominals=parent.string_variable_names
        self.inputs=inputs
        self.n_inputs=len(inputs)    
        self.variable=variable
        self.model=model
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Inputs"), wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.ALL | wx.EXPAND, 10)

        self.grid_inputs = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_inputs.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid_inputs.CreateGrid(self.n_inputs, 2)
        self.grid_inputs.SetColLabelValue(0, "Variable")
        self.grid_inputs.SetColLabelValue(1, "Value")
        self.grid_inputs.HideRowLabels()
        self.fillInputs()
        sizer_4.Add(self.grid_inputs, 0, wx.ALL | wx.EXPAND, 5)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Output"), wx.VERTICAL)
        sizer_3.Add(sizer_5,0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        self.output_field = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        sizer_5.Add(self.output_field, 0, wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_PREDICT = wx.Button(self, wx.ID_APPLY, "Predict")
        sizer_2.AddButton(self.button_PREDICT)

        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        sizer_2.AddButton(self.button_CLOSE)

        self.Bind(wx.EVT_BUTTON,self.OnPredict,self.button_PREDICT)
        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Center()
        self.Layout()  


    def OnPredict(self,evt):
        values=[]
        for row in range(self.n_inputs):
            values.append(self.grid_inputs.GetCellValue(row,1))

        response=self.controller.get_prediction(self.variable,self.model,values).getResponse()

        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
        elif response['status']==Status.OK:
            if Validator.check_float(response['data'][0]):
                value=np.round(response['data'],2)[0]
            else:
                value=response['data'][0]

            self.output_field.SetLabelText(str(value))

    def fillInputs(self):
        
        for row in range(self.n_inputs):
            self.grid_inputs.SetCellValue(row,0,self.inputs[row])
            self.grid_inputs.SetReadOnly(row,0)
            
            if self.inputs[row] in self.nominals:
                renderer=wx.grid.GridCellStringRenderer()
                self.grid_inputs.SetCellRenderer(row,1,renderer)
                self.grid_inputs.SetCellValue(row,1,"")
            else:
                renderer=wx.grid.GridCellFloatRenderer()
                self.grid_inputs.SetCellRenderer(row,1,renderer)
                
                self.grid_inputs.SetCellValue(row,1,"0.0")
                



class RulesResultsDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Neurofuzzy result")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.setting=parent.setting
        self.outputs=[]
        self.types=[]
        response=self.controller.get_target_process_type().getResponse()
        self.string_variable_names=parent.string_variable_names
        self.currentMetrics={}
        self.currentModel={}
        self.currentValidation=None
        self.currentSubmodels={}
        
        if response['status']==Status.OK:
            self.outputs=list(response['data'].keys())
            self.types=list(response['data'].values())
            
        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)

        self.models=self.controller.get_variable_models().getResponse()['data']
        self.submodels={}
        i=0
        for output in self.outputs:
            self.submodels[output]=self.models[output][0].submodels

        outputs=self._custom_outputs()
        #self.outputs=outputs
        self.cb_selections=[]
        
        self.saved=False
        self.path=""

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Results")
        label_1.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Outputs"), wx.VERTICAL)
        sizer_4.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        self.lb_outputs = wx.ListBox(self, wx.ID_ANY, choices=outputs)
        sizer_5.Add(self.lb_outputs, 1, 0, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND, 0)

        sizer_9 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "SubModel"), wx.HORIZONTAL)
        sizer_6.Add(sizer_9, 0, wx.ALL | wx.EXPAND, 10)

        self.cb_submodel = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN |wx.CB_READONLY)
        self.cb_submodel.Enable(False)
        sizer_9.Add(self.cb_submodel, 1, wx.ALL, 5)

        self.sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Rules"), wx.HORIZONTAL)
        sizer_6.Add(self.sizer_7, 1, wx.ALL | wx.EXPAND, 10)

        #self.label_rules = wx.StaticText(self, wx.ID_ANY, "Select an output")
        #self.sizer_7.Add(self.label_rules, 1, wx.ALL | wx.EXPAND, 5)

        self.rules_text_ctrl=wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_WORDWRAP | wx.TE_READONLY)
        self.sizer_7.Add(self.rules_text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Model Information"), wx.HORIZONTAL)
        #sizer_6.Add(sizer_8, 0, wx.ALL , 10)

        #self.label_model_info = wx.StaticText(self, wx.ID_ANY, "Select an output")
        #sizer_8.Add(self.label_model_info, 1, wx.ALL | wx.EXPAND, 5)

        ###
        # METRICS GRID
        self.validation_grid=wx.grid.Grid(self, wx.ID_ANY)
        self.validation_grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.validation_grid.CreateGrid(4, 2)
        self.validation_grid.SetRowLabelValue(0, "")
        self.validation_grid.SetRowLabelValue(1, "")
        self.validation_grid.SetRowLabelValue(2, "")
        self.validation_grid.SetRowLabelValue(3, "")
        self.validation_grid.SetColLabelValue(0, "Training")
        self.validation_grid.SetColLabelValue(1, "Testing")

        sizer_8.Add(self.validation_grid,0, wx.ALIGN_CENTER_VERTICAL |wx.ALL, 10)
        ##
        sizer_custom=wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_custom,0,wx.EXPAND | wx.ALL, 10)

        sizer_custom.Add(sizer_8, 0,wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Actions"), wx.HORIZONTAL)
        #sizer_6.Add(sizer_10, 0,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        sizer_custom.Add(sizer_10, 0,wx.ALIGN_CENTER_VERTICAL| wx.ALL, 10)
        
        grid_sizer_1 = wx.GridSizer(2, 2, 2, 2)
        sizer_10.Add(grid_sizer_1, 0, 0, 0)

        self.button_preciwise = wx.Button(self, wx.ID_ANY,  "      Evolution     ")
        grid_sizer_1.Add(self.button_preciwise, 1,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2)

        self.button_mf = wx.Button(self, wx.ID_ANY,         "Membership functions")
        grid_sizer_1.Add(self.button_mf, 1, wx.ALIGN_CENTER_HORIZONTAL |wx.ALL, 2) 

        self.button_predict = wx.Button(self, wx.ID_ANY, "      Predict       ")
        grid_sizer_1.Add(self.button_predict, 1,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2)

        self.button_save_alone = wx.Button(self, wx.ID_ANY, "    Export to file  ")
        grid_sizer_1.Add(self.button_save_alone, 1,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2)

        self.button_details = wx.Button(self, wx.ID_CONTEXT_HELP, "Details")
        #grid_sizer_1.Add(self.button_details, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "Save*")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        sizer_2.AddButton(self.button_details)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.Bind(wx.EVT_LISTBOX,self.OnSelectOutput,self.lb_outputs)
        self.Bind(wx.EVT_COMBOBOX,self.OnSelectSubmodel,self.cb_submodel)
        self.Bind(wx.EVT_BUTTON,self.OnSaveTask,self.button_SAVE)
        self.Bind(wx.EVT_BUTTON,self.OnPlotPrecisewise,self.button_preciwise)
        self.Bind(wx.EVT_BUTTON,self.OnPotMembershipFunctions,self.button_mf)
        self.Bind(wx.EVT_BUTTON,self.OnExportToFile,self.button_save_alone)
        self.Bind(wx.EVT_BUTTON,self.OnDetails,self.button_details)
        self.Bind(wx.EVT_BUTTON,self.OnPredict,self.button_predict)
        self.SetSizer(sizer_1)
        
        
        self._enable_buttons(False)
        sizer_1.Fit(self)
        
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.SetSize(900,700)
        self.Center()
        self.Layout()

    def OnPredict(self,evt):
        variable=self.lb_outputs.GetStringSelection().split(' - ')[0]
        inputs=self.controller.get_inputs_task().getResponse()['data']
        dialog=PredictDialog(self,variable,"Neurofuzzy",inputs)
        dialog.ShowModal()

    def OnDetails(self,evt):
        dialog=DetailsDialog(self,self.controller.get_task_metadata().getResponse()['data'])
        dialog.ShowModal()

    def ClearGrid(self):
        for i in range(self.validation_grid.GetNumberCols()):
            for j in range(self.validation_grid.GetNumberRows()):
                self.validation_grid.SetCellValue(j,i,"")
                self.validation_grid.SetCellBackgroundColour(j,i,self.validation_grid.GetDefaultCellBackgroundColour())
                self.validation_grid.SetRowLabelValue(j,"")

    def OnExportToFile(self,evt):
        index=self.lb_outputs.GetSelection()
        variable=self.lb_outputs.GetString(index).split(" - ")[0]
        submodel=self.cb_submodel.GetValue().split(" - ")[0]
        
        response=self.controller.get_text_reports(variable).getResponse()
        try:
            content=response['data']['Neurofuzzy']
        except Exception as exc:
            content=response['data']['DecisionTree']

        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,defaultDir=self.setting.GetPath(),defaultname=(submodel+"_"+variable)).getResponse()

        if path['status']==Status.OK:
            #save officialy
            path=path['data']
            response=self.controller.save_file(content,path).getResponse()
            if response['status']==Status.OK:
                wx.MessageBox("Filed saved in "+path)
            else:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
    def _custom_outputs(self):
        toret=[]
        i=0
        for output in self.outputs:
            tmp=output
            if self.types[i]=="regression":
                r2=self.models[output][0].get_enssemble_metrics()
                tmp=tmp+" - ("+str(np.round(r2*100,1))+"%)"
            toret.append(tmp)
            i+=1
        
        return toret
        

    def _enable_buttons(self,val):
        self.button_predict.Enable(val)
        #self.button_details.Enable(val)
        self.button_mf.Enable(val)
        self.button_preciwise.Enable(val)
        self.button_save_alone.Enable(val)

    def OnPlotPrecisewise(self,evt):
        submodel=self.cb_submodel.GetString(self.cb_submodel.GetSelection()).split(" - ")[0]
        
        model=self.currentSubmodels[submodel]['model']

        model.plot_r2_evolution()

    def OnPotMembershipFunctions(self,evt):
        
        submodel=self.cb_submodel.GetString(self.cb_submodel.GetSelection()).split(" - ")[0]
        
        model=self.currentSubmodels[submodel]['model']

        if self.current_type=="classification":
            model.plot_tree()
        else:
            model.plot_membership_functions()
        

    def OnSelectOutput(self,evt):
        self.ClearGrid()
        self._enable_buttons(False)
        self.rules_text_ctrl.SetValue("Select a submodel")
        #self.label_rules.SetLabelText("Select a submodel")
        #self.label_model_info.SetLabelText("Select a submodel")
        model_type=self.types[evt.GetSelection()]

        model=evt.GetString().split(" - ")[0]
        self.cb_submodel.Enable(True)

        if  model_type=="classification":
            self.button_mf.SetLabelText("Plot tree")
            self.current_type=model_type
        else:
            self.button_mf.SetLabelText("Membership functions")
            self.current_type=model_type

        submodels=self.submodels[model]
        self.currentSubmodels=(submodels)
        self._format_selection(submodels)
        

    def _format_selection(self,submodels):

        formated_submodels=list()
        
        for submodel in submodels:
           
            chain=submodel+" - ("
            for input in submodels[submodel]['inputs']:
                chain=chain+input
                if input!=submodels[submodel]['inputs'][-1]:
                    chain=chain+" +"
            chain=chain+")"

            formated_submodels.append(chain)

        self.cb_submodel.Clear()
        if len(formated_submodels)==0:
            self.cb_submodel.Enable(False)
        else:
            self.cb_submodel.Enable(True)
            self.cb_submodel.AppendItems(formated_submodels)

    def _display(self,submodel,rules,metric_value):
        j=0
        
        for elements in submodel:
            if elements!="model" and elements!="best" and elements!="inputs":
                i=0
                for metric in submodel[elements]:
                    
                    value=np.round(submodel[elements][metric],3)
                    if metric=="r2":
                        if value < 0.5:
                            colour=wx.Colour('#e07453')
                        elif value < 0.7:
                            colour=wx.Colour('#c7a23e')
                        elif value < 9:
                            colour=wx.Colour('#6f9651')
                        else:
                            colour=wx.Colour('#19bf1c')
                        self.validation_grid.SetCellBackgroundColour(i,j,colour)

                    self.validation_grid.SetRowLabelValue(i,metric)
                    
                    self.validation_grid.SetCellValue(i,j,str(value))
                
                    self.validation_grid.SetReadOnly(i,j,True)
                    i+=1
                j+=1
                
        rules_formatted=""
        for rule in rules:
            rules_formatted=rules_formatted+rule+"\n\n"
        
        #self.label_rules.SetLabelText(rules_formatted)
        self.rules_text_ctrl.SetValue(rules_formatted)
        #self.sizer_7.Layout()
    

    def _display_classification(self,submodel):
        submodel=self.currentSubmodels[submodel]
        
        accuracy=submodel['training_score']['accuracy']
        model=submodel['model']
        rules=model.get_rules()
       
        self._display(submodel,rules,accuracy)

    def _display_regression(self,submodel):
        submodel=self.currentSubmodels[submodel]
        
        r2=submodel['training_score']['r2']
        model=submodel['model']
        rules=model.get_rules()

        
        self._display(submodel,rules,r2)
        

    def OnSelectSubmodel(self,evt):
        self._enable_buttons(True)
        submodel=evt.GetString().split(" - ")[0]
        
        if submodel!="all":
            self._display_regression(submodel)
        else:
            self._display_classification(submodel)
        
    def OnSaveTask(self,evt):
        
        cancel=False
        taskname=self.controller.get_task_name().getResponse()
        if taskname['status']==Status.OK:
            taskname=taskname['data']

            if not self.saved:
                pathname=IOManage.GetPath(self,"Select a path",WILCARD_TASK,defaultDir=self.setting.GetPath(),defaultname=taskname).getResponse()
                
                if pathname['status']==Status.OK:
                    pathname=pathname['data']
                else:
                    cancel=True

            else:
                pathname=self.path

            if not cancel:
                response=self.controller.save_task(pathname).getResponse()

                if response['status']==Status.OK:
                    wx.MessageBox("Succesfully saved in "+pathname,"Info")
                    self.button_SAVE.SetLabel("Save")
                    self.saved=True
                    self.path=pathname
                else:
                    wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)

        else:
            wx.MessageBox(taskname['data'],"Error",wx.ICON_ERROR)




class SettingsDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Settings")
        self.SetFont(parent.GetFont())
        self.currentSettings=parent.setting
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_options = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Options"), wx.HORIZONTAL)
        sizer_3.Add(sizer_options, 1, wx.ALL | wx.EXPAND, 10)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_options.Add(sizer_4, 1, wx.EXPAND, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        label_font_size = wx.StaticText(self, wx.ID_ANY, "Font size")
        sizer_5.Add(label_font_size, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)


        self.original_font_size=self.currentSettings.font_size
        self.restart=False

        self.font_size_ctrl = wx.SpinCtrl(self, wx.ID_ANY,initial=self.original_font_size, min=9, max=20)
        sizer_5.Add(self.font_size_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND, 0)

        label_font_size_copy = wx.StaticText(self, wx.ID_ANY, "Default path")
        sizer_6.Add(label_font_size_copy, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)


        self.default_path_ctrl = wx.TextCtrl(self, wx.ID_ANY,self.currentSettings.defaultPath,style=wx.TE_READONLY,size=(300,-1))
        sizer_6.Add(self.default_path_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.icon_folder_bitmap = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("C:/Users/USUARIO/Desktop/NeuroRule/front/resources/img/guardar.png", wx.BITMAP_TYPE_ANY))
        sizer_6.Add(self.icon_folder_bitmap, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_colors = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Colors"), wx.HORIZONTAL)
        sizer_3.Add(sizer_colors, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_1 = wx.GridSizer(2, 2, 2, 2)
        sizer_colors.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_7, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Inputs")
        sizer_7.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.input_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,self.currentSettings.independentColor)
        
        sizer_7.Add(self.input_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_8, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Outputs")
        sizer_8.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.output_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,self.currentSettings.targetColor)
        
        sizer_8.Add(self.output_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_9, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Missing values")
        sizer_9.Add(label_3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.nan_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,colour=self.currentSettings.NanColor)
        
        sizer_9.Add(self.nan_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_10, 1, wx.EXPAND, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Outliers")
        sizer_10.Add(label_4, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.outliers_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,colour=self.currentSettings.outlierColor)
        
        sizer_10.Add(self.outliers_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        self.Bind(wx.EVT_BUTTON,self.OnChooseFolder,self.icon_folder_bitmap)
        self.Bind(wx.EVT_SPINCTRL,self.OnChangeFont,self.font_size_ctrl)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        self.Center()
    
    def OnChangeFont(self,evt):
        
        if self.original_font_size!=evt.GetPosition():
            self.restart=True
    
    def OnChooseFolder(self,evt):
        response=IOManage.GetPathFolder(self,"Select a new path").getResponse()
        if response['status']==Status.OK:
            self.default_path_ctrl.SetLabelText(response['data'])

    def OnApply(self,evt):
        font_size=self.font_size_ctrl.GetValue()

        if font_size<9 or font_size>20:
            wx.MessageBox("Invalid value for font size","Error",wx.ICON_ERROR)
        else:
            self.currentSettings.font_size=font_size
            self.currentSettings.defaultPath=self.default_path_ctrl.GetValue()
            self.currentSettings.independentColor=self.input_color_ctrl.GetColour()
            self.currentSettings.targetColor=self.output_color_ctrl.GetColour()
            self.currentSettings.NanColor=self.nan_color_ctrl.GetColour()
            self.currentSettings.outlierColor=self.outliers_color_ctrl.GetColour()

            message="Configuration saved!"
            if self.restart:
                message=message+" You need to restart the program to see the changes."
            wx.MessageBox(message,"Info",wx.OK)
            self.currentSettings.update_conf()
            self.EndModal(wx.ID_REFRESH)
            self.Destroy()

class CreateSetDialog(wx.Dialog):
    def __init__(self,parent,title):
        
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle(title)

        self.new_set=parent.new_set
        self.controller=parent.controller

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, title)
        label_1.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND, 0)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "New variable"), wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 15)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)

        label_name = wx.StaticText(self, wx.ID_ANY, "Name")
        sizer_9.Add(label_name, 0, wx.ALL, 4)

        self.variable_name_ctrl = wx.TextCtrl(self, wx.ID_ANY, "")
        sizer_9.Add(self.variable_name_ctrl, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(sizer_10, 1, wx.EXPAND | wx.TOP, 0)

        label_type = wx.StaticText(self, wx.ID_ANY, "Type")
        sizer_10.Add(label_type, 0, wx.ALL, 7)

        self.type_choice = wx.Choice(self, wx.ID_ANY, choices=["Numeric","Nominal"])
        self.type_choice.SetSelection(0)
        sizer_10.Add(self.type_choice, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        sizer_11 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Actions"), wx.HORIZONTAL)
        sizer_6.Add(sizer_11, 1, wx.ALL | wx.EXPAND, 15)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(sizer_12, 1, wx.EXPAND, 0)

        self.button_add_variable = wx.Button(self, wx.ID_ANY, "Add")
        sizer_12.Add(self.button_add_variable, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.button_remove_variable = wx.Button(self, wx.ID_ANY, "Remove")
        sizer_12.Add(self.button_remove_variable, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        self.button_add_variable.SetDefault()

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Set"), wx.VERTICAL)
        sizer_4.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 10)

        self.list_box_new_set = wx.ListBox(self, wx.ID_ANY, choices=[],style=wx.LB_MULTIPLE)
        sizer_5.Add(self.list_box_new_set, 1, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "Create")
        
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Bind(wx.EVT_BUTTON,self.OnAddVariable,self.button_add_variable)
        self.Bind(wx.EVT_BUTTON,self.OnRemoveVariable,self.button_remove_variable)
        self.Bind(wx.EVT_BUTTON,self.OnCreate,self.button_OK)
        self.Center()
        self.Layout()

    def OnCreate(self,evt): 

        if len(self.new_set)==0:
            wx.MessageBox("You can not create a set without variables.","Warning",wx.ICON_WARNING)
        else:    
            self.EndModal(wx.ID_APPLY)
            self.Destroy()


    def OnAddVariable(self,evt):

        name=self.variable_name_ctrl.GetValue()
        ok=validate_name(name)

        if not ok:
            wx.MessageBox("Not valid name for variable","Error",wx.ICON_ERROR)
        else:
            
            current_names=list(self.new_set.keys())
            if name in current_names:
                wx.MessageBox("There is already a variable with this name.","Warning",wx.ICON_WARNING)
            else:

                var_type=self.type_choice.GetStringSelection()

                if var_type=="Nominal":
                    self.new_set[name]=str
                elif var_type=="Numeric":
                    self.new_set[name]=float

                self.list_box_new_set.AppendItems([str(name+" ("+var_type+") ")])
                self.variable_name_ctrl.SetLabelText("")
        
    
    def OnRemoveVariable(self,evt):
        selections=self.list_box_new_set.GetSelections()
        strings=self.list_box_new_set.GetStrings()
        toDel=[]
    
        for selection in selections:
            full=strings[selection]
            name=full.split(" ")[0]
            del self.new_set[name]

            toDel.append(full)

        for elem in toDel:    
            strings.remove(elem)
        
        self.list_box_new_set.Clear()
        if len(strings)!=0:
            self.list_box_new_set.AppendItems(strings)


class MappingDialog(wx.Dialog):
    def __init__(self,parent, bins,variable):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Mapping dialog - BETA")

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
            rule=" range("+range+") -> new value("+name+")"
            
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
            
        pattern = r"range\((.*?)\) -> new value\((.*?)\)"


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


class HelpDialog(wx.Dialog):
    def __init__(self,parent,file,title):
    
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Help dialog")
        self.title=title
        f = open(file)
        self.content=json.load(f)
        f.close()

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)

        self.text_ctrl_1 = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.text_ctrl_1.ShowCancelButton(True)
        sizer_4.Add(self.text_ctrl_1, 0, wx.ALL, 10)

        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.BORDER_SUNKEN | wx.TR_HAS_BUTTONS | wx.TR_NO_BUTTONS | wx.TR_SINGLE)
        sizer_4.Add(self.tree, 1, wx.ALL | wx.EXPAND, 10)

        self._build_tree(self.content)
        sizer_webview = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_webview, 1, wx.ALL | wx.EXPAND, 10)

        self.browser = wxhtml2.WebView.New(self)

        # HTML content to render
        html_content = """
        <html>
        <body>
            <h1>Welcome the help menu!</h1>
            <p>Select the topic in order to get more information.</p>
        </body>
        </html>
        """

        self.browser.SetPage(html_content, "")

        sizer_webview.Add(self.browser, 1, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnChangeTreeSelection,self.tree)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetSize(900,800)
        self.Center()
        self.Layout()
    
    def OnChangeTreeSelection(self,evt):
        try:
            itemId=self.tree.GetSelection()
            if self.root!=itemId:
                selection=self.tree.GetItemText(itemId)
                parent_item=self.tree.GetItemParent(self.tree.GetSelection())
                parent=self.tree.GetItemText(parent_item)
                if parent_item==self.root:
                    path=self.content[selection]['content']['file']
                else:
                    path=self.content[parent]['child'][selection]['content']['file']
                
                with open(path, 'r') as file:
                    content = file.read()

                #self.browser.LoadURL("file:///"+file)
                self.browser.SetPage(content, "")

        except Exception as exc:
            print(exc)
        

    def _build_tree(self,content):
        

        self.root = self.tree.AddRoot(self.title)

        self._create_layers(content,self.root)

        self.tree.Expand(self.root)
    
    def _create_layers(self,layer,parent):
        keys=list(layer.keys())
        for key in keys:
            
            new_parent=self.tree.AppendItem(parent,key)
            
            if layer[key]['content']==False:
                self._create_layers(layer[key]['child'],new_parent)


class DetailsDialog(wx.Dialog):
    def __init__(self,parent,task):
        
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Task details")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        label_task = wx.StaticText(self, wx.ID_ANY, "Task:")
        label_task.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_4.Add(label_task, 0, wx.ALL, 10)

        task_name = wx.StaticText(self, wx.ID_ANY, task['name'])
        task_name.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        sizer_4.Add(task_name, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Details"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 0, wx.ALL, 10)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 5)

        label_date = wx.StaticText(self, wx.ID_ANY, "Date: ")
        sizer_7.Add(label_date, 0, 0, 0)

        task_date = wx.StaticText(self, wx.ID_ANY, task['date'])
        sizer_7.Add(task_date, 0, 0, 0)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_8, 1, wx.ALL | wx.EXPAND, 5)

        label_path= wx.StaticText(self, wx.ID_ANY, "Path: ")
        sizer_8.Add(label_path, 0, 0, 0)

        path=task['path']
        if path==None:
            path="Not saved yet!"
        task_path = wx.StaticText(self, wx.ID_ANY,path)
        sizer_8.Add(task_path, 1, 0, 0)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_9, 1, wx.ALL | wx.EXPAND, 5)

        label_size = wx.StaticText(self, wx.ID_ANY, "Size: ")
        sizer_9.Add(label_size, 0, 0, 0)

        if task['path']==None:
            size_str="Not saved yet!"
        else:
            size=os.path.getsize(task['path'])
            size=size/(1024*1024) #Convert to MB
            size_str=str(np.round(size,4))+" MB"

        task_size = wx.StaticText(self, wx.ID_ANY,size_str)
        sizer_9.Add(task_size, 1, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        #self.button_rename = wx.Button(self, wx.ID_APPLY, "Rename")
        #sizer_2.AddButton(self.button_rename)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.Center()
        self.Layout()


class LoadFileDialog(wx.Dialog):
    def __init__(self,parent,conf):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Load file")

        self.conf=conf

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Path"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.ALL  | wx.ALIGN_CENTER_VERTICAL, 10)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        self.path = wx.TextCtrl(self, wx.ID_ANY,value=self.conf['pathname'],style=wx.TE_READONLY)
        sizer_5.Add(self.path, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        self.button_change_path = wx.Button(self, wx.ID_ANY, "Change")
        sizer_5.Add(self.button_change_path, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Options"), wx.HORIZONTAL)
        sizer_3.Add(sizer_6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 0, 0, 0)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_8, 0, wx.ALL | wx.EXPAND, 10)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Separator")
        sizer_8.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.separator = wx.TextCtrl(self, wx.ID_ANY, ",")

        self._on_change_path(self.conf['pathname'])
        self.separator.SetMinSize((50, 23))
        sizer_8.Add(self.separator, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_9, 0, wx.ALL | wx.EXPAND, 10)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Decimal")
        sizer_9.Add(label_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.choice_decimal = wx.Choice(self, wx.ID_ANY, choices=[".", ","])
        self.choice_decimal.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.choice_decimal.SetSelection(0)
        sizer_9.Add(self.choice_decimal, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)


        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnChangePath,self.button_change_path)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_OK)
        self.button_OK.SetDefault()

        self.SetSize(800,200)
        self.Center()
        self.Layout()
    
    def _on_change_path(self,path):
        if str(path).endswith(".xlsx"):
            self.separator.Enable(False)
        else:
            self.separator.Enable(True)

    def OnApply(self,evt):
        self.conf['pathname']=self.path.GetValue()
        self.conf['dec']=self.choice_decimal.GetStringSelection()
        self.conf['sep']=self.separator.GetValue()
        
        self.EndModal(wx.ID_OK)

    def OnChangePath(self,evt):
        response=IOManage.LoadFile(self,evt).getResponse()
        if response['status']==Status.OK:
            self.path.SetLabelText(response['data'])
            self._on_change_path(response['data'])


class TraceDialog(wx.Dialog):
    def __init__(self,parent):
       
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Trace dialog")

        
        self.settings=parent.setting
        content=self._fill_text("all")
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_filter = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Filter by level"), wx.HORIZONTAL)
        sizer_1.Add(sizer_filter, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.cb_level=wx.ComboBox(self,id=wx.ID_ANY,value="all",choices=["all","INFO","ERROR","WARNING"], style=wx.CB_READONLY)

        sizer_filter.Add(self.cb_level,0,wx.ALL,5)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Logs"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.text_logs = wx.TextCtrl(self, wx.ID_ANY,content, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer_3.Add(self.text_logs, 1, wx.ALL | wx.EXPAND, 10)

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

        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_SAVE)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeFilter,self.cb_level)
        self.SetEscapeId(self.button_CLOSE.GetId())

        self.SetSize((800,500))
        self.Layout()
    
    def OnChangeFilter(self,evt):
        level=self.cb_level.GetValue()
        logs=self._fill_text(level)
        self.text_logs.SetLabelText(logs)

    def _fill_text(self,level):
        logs=""
        trace=Trace()
        history=trace.get_log_history()
        for log in history:
            if level!="all":
                if log['level']==level:
                    logs=logs+str(log['time'])+" - "+str(log['level'])+" - "+log['message']+"\n"
            else:
                logs=logs+str(log['time'])+" - "+str(log['level'])+" - "+log['message']+"\n"
        
        return logs

    def OnSave(self,evt):
        
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,defaultDir=self.settings.GetPath()).getResponse()

        if path['status']==Status.OK: 
            saver=Saver(path['data'],content=self.text_logs.GetLabelText())
            saver.save()
            wx.MessageBox("File saved succesfully in "+path['data'],"Info")
