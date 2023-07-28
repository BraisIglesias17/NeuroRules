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
        #self.Bind(wx.CHK_CHECKED,self.OnCheck,self.checkbox_1)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())
        
        self.Layout()
        # end wxGlade

    def OnCheck(self,event):
        print(event)

    def OnApply(self,event):
        if len(self.independent_variables)==0:
            print("ERROR")
        elif len(self.targets)==0:
            print("ERROR")
        else:
            self.controller.set_independent_variables(self.independent_variables)
            self.controller.set_targets(self.targets)
            print(f'{self.independent_variables},{self.targets}')
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
        
        
        self.Layout()
        # end wxGlade

    def OnSave(self,event):
        result=IOManage.OnSaveAs(self,event,self.rules_to_string).getResponse()
        if result['status']:
            print(f"Imagen guardada con éxito en {result['data']}")
            cadena=str("Imagen guardada con éxito en "+result['data'])
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