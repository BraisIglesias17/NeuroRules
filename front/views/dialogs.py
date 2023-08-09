import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from back.IO.IOManage import IOManage
from back.data.contextData import ContextData
from back.respuestas import Status



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
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 20)

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

        self.SetEscapeId(self.button_CANCEL.GetId())
        
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
            
            self.Close(wx.OK)


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
        
        
        myGrid.CreateGrid(rows,1)
        myGrid.SetRowLabelSize(0)
        
        names=self.controller.get_names().getResponse()['data']

        myGrid.SetColLabelValue(0,'Variable')
        """
        labels=self.metrics.index
        for i in range(1,cols):
            print(i)
            myGrid.SetColLabelValue(i,labels[i])
        myGrid.SetGridLineColour(wx.Colour('#8a8a81'))
        #myGrid.SetCellEditor(6, 0, gridlib.GridCellFloatEditor())
        """        
        i=0 
        j=0
    
        for variable in names:
            
            
            myGrid.SetCellValue(i,j,str(variable))
            i+=1
            #myGrid.SetCellBackgroundColour(i, j, wx.Colour('#2c8a45'))
            """
            for index in self.metrics.index:
                    if index != 'count':
                        value=self.metrics[[variable]].loc[index]
                        myGrid.SetCellValue(i,j," "+str(round(value.values[0],2))+" ")
                        myGrid.SetReadOnly(i,j,True)
                    j+=1
            """     
        myGrid.AppendCols(1)
        myGrid.SetColLabelValue(myGrid.GetNumberCols() - 1," Type ")
        
        opciones_dropdown = ['Ignore','Property', 'Ingredient']

        
        editor_dropdown = gridlib.GridCellChoiceEditor(opciones_dropdown, allowOthers=False)
        for row in range(myGrid.GetNumberRows()):
            col = myGrid.GetNumberCols() - 1
            myGrid.SetCellValue(row, col, opciones_dropdown[0])
            myGrid.SetCellEditor(row, col, editor_dropdown)

        myGrid.AutoSize()
        myGrid.SetColSize(myGrid.GetNumberCols() - 1,100)
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
            dialog=MessageDialog(self,False,cadena)
            dialog.ShowModal()
        else:
            dialog=MessageDialog(self,False,"error")
            dialog.ShowModal()


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
        sizer_3.Add(sizer_4, 1, wx.ALL| wx.EXPAND, 10)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.EXPAND,10)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 0, wx.ALL | wx.EXPAND, 5)

        self.checkbox_delete_missing = wx.CheckBox(self, wx.ID_ANY, "Delete rows with missing values")
       
        sizer_7.Add(self.checkbox_delete_missing, 1, wx.ALL, 5)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_8, 1, wx.ALL | wx.EXPAND, 5)

        self.label_2 = wx.StaticText(self, wx.ID_ANY, "Sustitution strategy")
        sizer_8.Add(self.label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.combo_box_missing_sustitution = wx.ComboBox(self, wx.ID_ANY, choices=["None","Mean", "Median"],style=wx.CB_READONLY,value="None")
        sizer_8.Add(self.combo_box_missing_sustitution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Outliers"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 1, wx.ALL|wx.EXPAND,10)

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


        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 1, wx.ALL | wx.EXPAND, 5)

        self.label_3 = wx.StaticText(self, wx.ID_ANY, "Sustitution strategy")
        sizer_10.Add(self.label_3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.combo_box_outlier_sustitution = wx.ComboBox(self, wx.ID_ANY, choices=["None","Mean", "Median"],style=wx.CB_READONLY,value="None")
        sizer_10.Add(self.combo_box_outlier_sustitution, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)


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

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "Close")
        sizer_2.AddButton(self.button_CANCEL)

        self.Bind(wx.EVT_CHECKBOX,self.OnCheckMissing,self.checkbox_delete_missing)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckDeleteOutliers,self.checkbox_delete_outliers)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnChangeVariable,self.combo_box_variable)
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
                
                self.checkbox_delete_missing.SetValue(options['delete_missing'])
                self.combo_box_missing_sustitution.SetValue(options['substitute_missing'])
                self.checkbox_delete_outliers.SetValue(options['delete_outliers'])
                self.combo_box_outlier_sustitution.SetValue(options['substitute_outliers'])
                self.checkbox_highlight_outliers.SetValue(options['highlight_outliers'])
                
            else:
                wx.MessageBox("A problem has occurred","Error",wx.OK|wx.ICON_ERROR)


    def OnCheckDeleteOutliers(self,event):
        checked=self.checkbox_delete_outliers.GetValue()

        if checked:
            self.combo_box_outlier_sustitution.Enable(False)
            self.checkbox_highlight_outliers.Enable(False)
            self.label_3.Enable(False)
        else:
            self.combo_box_outlier_sustitution.Enable(True)
            self.checkbox_highlight_outliers.Enable(True)
            self.label_3.Enable(True)


    def OnCheckMissing(self,event):

        checked=self.checkbox_delete_missing.GetValue()
        #variable=self.combo_box_variable.GetValue()
        
        if checked:

            self.combo_box_missing_sustitution.Enable(False)
            self.label_2.Enable(False)
        else:
            self.combo_box_missing_sustitution.Enable(True)
            self.label_2.Enable(True)

    def OnApply(self,event):
        try:
            target=self.combo_box_variable.GetValue()
            dm=self.checkbox_delete_missing.GetValue()
            sm=self.combo_box_missing_sustitution.GetValue()
            do=self.checkbox_delete_outliers.GetValue()
            so=self.combo_box_outlier_sustitution.GetValue()
            ho=self.checkbox_highlight_outliers.GetValue()
            if target == "All":
                #Cambiar todos
                for variable in self.names:
                    result=self.parent.controller.set_cleanse_option(variable,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so}).getResponse()
                    
            else:
                result=self.parent.controller.set_cleanse_option(target,{'delete_missing':dm,'substitute_missing':sm,'delete_outliers':do,'highlight_outliers':ho,'substitute_outliers':so}).getResponse()
            
            if result['status']== Status.OK:
                wx.MessageBox("Changed succesfully submited ")
        except Exception as exc:
            wx.MessageBox(str(exc),"Error",wx.OK|wx.ICON_ERROR)
                
            
            


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

        label_2 = wx.StaticText(self, wx.ID_ANY, "Y Axis")
        sizer_7.Add(label_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.listbox_y_axis = wx.ListBox(self, wx.ID_ANY, choices=names)
        sizer_7.Add(self.listbox_y_axis, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

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

        self.radio_btn_frequency = wx.RadioButton(self, wx.ID_ANY, "Frequency")
        sizer_11.Add(self.radio_btn_frequency, (0, 2), (1, 1), wx.ALL, 5)

        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(sizer_12, 1, wx.ALL | wx.EXPAND, 10)

        self.checkbox_regression_line = wx.CheckBox(self, wx.ID_ANY, "Show Linear Regression Fit Line")
        sizer_12.Add(self.checkbox_regression_line, 1, wx.ALL | wx.EXPAND, 10)

        sizer_13 = wx.GridBagSizer(0, 0)
        sizer_12.Add(sizer_13, 1, wx.ALL | wx.EXPAND, 5)

        label_number_bins = wx.StaticText(self, wx.ID_ANY, "Number of Bins")
        sizer_13.Add(label_number_bins, (0, 0), (1, 1), wx.ALL, 10)

        self.input_number_bins = wx.SpinCtrl(self, wx.ID_ANY, min=0, max=100,initial=10)
        sizer_13.Add(self.input_number_bins, (0, 1), (1, 1), wx.ALL | wx.EXPAND, 10)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

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


        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_frequency)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_3d_graph)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnChangeType,self.radio_btn_2d_graph)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()
        # end wxGlade


    def OnChangeType(self,evt):
        
        if self.radio_btn_frequency.GetValue():
            
            self.listbox_y_axis.Enable(False)
            self.listbox_z_axis.Enable(False)
        elif self.radio_btn_2d_graph.GetValue():
            
            self.listbox_y_axis.Enable(True)
            self.listbox_z_axis.Enable(False)
        else:
            
            self.listbox_y_axis.Enable(True)
            self.listbox_z_axis.Enable(True)




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
               