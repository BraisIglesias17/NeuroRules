import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from back.IO.IOManage import IOManage
from back.data.contextData import ContextData
from back.respuestas import Status
from back.statistic.statistic import StatisticTest
from ..plots import plot_2d,plot_3d,plot_hist, plot_regression,plot_boxplot,plot_correlation_matrix
import numpy as np

class VariableTypeDialog(wx.Dialog):
    def __init__(self,parent,settings,controller):
        # begin wxGlade: VariableTypeDialog.__init__
        super(VariableTypeDialog, self).__init__(parent, size = (1000,1000)) 
        
        self.SetTitle("Select variables type")
        
        self.setting=settings
        self.IO=IOManage()
        self.controller=controller
        self.metrics=self.controller.get_summary().getResponse()['data']
        #Datos globales
        self.data=pd.DataFrame()

        self.remove_non_used_variables=False
        self.independent_variables=[]
        self.targets=[]
        self.names=self.controller.get_names().getResponse()['data']
        
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

    def OnCancel(self,event):
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
            
            for row in range(myGrid.GetNumberRows()):
                col = myGrid.GetNumberCols() - 1
                myGrid.SetCellEditor(row, col, editor_dropdown) ## LANZA EXCEPCION
                myGrid.SetCellValue(row, col, opciones_dropdown[0])
                
            
            myGrid.AutoSize()
            myGrid.SetColSize(myGrid.GetNumberCols() - 1,100)
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
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        
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
        print(message)
        label_message = wx.StaticText(self, wx.ID_ANY, message)
        sizer_3.Add(label_message, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)

        if status:
            print("ICON OK")
        else:
            print("ICON NO OK")
        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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
        self.SetSize((850, 481))
        self.SetTitle("Summary")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Statistics"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 10)

        self.IO=parent.IO
        self.names=parent.controller.get_names().getResponse()
        self.summary=parent.controller.get_summary().getResponse()

        if self.names['status']== Status.OK and self.summary['status']== Status.OK:
            self.names=self.names['data']
            self.summary=self.summary['data']
        else:
            wx.MessageBox("A problem has occurred")

        
        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY)
        self.grid_1=self.createDataGrid(self.grid_1,len(self.names))
        
        sizer_3.Add(self.grid_1, 1, wx.ALL | wx.EXPAND, 5)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "Save")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        #self.SetAffirmativeId(self.button_OK.GetId())
        self.Bind(wx.EVT_BUTTON,self.OnSave,self.button_OK)
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade

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
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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


