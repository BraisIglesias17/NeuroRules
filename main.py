import wx
import wx.html2
import wx.grid as gridlib
import pandas as pd
from front.settings.settings import Settings 
from back.IO.IOManage import IOManage
#from dialogs import CreateSetDialog
from back.data.contextData import ContextData
from back.controller.controller import Controller
from back.respuestas import Status
from front.views.dialogs import VariableTypeDialog,RulesDialog,CleanDataDialog,GraphDialog,SummaryDialog
from back.validation.validation import Validator
import numpy as np

class MainWindow(wx.Frame):    
    def __init__(self,*args, **kwds):
        super().__init__(parent=None, title='Ruler')
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.createMenuBar()
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.setting=Settings()
        self.IO=IOManage()
        self.controller=Controller()
        self.init=False
        self.highlighted_cells=[]  
        self.highlighted_cols=[]

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 0, wx.ALL | wx.EXPAND, 15)

        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Data"), wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL, 10)

        self.import_file_button = wx.Button(self.panel, wx.ID_ANY, "Import data\n")
        sizer_4.Add(self.import_file_button, 1, wx.ALL | wx.EXPAND, 5)

        #self.create_set_button = wx.Button(self.panel, wx.ID_ANY, "Create set")
        #sizer_4.Add(self.create_set_button, 1, wx.ALL | wx.EXPAND, 5)

        self.clear_set_button = wx.Button(self.panel, wx.ID_ANY, "Clear")
        sizer_4.Add(self.clear_set_button, 1, wx.ALL | wx.EXPAND, 5)
        

        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Preprocess"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL, 10)

        self.clean_data_button = wx.Button(self.panel, wx.ID_ANY, "Clean data\n")
        sizer_5.Add(self.clean_data_button, 1, wx.ALL | wx.EXPAND, 5)

        self.preprocess_data_button = wx.Button(self.panel, wx.ID_ANY, "Preprocess data\n")
        sizer_5.Add(self.preprocess_data_button, 1, wx.ALL | wx.EXPAND, 5)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Analzye"), wx.HORIZONTAL)
        sizer_3.Add(sizer_6, 0, wx.ALL, 10)

        self.plot_data_button = wx.Button(self.panel, wx.ID_ANY, "Plot\n")
        sizer_6.Add(self.plot_data_button, 1, wx.ALL, 5)

        self.statistics_button = wx.Button(self.panel, wx.ID_ANY, "Statistics\n")
        sizer_6.Add(self.statistics_button, 1, wx.ALL, 5)

        self.summary_button = wx.Button(self.panel, wx.ID_ANY, "Summary\n")
        sizer_6.Add(self.summary_button, 1, wx.ALL, 5)

        
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Rules"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL, 10)

        self.next_button = wx.Button(self.panel, wx.ID_ANY, "Select variables\n")
        sizer_7.Add(self.next_button, 1, wx.ALL, 5)
        self.train_button = wx.Button(self.panel, wx.ID_ANY, "Train\n")
        sizer_7.Add(self.train_button, 1, wx.ALL, 5)
        self.train_button.Enable(False)
        
        self.grid_sizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Data Sheet"), wx.VERTICAL)
       
        
        sizer_1.Add(self.grid_sizer, 1, wx.EXPAND, 0)

        self.grid = wx.grid.Grid(self.panel, wx.ID_ANY)
        self.grid.CreateGrid(1000,25)
        self.grid_sizer.Add(self.grid, 1, wx.EXPAND, 0)
        

        #Declaracion de eventos
        
        self.Bind(wx.EVT_BUTTON,self.OnOpenFile,self.import_file_button)
        self.Bind(wx.EVT_BUTTON,self.OnClearGrid,self.clear_set_button)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,self.OnCellEdit)
        self.Bind(wx.EVT_BUTTON,self.OnNext,self.next_button)
        self.Bind(wx.EVT_BUTTON, self.OnTrain,self.train_button)
        self.Bind(wx.EVT_BUTTON,self.OnPreprocess,self.preprocess_data_button)
        self.Bind(wx.EVT_BUTTON,self.OnCleanData,self.clean_data_button)
        self.Bind(wx.EVT_BUTTON,self.OnGraph,self.plot_data_button)
        self.Bind(wx.EVT_BUTTON,self.OnSummary,self.summary_button)
        self.Bind(wx.EVT_BUTTON,self.OnPreprocess,self.statistics_button)
        #self.Bind(wx.EVT_BUTTON,self.OnCreateData,self.create_set_button)
        #self.Bind(wx.EVT_BUTTON,self.OnNext,self.statistics_button)
        
        
    
        self.enableButtons(False)
        self.panel.SetSizer(sizer_1)

        self.Layout()
        self.SetSize((1800, 900))
        self.Center()
        self.Show(True)


    def OnSummary(self,evt):
        dialog=SummaryDialog(self)
        dialog.ShowModal()


    def OnGraph(self,evt):
        dialog=GraphDialog(self)
        dialog.ShowModal()

    def OnCleanData(self,evt):
        dialog=CleanDataDialog(self,self.controller,self.setting)
        dialog.ShowModal()
        response=self.controller.get_data().getResponse()
        
        if response['status']==Status.OK:
            self.ClearGrid()
            self.updateGrid(response['data'])
        else:
            wx.MessageBox("A problem has occurred","Error",wx.OK|wx.ICON_ERROR)
    
        

        
    def OnPreprocess(self,event):
        wx.MessageBox('To do', 'To do', wx.OK | wx.ICON_WARNING)


    def OnTrain(self,event):
        print("ON TRAIN")
        #Validar datos
        rules=self.controller.create_models("model","params")
        dialog=RulesDialog(self,rules)
        dialog.ShowModal()

    
    def OnNext(self,event):
        dialog=VariableTypeDialog(self,self.setting,self.controller)
        code=dialog.ShowModal()    
    
        #if code == wx.OK:
        self.train_button.Enable(True)
        self.updateColors()
        

    def updateColors(self):
        independent=self.controller.get_independent_indexes().getResponse()['data']
        targets=self.controller.get_target_indexes().getResponse()['data']

        rows,cols=self.controller.get_data_shape().getResponse()['data']

        for row in range(rows):
            for col in range(cols):
                if col in targets:
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(self.setting.targetColor))
                    self.highlighted_cols.append([row,col])
                elif col in independent:
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(self.setting.independentColor))
                    self.highlighted_cols.append([row,col])
                else:
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(self.setting.defaultColor))
        
       
    def enableButtons(self,val):
        self.clean_data_button.Enable(val)
        self.clear_set_button.Enable(val)
        self.statistics_button.Enable(val)
        self.summary_button.Enable(val)
        self.plot_data_button.Enable(val)
        self.preprocess_data_button.Enable(val)
        self.next_button.Enable(val)

    def OnOpenFile(self,event):
        
        response=self.controller.load_content(self,event).getResponse()
        if response['status']==Status.OK:
            self.ClearGrid()
            self.updateGrid(response['data'])

            ##Inicializar settings de clean,process  y model
 
    def OnCellEdit(self,event):
        row,col=event.GetRow(),event.GetCol()
    
        response=self.controller.update_data_position(row,col,self.grid.GetCellValue(row,col)).getResponse()

        if not response['status'] == Status.OK:
            self.grid.SetCellValue(row,col,str(self.controller.get_position(row,col).getResponse()['data']))
            self.updateGrid(self.controller.get_data().getResponse()['data'])
        else:
            self.grid.SetCellBackgroundColour(row, col, wx.Colour('#FFFFFF'))
            

    def OnClearGrid(self,event):
        self.ClearGrid()
        self.enableButtons(False)
        self.train_button.Enable(False)

    def ClearGrid(self):
        
        self.grid.ClearGrid()     
        for coords in self.highlighted_cells:
            self.grid.SetCellBackgroundColour(coords[1], coords[0], wx.WHITE)

        for coords in self.highlighted_cols:
            self.grid.SetCellBackgroundColour(coords[0], coords[1], wx.WHITE)

        self.highlighted_cells=[]
        self.highlighted_cols=[]
        
                
    def updateGrid(self,df):
        
        i=0 
        rows,cols = df.shape
        if rows==0:
            rows=self.setting.initial_rows

        rows+=5
        #new_grid=self.createDataGrid(rows,cols)

        
        #self.grid_sizer.Replace(self.grid,new_grid)
        #self.grid.Destroy()

        #self.grid=new_grid
        
        for column in list(df.columns.values):
            self.grid.SetColLabelValue(i,column)
            #Verifico el tipo 
            self.types=df[column].dtypes
            i+=1
            
        
        for i in range(len(df.axes[1])):
            for j in range(len(df.axes[0])):
                if(i<50 and j<50):
                    value=str(df.loc[j][i])
                    
                    if Validator.check_float(df.loc[j][i]):
                        value=str(np.round(df.loc[j][i],2))

                    if value=="" or value=="nan":
                        self.grid.SetCellBackgroundColour(j, i, wx.Colour('#ba4941'))
                        self.highlighted_cells.append([i,j])
                    self.grid.SetCellValue(j,i,value)
                   
        if self.controller.contextData != None:
            self.enableButtons(True)
        
        #self.grid_sizer.Layout()
        #self.grid.AutoSize()
        
    def createDataGrid(self,rows,cols):
        myGrid = gridlib.Grid(self.panel)
        myGrid.CreateGrid(rows,cols)
        myGrid.SetRowLabelSize(0)
        myGrid.SetGridLineColour(wx.Colour('#8a8a81'))
        #myGrid.SetCellEditor(6, 0, gridlib.GridCellFloatEditor())
        return myGrid
 
    def createMenuBar(self):
        menubar = wx.MenuBar()  
        
        fileMenu = wx.Menu()  
        fileMenu.Append(wx.ID_NEW, '&Import file') 
        fileMenu.Append(wx.ID_ANY, '&Save')
        fileMenu.Append(wx.ID_ANY, '&Save as')

        modelMenu= wx.Menu()
        modelMenu.Append(wx.ID_ANY, '&Options')

        settingsMenu= wx.Menu()
        settingsMenu.Append(wx.ID_ANY, '&Settings')

        helpMenu = wx.Menu()  
        helpMenu.Append(wx.ID_ABOUT, '&About us')

        menubar.Append(fileMenu, '&File') 
        menubar.Append(modelMenu,'&Model') 
        menubar.Append(settingsMenu,'&Settings') 
        menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)  

if __name__ == '__main__':
    app = wx.App()
    
    frame = MainWindow(None, wx.ID_ANY, "")
    
    app.MainLoop()
    




