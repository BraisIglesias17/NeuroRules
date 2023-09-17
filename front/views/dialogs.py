import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from back.IO.IOManage import IOManage
from back.data.contextData import ContextData
from back.respuestas import Status
from back.statistic.statistic import StatisticTest
from ..plots import plot_2d,plot_3d,plot_hist, plot_regression,plot_boxplot,plot_correlation_matrix,plot_countplot,plot_histogram_grouped, plot_general_group,plot_covariance_matrix
import numpy as np
import copy
import math

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
        sizer_1.Add(sizer_3, 0, wx.EXPAND, 30)

        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid=self.createDataGrid(self.grid,len(self.names))
        sizer_3.Add(self.grid, 1,wx.CENTER, 30)

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
        #self.Bind(wx.CHK_CHECKED,self.OnCheck,self.checkbox_1)

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

    def OnCheck(self,event):
        print(event)

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
        # end wxGlade

    def OnSave(self,event):
        result=IOManage.OnSaveAs(self,event,self.rules_to_string,message="Save rules",wildcard=".txt files (*.txt)|*.txt").getResponse()
        if result['status']:
            
            cadena=str("Archivo guardado con éxito en "+result['data'])
            #dialog=MessageDialog(self,False,cadena)
            wx.MessageBox(cadena,"Info")
            
        else:
            wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)
            #dialog=MessageDialog(self,False,"error")
            


    def writeRules(self,rules):
        cadena="Rules:\n"
        for i in rules[0]:
            
            cadena=cadena+ i + "\n\n"
        
        self.rules_to_string=cadena
        self.rules_text_field.SetValue(cadena)
        



class MessageDialog(wx.Dialog):
    def __init__(self,parent,status,message):
        # begin wxGlade: MessageDialog.__init__
        super(MessageDialog, self).__init__(parent)
        
        
        self.SetSize((450, 150))
        self.SetTitle("Information")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        
        label_message = wx.StaticText(self, wx.ID_ANY, message)
        sizer_3.Add(label_message, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)

        if status:
            print("ICON OK")
        else:
            print("ICON NO OK")
        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 7)

        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        sizer_2.AddButton(self.button_CLOSE)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetEscapeId(self.button_CLOSE.GetId())

        self.Layout()


class CleanDataDialog(wx.Dialog):
    def __init__(self,parent,controller,settings):
        # begin wxGlade: CleanDataDialog.__init__
        super(CleanDataDialog, self).__init__(parent)
        self.SetTitle("Clean data")
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
            


class GraphDialog(wx.Dialog):
    def __init__(self,parent):
        # begin wxGlade: GraphDialog.__init__


        super(GraphDialog, self).__init__(parent)
        self.SetTitle("Graph")

        self.controller=parent.controller

        resp=self.controller.get_names().getResponse()
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

        self.Bind(wx.EVT_BUTTON,self.generate_graph,self.button_OK)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade

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
                plot_boxplot({'x':{'name':x,'data':data[x]}},options)



class SummaryDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(SummaryDialog, self).__init__(parent)
        self.SetSize((810, 481))
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
        result=self.IO.OnSaveAs(self,event,self.summary,message="Save summary",wildcard="(*.csv)|*.csv|(*.xlsx)|*.xlsx").getResponse()
        if result['status'] == Status.OK:
            
            cadena=str("File saved succesfully in "+result['data'])
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

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("C:\\Users\\USUARIO\\Desktop\\NeuroRule\\front\\resources\\logo_128x128.png", wx.BITMAP_TYPE_ANY))
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

class ShowIdentifierColsDialog(wx.Dialog):
    def __init__(self,parent):
        
        super(ShowIdentifierColsDialog, self).__init__(parent)
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
        
            


class StatisticDialog(wx.Dialog):
    def __init__(self,parent, *args, **kwds):
        # begin wxGlade: StatisticDialog.__init__
        super(StatisticDialog, self).__init__(parent)
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
        

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade        

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
                        grouping_values=np.unique(y)
                        
                        dict_y={}
                        for group in grouping_values:
                            dict_y[group]=x[y==group]

                        self.OnLaunchGroupingResultDialog(StatisticTest.ANOVA,test,dict_y,grouping_values,names=[a,b],msg="to determine that there is significant differences between ")
                    elif 'Pearson' in test and complete:
                        self.OnLaunchResulDialog(StatisticTest.pearson,test,variables=[x,y],names=[a,b],condition=False,msg="to determine that there is correlation between ")
                    
                    #TO DO TESTS
                    
                    

    def OnLaunchGroupingResultDialog(self,test,test_name,dict_y,groups,names,msg=""):
        i=0
        j=0
        different_pairs=[]
        not_different_pairs=[]
        pvalues=[]
        for i in range(0,len(groups)-1):
            for j in range(i+1,len(groups)):
                
                result=test(dict_y[groups[i]],dict_y[groups[j]])
                pvalues.append(np.round(result.pvalue,3))
                if result.pvalue<0.05:
                    different_pairs.append(str(groups[i]+" and "+groups[j]+" p-value ("+str(np.round(result.pvalue,3))+")"))
                else:
                    not_different_pairs.append(str(groups[i]+" and "+groups[j]+" p-value ("+str(np.round(result.pvalue,3))+")"))


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
        self.result=result

        self.image="C:/Users/USUARIO/Desktop/NeuroRule/front/resources/x.png"
        self.header="Unsuccesful"
        pvalues=self.result['pvalue']
        self.single_result=len(pvalues)==1

        if self.single_result:
            pvalue=np.round(self.result['pvalue'][0],4)
            
            if (lower and pvalue>0.05) or (lower==False and pvalue<0.05):
                self.image="C:/Users/USUARIO/Desktop/NeuroRule/front/resources/ok.png"
                self.header="Succesful"

                explanation="\nThere is significicant statistical evidence "+explanation
            else:
                explanation="\nThere is NO significicant statistical evidence "+explanation
        else:
            
            for pvalue in pvalues:
                if (lower and pvalue>0.05) or (lower==False and pvalue<0.05):
                    self.image="C:/Users/USUARIO/Desktop/NeuroRule/front/resources/ok.png"
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
        sizer_7.Add(label_3, 0, wx.EXPAND, 10)

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
        
        self.parent=parent
        self.variable=variable
        self.group=group
        self.numeric=numeric
        isGrouped=True
        message=str(variable+" grouped by "+group)
        label="Group"
        plottable=True
        #Obtain summary
        if group=="None":
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
        
        self.grid_1=self.createDataGrid(self.grid_1,data,variable,isGrouped)
    
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

        """
        self.change_inputsOuputs = wx.Button(self, wx.ID_ANY, "Change")
        sizer_5.Add(self.change_inputsOuputs, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        """
        

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
            #print(result['data'])
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