class StatisticDialog(wx.Dialog):
    def __init__(self,parent, *args, **kwds):
        # begin wxGlade: StatisticDialog.__init__
        super(StatisticDialog, self).__init__(parent)
        self.SetTitle("Statistics")
        self.controller=parent.controller
        self.names=list(parent.names)
        self.one_variable_test=False
        tests=StatisticTest.get_tests()
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "A "), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_A = wx.ComboBox(self, wx.ID_ANY, choices=self.names,value="First variable",style=wx.CB_READONLY)
        sizer_4.Add(self.combo_box_A, 1, wx.ALL, 5)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "B"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_B = wx.ComboBox(self, wx.ID_ANY, choices=self.names,value="Second variable (if needed)", style=wx.CB_READONLY)
        sizer_5.Add(self.combo_box_B, 1, wx.ALL, 5)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Test"), wx.HORIZONTAL)
        sizer_3.Add(sizer_6, 0, wx.ALL | wx.EXPAND, 10)

        self.combo_box_test = wx.ComboBox(self, wx.ID_ANY, choices=tests,value="Test to apply", style=wx.CB_READONLY)
        sizer_6.Add(self.combo_box_test, 1, wx.ALL, 5)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Other options"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 10)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)

        self.checkbox_automatic_tests = wx.CheckBox(self, wx.ID_ANY, "Run automatic test")
        sizer_8.Add(self.checkbox_automatic_tests, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.checkbox_corr = wx.CheckBox(self, wx.ID_ANY, "Show global correlation matrix")
        sizer_8.Add(self.checkbox_corr, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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
        self.Bind(wx.EVT_CHECKBOX,self.OnChangeCorr,self.checkbox_corr)
        #self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade

    def OnChangeCorr(self,evt):
        if self.checkbox_corr.GetValue():
            self.combo_box_A.Enable(False)
            self.combo_box_B.Enable(False)
            self.combo_box_test.Enable(False)
        else:
            self.combo_box_A.Enable(True)
            self.combo_box_B.Enable(True)
            self.combo_box_test.Enable(True)

    def validate_choice(self,val):
        if val=="":
            return False
        return True

    def OnRun(self,event):
        test=self.combo_box_test.GetValue()
        a=self.combo_box_A.GetValue()
        b=self.combo_box_B.GetValue()
        other_option=False
        
        if self.checkbox_corr.GetValue():
            df=self.controller.get_data().getResponse()['data']
            plot_correlation_matrix(df)
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
                    if test == 'Shapiro':   
                        self.OnLaunchResulDialog(StatisticTest.shapiro_wilk,test,variables=[x],names=[a])
                    elif test=='ANOVA' and complete:
                        self.OnLaunchResulDialog(StatisticTest.ANOVA,test,variables=[x,y],names=[a,b])
                    
                    #TO DO TESTS
                    
                    

        
    def OnLaunchResulDialog(self,test,test_name,variables,names):
        
        title=""
        message=""
        if len(variables)==2:
            result=test(variables[0],variables[1])
            a=names[0]
            b=names[1]
            title=str("Test "+test_name+" on "+a+" and "+b)
            message=str("to determine that there is significant differences between "+a+" and "+b)
        else:
            result=test(variables[0])
            title="Test "+test_name+" on "+names[0]
            message="to determine that this variable has a normal distribution"

        dialog=TestResultDialog(self,title,{'pvalue':result.pvalue},message)
        dialog.ShowModal()
        
        

        


    def OnChangeTest(self,event):
        if self.combo_box_test.GetValue() == 'Shapiro' or self.combo_box_test.GetValue() == 'McNemar' or self.combo_box_test.GetValue() == 'Kolmorov':
            self.combo_box_B.Enable(False)
            self.one_variable_test=True
        else:
            self.combo_box_B.Enable(True)
            self.one_variable_test=False



class TestResultDialog(wx.Dialog):
    def __init__(self,parent,name,result,explanation):
        # begin wxGlade: TestResultDialog.__init__
        super(TestResultDialog, self).__init__(parent)
        self.SetTitle(name)
        self.result=result

        self.image="C:/Users/USUARIO/Desktop/NeuroRule/front/resources/ok.png"
        self.header="Succesful"
        
        pvalue=np.round(self.result['pvalue'],4)
        
        if self.result['pvalue']>0.05:
            self.image="C:/Users/USUARIO/Desktop/NeuroRule/front/resources/x.png"
            self.header="Unsuccesful"

            explanation="There is NO significicant statistical evidence "+explanation
        else:
            explanation="There is significicant statistical evidence "+explanation

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

        label_2 = wx.StaticText(self, wx.ID_ANY, "p-value")
        sizer_6.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP, 10)

        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, str(pvalue))
        #self.text_ctrl_1.SetMinSize((70, 23))
        self.text_ctrl_1.Enable(False)
        sizer_6.Add(self.text_ctrl_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Explanation"), wx.VERTICAL)
        sizer_5.Add(sizer_7, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        label_3 = wx.StaticText(self, wx.ID_ANY, explanation)
        sizer_7.Add(label_3, 0, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())

        self.Layout()
        # end wxGlade

class SummaryPickDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Summary pick")
        self.parent=parent
        names=parent.names
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
        sizer_4.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 5)

        groupby_variables=self.parent.string_variable_names
        groupby_variables.append("None")
        self.combo_box_group = wx.ComboBox(self, wx.ID_ANY, choices=groupby_variables,value="None", style=wx.CB_READONLY)
        if len(groupby_variables)==1:
            self.combo_box_group.Enable(False)

        sizer_6.Add(self.combo_box_group, 0, wx.ALL, 5)

        self.checkbox_all_variable = wx.CheckBox(self, wx.ID_ANY, "Show all variables summary")
        sizer_3.Add(self.checkbox_all_variable, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade
    
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
            self.Close()
        else:
            variable=self.combo_box__variable.GetValue()
            group=self.combo_box_group.GetValue()

            print(f'var:{variable},group:{group}')