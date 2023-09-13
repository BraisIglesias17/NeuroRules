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
from front.views.dialogs import VariableTypeDialog,RulesDialog,CleanDataDialog,GraphDialog,SummaryDialog,AboutUsDialog,ShowHiddenDialog,SummaryPickDialog,StatisticDialog,CreateTaskDialog
from back.validation.validation import Validator
import numpy as np
import sys

class MainWindow(wx.Frame):    
    def __init__(self,*args, **kwds):
        super().__init__(parent=None, title='Ruler')
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.ROW_BOUND=1000
        self.COL_BOUND=30

        self.SetIcon(wx.Icon('./front/resources/logo_50x50.png',type=wx.BITMAP_TYPE_PNG))
        self.SetTitle("NeuroRule 1.0.0")
        font=self.GetFont()
        print(f'Size:{font.GetPointSize()}, family:{font.GetFamily()}')
        self.createMenuBar()
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.setting=Settings()
        self.IO=IOManage()
        self.controller=Controller()
        self.init=False
        self.highlighted_cells=[]  
        self.highlighted_cols=[]
        self.initial_col_names=[]
        self.start=True
        self.names=[]

        self.float_variable_names=[]
        self.int_variable_names=[]
        self.string_variable_names=[]

        self.hidden_columns=[]
        self.names_to_show=[]
        self.filename=""


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

        
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Task"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL, 10)

        self.next_button = wx.Button(self.panel, wx.ID_ANY, "Select variables\n")
        sizer_7.Add(self.next_button, 1, wx.ALL, 5)
        self.train_button = wx.Button(self.panel, wx.ID_ANY, "Create Task\n")
        sizer_7.Add(self.train_button, 1, wx.ALL, 5)
        self.train_button.Enable(False)
        
        self.grid_sizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Data Sheet"), wx.VERTICAL)
       
        
        sizer_1.Add(self.grid_sizer, 1, wx.EXPAND, 0)
        self.grid = wx.grid.Grid(self.panel, wx.ID_ANY)
        self.grid.CreateGrid(1000,25)
        self.grid_sizer.Add(self.grid, 1, wx.EXPAND, 0)
        
        self.status_bar=self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-1,300])
        self.status_bar.SetStatusText("  Empty sheet")
        self.status_bar.SetStatusText("None data",1)

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
        self.Bind(wx.EVT_BUTTON,self.OnStatistics,self.statistics_button)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK,self.OnCickLabelCell)
        self.Bind(wx.EVT_CLOSE,self.OnExit)
        
        #self.Bind(wx.EVT_BUTTON,self.OnCreateData,self.create_set_button)
        #self.Bind(wx.EVT_BUTTON,self.OnNext,self.statistics_button)
        
        self.enableButtons(False)
        self.panel.SetSizer(sizer_1)

        self.Layout()
        self.SetSize((1800, 900))
        self.Center()
        self.Show(True)

    def OnStatistics(self,evt):
        dialog=StatisticDialog(self)
        dialog.ShowModal()

    def OnSummary(self,evt):
        #dialog=SummaryDialog(self)
        dialog=SummaryPickDialog(self)
        dialog.ShowModal()


    def OnGraph(self,evt):
        dialog=GraphDialog(self)
        dialog.ShowModal()

    def OnCleanData(self,evt):
        dialog=CleanDataDialog(self,self.controller,self.setting)
        code=dialog.ShowModal()

        if code==wx.ID_APPLY:
            response=self.controller.get_data().getResponse()
            
            if response['status']==Status.OK:
                self.ClearGrid()
                self.updateGrid(response['data'])
            else:
                wx.MessageBox("A problem has occurred","Error",wx.OK|wx.ICON_ERROR)

    def OnExit(self,event):
        sys.exit(0)
        
    def OnPreprocess(self,event):
        wx.MessageBox('To do', 'To do', wx.OK | wx.ICON_WARNING)


    def OnTrain(self,event):
        print("ON TRAIN")
        #Validar datos
        dialog=CreateTaskDialog(self)
        dialog.Show()
        """
        rules=self.controller.create_models("model","params")
        dialog=RulesDialog(self,rules)
        dialog.ShowModal()
        """
        

    
    def OnNext(self,event):
        
        dialog=VariableTypeDialog(self)
        code=dialog.ShowModal()    
    
        if code == wx.OK:
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
            self.updateGrid(response['data']['data'])
            self.filename=response['data']['file']
            
            self.SetStatusText(str(" Working on "+self.filename))

           
 
    def OnCellEdit(self,event):
        row,col=event.GetRow(),event.GetCol()
    

        response=self.controller.update_data_position(row,col,self.grid.GetCellValue(row,col)).getResponse()

        if not response['status'] == Status.OK:
            self.grid.SetCellValue(row,col,str(self.controller.get_position(row,col).getResponse()['data']))
            wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
        else:
            self.grid.SetCellBackgroundColour(row, col, wx.Colour('#FFFFFF'))
            

    def OnClearGrid(self,event):
        self.ClearGrid()
        self.controller.clear_data()
        self.enableButtons(False)
        self.train_button.Enable(False)
        self.restoreStatus()
        


    def ClearGrid(self):
        
        self.grid.ClearGrid()     
        for coords in self.highlighted_cells:
            self.grid.SetCellBackgroundColour(coords[1], coords[0], wx.WHITE)

        for coords in self.highlighted_cols:
            self.grid.SetCellBackgroundColour(coords[0], coords[1], wx.WHITE)

        self.highlighted_cells=[]
        self.highlighted_cols=[]

        for i in range(0,len(self.initial_col_names)):
            self.grid.SetColLabelValue(i,self.initial_col_names[i])
        self.initial_col_names=[]
        self.start=True
        

    def updateStatus(self,rows,cols):
        message=str(rows)+" rows, "+str(cols)+" cols"
        self.SetStatusText(message,1)
    

    def restoreStatus(self):
        self.SetStatusText(" None existing file")
        self.SetStatusText("None data",1)


    def updateGrid(self,df):
        
        i=0 
        rows,cols = df.shape
        if rows==0:
            rows=self.setting.initial_rows

        self.updateStatus(rows,cols)

        rows+=5
           
        i=0
        self.names=[]
        self.names=df.columns.values
        for column in list(df.columns.values):
            if self.start:
                self.initial_col_names.append(self.grid.GetColLabelValue(i))
            
            type=df.dtypes[i]
            
            
            if str(type).find("int") != -1:
                
                self.grid.SetColFormatNumber(i)
            elif str(type).find("float") != -1:
                self.grid.SetColFormatFloat(i,-1,2)

            self.grid.SetColLabelValue(i,column)
            #Verifico el tipo 
            self.types=df[column].dtypes
            i+=1
        self.start=False

        
        
        for j in range(i,len(self.initial_col_names),1):   
            
            self.grid.SetColLabelValue(j,self.initial_col_names.pop(j))

        

        for i in range(len(df.axes[1])):
            for j in range(len(df.axes[0])):
                if(i<self.COL_BOUND and j<self.ROW_BOUND):
                    value=str(df.loc[j][i])
                    
                    
                    if value=="" or value=="nan":
                        self.grid.SetCellBackgroundColour(j, i, wx.Colour(self.setting.NanColor))
                        self.highlighted_cells.append([i,j])
                    
                    elif Validator.check_float(df.loc[j][i]) and not Validator.check_integer(df.loc[j][i]):
                        
                        value=str(np.round(df.loc[j][i],2))

                    
            
                    self.grid.SetCellValue(j,i,value)
                   
        if not df.empty:
            self.enableButtons(True)
        else:
            self.enableButtons(False)
        
        self.float_variable_names,self.int_variable_names,self.string_variable_names=self.controller.get_types().getResponse()['data']

        #self.grid_sizer.Layout()
        #self.grid.AutoSize()
        
    def createDataGrid(self,rows,cols):
        myGrid = gridlib.Grid(self.panel)
        myGrid.CreateGrid(rows,cols)
        myGrid.SetRowLabelSize(0)
        myGrid.SetGridLineColour(wx.Colour('#8a8a81'))
        #myGrid.SetCellEditor(6, 0, gridlib.GridCellFloatEditor())
        return myGrid
    
    def OnCickLabelCell(self,evt):
        position = evt.GetPosition()
        row = evt.GetRow()
        col = evt.GetCol()

        shape=self.controller.get_data_shape().getResponse()
        if col !=-1:
            if shape['status']==Status.OK:
                shape=shape['data']

                if shape[1]>col:
                    position[1]+=80
                    menu = wx.Menu()
                    changeName=menu.Append(wx.ID_ANY, "Change column name")
                    hideColumn=menu.Append(wx.ID_ANY, "Hide column")
                    deleteColumn=menu.Append(wx.ID_ANY, "Delete column")
                    
                    self.Bind(wx.EVT_MENU,lambda event: self.OnChangeName(event,col),changeName)
                    self.Bind(wx.EVT_MENU,lambda event: self.OnDeleteColumn(event,col),deleteColumn)
                    self.Bind(wx.EVT_MENU,lambda event: self.OnHideColumn(event,col),hideColumn)
                    self.PopupMenu(menu, position)

                    
                    menu.Destroy()
        else:
            if shape['status']==Status.OK:
                shape=shape['data']

                if shape[0]>row:
                    position[1]+=100
                    position[0]+=10
                    menu = wx.Menu()
                    deleteColumn=menu.Append(wx.ID_ANY, "Delete row")
                    
                    self.Bind(wx.EVT_MENU,lambda event: self.OnDeleteRow(event,row),deleteColumn)
                    self.PopupMenu(menu, position)

                    
                    menu.Destroy()


        
    
    def OnChangeName(self,event,col):
        current_name=self.names[col]
        dialog=wx.TextEntryDialog(self,"New name","Enter new name for "+current_name,value="")
        code=dialog.ShowModal()

        if code == wx.ID_OK:
            new_value=dialog.GetValue()
            result=self.controller.rename_col(new_value,current_name).getResponse()

            if result['status']!=Status.OK:
                wx.MessageBox(result['data'],"Error",wx.OK|wx.ICON_ERROR)
            else:
                data=self.controller.get_data().getResponse()['data']
                
                #reemplazar elementos de la lista
                self.names[col]=new_value
                
                index=0
                toSubstitute=[]
                if current_name in self.int_variable_names:
                    index=self.int_variable_names.index(current_name)
                    toSubstitute=self.int_variable_names
                elif current_name in self.float_variable_names:
                    index=self.float_variable_names.index(current_name)
                    toSubstitute=self.float_variable_names
                else:
                    index=self.string_variable_names.index(current_name)
                    toSubstitute=self.string_variable_names

                toSubstitute[index]=new_value

                self.grid.SetColLabelValue(col,new_value)
            
        

    def OnDeleteColumn(self,event,col):
        label=self.grid.GetColLabelValue(col)
        message=str("Are you sure you want to delete "+label+" ?")
        
        col=[col]
        cols=self.grid.GetSelectedCols()
        if len(cols) > 1:
            col=cols
            message="Are you sure you want to delete "+str(len(cols))+" cols ?"

        code=wx.MessageBox(message,"Info",wx.YES_NO| wx.ICON_INFORMATION)
        if code==wx.YES:
            result=self.controller.delete_col(col).getResponse()
            if result['status']!=Status.OK:
                wx.MessageBox(result['data'],"Error",wx.OK| wx.ICON_ERROR)
            else:
                response=self.controller.get_data().getResponse()
                if response['status']==Status.OK:
                    self.ClearGrid()
                    self.updateGrid(response['data'])

    def OnDeleteRow(self,event,row):
        message="Are you sure you want to delete this row ?"
        row=[row]
        rows=self.grid.GetSelectedRows()
        if len(rows) > 1:
            row=rows
            message="Are you sure you want to delete "+str(len(rows))+" rows ?"

        code=wx.MessageBox(str(message),"Info",wx.YES_NO| wx.ICON_INFORMATION)
        if code==wx.YES:
            result=self.controller.delete_row(row).getResponse()
            if result['status']!=Status.OK:
                wx.MessageBox(result['data'],"Error",wx.OK| wx.ICON_ERROR)
            
            else:
                
                response=self.controller.get_data().getResponse()
                if response['status']==Status.OK:
                    
                    self.ClearGrid()
                    self.updateGrid(response['data'])
                

    def OnHideColumn(self,event,col):
        selections=(self.grid.GetSelectedCols())
        if col not in selections:
            selections.append(col)
        self.hidden_columns=selections
      
        for column in selections:
            self.grid.HideCol(column)
    
    def OnShowHidden(self,event):
        if len(self.hidden_columns)==0:
            wx.MessageBox("There is no hidden columns")
        else:
            dialog=ShowHiddenDialog(self)
            code=dialog.ShowModal()
            if code==wx.OK:
                for name in self.names_to_show:
                    index=list(self.names).index(name)
                    self.hidden_columns.remove(index)
                    self.grid.ShowCol(index)
        
 
    def OnAboutUs(self,event):
        dialog=AboutUsDialog(self)
        dialog.ShowModal()


    def createMenuBar(self):
        menubar = wx.MenuBar()  
        
        fileMenu = wx.Menu()  
        fileMenu.Append(wx.ID_NEW, '&Import file') 

        item=wx.MenuItem(fileMenu,wx.ID_ANY,'&Save')
        image = wx.Image('./front/resources/guardar.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        #wx.Bitmap.Rescale(image,wx.Size(16,16))
        item.SetBitmap(image)

        fileMenu.Append(item)
        fileMenu.Append(wx.ID_ANY, '&Save as')

        modelMenu= wx.Menu()
        modelMenu.Append(wx.ID_ANY, '&Options')

        settingsMenu= wx.Menu()
        settingsMenu.Append(wx.ID_ANY, '&Settings')

        preprocessSubmenu=wx.Menu()
        preprocessSubmenu.Append(wx.ID_ANY,"&Options")
        preprocessSubmenu.Append(wx.ID_ANY,"&Cleanse")
        preprocessSubmenu.Append(wx.ID_ANY,"&Preprocess")

        analyzeSubmenu=wx.Menu()
        analyzeSubmenu.Append(wx.ID_ANY,"&Options")
        analyzeSubmenu.Append(wx.ID_ANY,"&Plot")
        analyzeSubmenu.Append(wx.ID_ANY,"&Statistics")
        analyzeSubmenu.Append(wx.ID_ANY,"&Summary")

        dataMenu=wx.Menu()
        dataMenu.Append(wx.ID_ANY,"&Create set")
        dataMenu.Append(wx.ID_ANY,"&Clear data")
        dataMenu.AppendSubMenu(preprocessSubmenu,"Data processing")
        dataMenu.AppendSubMenu(analyzeSubmenu,"Data analysis")

        viewMenu=wx.Menu()
        item=wx.MenuItem(viewMenu,wx.ID_ANY,'&Show hidden columns')
        
        viewOptionsMenu=wx.Menu()
        viewOptionsMenu.Append(wx.ID_ANY,'&Show rules options')
        viewOptionsMenu.Append(wx.ID_ANY,'&Show model option')
        viewOptionsMenu.Append(wx.ID_ANY,'&Show analysis options')
        viewOptionsMenu.Append(wx.ID_ANY,'&Show preprocess options')
        
        showHidden=viewMenu.Append(item)
        viewMenu.AppendSubMenu(viewOptionsMenu,"Display options")

        helpMenu = wx.Menu()  
        aboutUsOption=helpMenu.Append(wx.ID_ABOUT, '&About us')

        menubar.Append(fileMenu, '&File') 
        menubar.Append(dataMenu,"&Data")
        menubar.Append(modelMenu,'&Model')
        menubar.Append(viewMenu,'&View')  
        menubar.Append(settingsMenu,'&Settings') 
        menubar.Append(helpMenu, '&Help')

        self.Bind(wx.EVT_MENU,self.OnShowHidden,showHidden)
        self.Bind(wx.EVT_MENU,self.OnAboutUs,aboutUsOption)

        self.SetMenuBar(menubar)  

if __name__ == '__main__':
    app = wx.App()
    
    frame = MainWindow(None, wx.ID_ANY, "")
    
    app.MainLoop()
    




