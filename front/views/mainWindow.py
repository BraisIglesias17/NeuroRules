import wx
import wx.grid as gridlib
from front.settings.settings import Settings 
from front.IO.IOManage import IOManage
from back.controller.controller import Controller
from back.respuestas import Status
from front.views.dialogs import LoadFileDialog,HelpDialog,CreateSetDialog,SettingsDialog,RulesResultsDialog,RulePredictinglDialog,ResultsDialog,PredictionModelDialog,PickDialog,PreprocessDialog,RulesDialog,TransformDialog,CleanDataDialog,GraphDialog,SummaryDialog,AboutUsDialog,ShowHiddenDialog,SummaryPickDialog,StatisticDialog,CreateTaskDialog,ShowIdentifierColsDialog
from back.validation.validation import Validator
import numpy as np
import sys
from front.constants import WILCARD_TASK,WILDCARD_DATA_FILE
import wx.adv



class MainWindow(wx.Frame):    
    def __init__(self,*args, **kwds):
        super().__init__(parent=None, title='Ruler')
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.ROW_BOUND=500
        self.COL_BOUND=30

        self.setting=Settings()
        self.SetFont(self.setting.font)

        self.SetIcon(wx.Icon('./front/resources/img/logo_50x50.png',type=wx.BITMAP_TYPE_PNG))
        self.SetTitle("NeuroRule 1.0.0")
        self.createMenuBar()
        self.panel = wx.Panel(self, wx.ID_ANY)
                
        self.IO=IOManage()
        self.controller=Controller()
        self.init=False
        self.highlighted_cells=[]  
        self.highlighted_cols=[]
        self.initial_col_names=[]
        self.highlighted_outliers_cells=[]
        self.start=True
        self.names=[]
        self.new_set={}

        self.float_variable_names=[]
        self.int_variable_names=[]
        self.string_variable_names=[]

        self.hidden_columns=[]
        self.names_to_show=[]
        self.filename=""

        self.identifier_cols=[]

        self.override_warning=True

        ##interface
        self.showPrediction=True
        self.showAnalysis=True
        self.showData=True
        self.showTask=True

        sizer_1 = wx.BoxSizer(wx.VERTICAL)  
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 0, wx.ALL | wx.EXPAND, 15)

        self.sizer_data = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Data"), wx.HORIZONTAL)
        sizer_3.Add(self.sizer_data, 0, wx.ALL, 10)

        self.import_file_button = wx.Button(self.panel, wx.ID_ANY, "Import data\n")
        self.sizer_data.Add(self.import_file_button, 0, wx.ALL | wx.EXPAND, 5)

        #self.create_set_button = wx.Button(self.panel, wx.ID_ANY, "Create set")
        #sizer_4.Add(self.create_set_button, 1, wx.ALL | wx.EXPAND, 5)

        self.clear_set_button = wx.Button(self.panel, wx.ID_ANY, "Clear")
        self.sizer_data.Add(self.clear_set_button, 1, wx.ALL | wx.EXPAND, 5)
        
        self.sizer_preprocess = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Preprocess"), wx.HORIZONTAL)
        sizer_3.Add(self.sizer_preprocess, 0, wx.ALL, 10)

        self.clean_data_button = wx.Button(self.panel, wx.ID_ANY, "Clean data\n")
        self.sizer_preprocess.Add(self.clean_data_button, 1, wx.ALL | wx.EXPAND, 5)

        self.transform_data_button = wx.Button(self.panel, wx.ID_ANY, "Transform data\n")
        self.sizer_preprocess.Add(self.transform_data_button, 1, wx.ALL | wx.EXPAND, 5)

        #self.preprocess_data_button = wx.Button(self.panel, wx.ID_ANY, "Preprocess data\n")
        #self.sizer_preprocess.Add(self.preprocess_data_button, 1, wx.ALL | wx.EXPAND, 5)

        #self.preprocess_data_button.Hide()

        self.sizer_analysis = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Analysis"), wx.HORIZONTAL)
        sizer_3.Add(self.sizer_analysis, 0, wx.ALL, 10)

        self.plot_data_button = wx.Button(self.panel, wx.ID_ANY, "Plot\n")
        self.sizer_analysis.Add(self.plot_data_button, 1, wx.ALL, 5)

        self.statistics_button = wx.Button(self.panel, wx.ID_ANY, "Statistics\n")
        self.sizer_analysis.Add(self.statistics_button, 1, wx.ALL, 5)

        self.summary_button = wx.Button(self.panel, wx.ID_ANY, "Summary\n")
        self.sizer_analysis.Add(self.summary_button, 1, wx.ALL, 5)

        
        self.sizer_task = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Task"), wx.HORIZONTAL)
        sizer_3.Add(self.sizer_task, 0, wx.ALL, 10)

        #self.next_button = wx.Button(self.panel, wx.ID_ANY, "Select variables\n")
        #sizer_7.Add(self.next_button, 1, wx.ALL, 5)

        self.prediction_button = wx.Button(self.panel, wx.ID_ANY, "Prediction Model\n")
        self.sizer_task.Add(self.prediction_button, 1, wx.ALL, 5)

        self.neurofuzzy_button = wx.Button(self.panel, wx.ID_ANY, "Neurofuzzy Model\n")
        self.sizer_task.Add(self.neurofuzzy_button, 1, wx.ALL, 5)

        self.results_button = wx.Button(self.panel, wx.ID_ANY, "Results \n")
        self.sizer_task.Add(self.results_button, 0, wx.ALL, 5)
        #self.train_button.Enable(False)
        
        self.grid_sizer = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Data Sheet"), wx.VERTICAL)
       
        
        sizer_1.Add(self.grid_sizer, 1, wx.ALL| wx.EXPAND, 5)
        self.grid = wx.grid.Grid(self.panel, wx.ID_ANY)
        self.grid.CreateGrid(self.ROW_BOUND,25)
        self.grid_sizer.Add(self.grid, 1, wx.EXPAND, 0)
        
        self.status_bar=self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-1,300,300])
        self.status_bar.SetStatusText("  Empty sheet")
        self.status_bar.SetStatusText("  None task",1)
        self.status_bar.SetStatusText("None data",2)

        #Declaracion de eventos
        
        self.Bind(wx.EVT_BUTTON,self.OnOpenFile,self.import_file_button)
        self.Bind(wx.EVT_BUTTON,self.OnClearGrid,self.clear_set_button)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,self.OnCellEdit)
        #self.Bind(wx.EVT_BUTTON,self.OnNext,self.next_button)
        self.Bind(wx.EVT_BUTTON,self.OnNeurofuzzyModel,self.neurofuzzy_button)
        self.Bind(wx.EVT_BUTTON,self.OnPredictionModel,self.prediction_button)
        self.Bind(wx.EVT_BUTTON,self.OnShowResults,self.results_button)
        #self.Bind(wx.EVT_BUTTON, self.OnTrain,self.train_button)
        #self.Bind(wx.EVT_BUTTON,self.OnPreprocess,self.preprocess_data_button)
        self.Bind(wx.EVT_BUTTON,self.OnCleanData,self.clean_data_button)
        self.Bind(wx.EVT_BUTTON,self.OnTransformData,self.transform_data_button)
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

    def OnShowResults(self,evt):
        
        task=self.controller.task_state().getResponse()
        if task['status']==Status.EXISTING_TASK or task['status']==Status.EXISTING_TASK_NO_EXECUTED or task['status']==Status.EXISTING_TASK_UNSAVED:
            rules=task['data']['rules']
           
            if not rules:
                dialog=ResultsDialog(self)
                code=dialog.ShowModal()
            else:
                dialog=RulesResultsDialog(self)
                code=dialog.ShowModal()
        elif task['status']==Status.OK:
            wx.MessageBox("There is no task loaded","Info")
        else:
            wx.MessageBox(task['data'],"Error",wx.ICON_ERROR)

    def OnPredictionModel(self,evt):
        
        #dialog=PickDialog(self)#VariableTypeDialog(self)
        #code=dialog.ShowModal()    
    
        code=self.OnManageCurrentTask()

        if code == wx.ID_APPLY:
            #self.train_button.Enable(True)
            self.updateColors()

            dialog_prediction=PredictionModelDialog(self)
            code=dialog_prediction.ShowModal()

            if code==wx.ID_OK:
                #show resusts
                dialog=ResultsDialog(self)
                code=dialog.ShowModal() 
    
    def OnManageCurrentTask(self):
        response=self.controller.task_state().getResponse()
        status=response['status']
        

        if status==Status.UNEXISTING_TASK or status==Status.EXISTING_TASK:
            dialog=PickDialog(self)
            code=dialog.ShowModal()
            return code
        
        elif status==Status.EXISTING_TASK_NO_EXECUTED:
            code=wx.MessageBox("Do you want to change the inputs or outputs?","Info",wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            
            if code!=wx.CANCEL:
                if code == wx.YES:
                    dialog=PickDialog(self)
                    code=dialog.ShowModal()
                    return code
                else:
                    return wx.ID_APPLY
            else:
                return code
            
        elif status==Status.EXISTING_TASK_UNSAVED:
            code=wx.MessageBox("Do you want to save the current task before continue?","Info",wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            
            if code!=wx.CANCEL:
                if code == wx.YES:
                    self.saveTask()
                
                dialog=PickDialog(self)
                code=dialog.ShowModal()
                return code
            
            return code

    def saveTask(self):
        cancel=False
        taskname=self.controller.get_task_name().getResponse()
        if taskname['status']==Status.OK:
            taskname=taskname['data']
            
            pathname=IOManage.GetPath(self,"Select a path",WILCARD_TASK,defaultDir=self.setting.GetPath(),defaultname=taskname).getResponse()
            
            if pathname['status']==Status.OK:
                pathname=pathname['data']
            else:
                cancel=True
        if not cancel:
            response=self.controller.save_task(pathname).getResponse()
            
            if response['status']==Status.OK:
                wx.MessageBox("Succesfully saved in "+pathname,"Info")
            else:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
            
    def OnNeurofuzzyModel(self,evt):
        
          
        code=self.OnManageCurrentTask()

        if code == wx.ID_APPLY:
            
            self.updateColors()

            dialog_prediction=RulePredictinglDialog(self)
            code=dialog_prediction.ShowModal()

            if code==wx.ID_OK:
                dialog=RulesResultsDialog(self)
                code=dialog.ShowModal()


    
    def OnTransformData(self,evt):
        dialog=TransformDialog(self)
        code=dialog.ShowModal()
        
        if code==wx.OK:
            
            df=self.controller.get_data().getResponse()
            if df['status']==Status.OK:
                self.ClearGrid()
                self.updateGrid(df['data'])
            else:
                wx.MessageBox("An error has ocurred:"+df['data'],"Error",wx.OK|wx.ICON_ERROR)
            
    

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
            
            outliers=self.controller.get_outliers().getResponse()
            
            if response['status']==Status.OK:
                self.ClearGrid()
                
                self.updateGrid(response['data'])
                

                if outliers['status']==Status.OK:
                    self.HighlightOutliers(outliers['data'])
            else:
                wx.MessageBox("A problem has occurred","Error",wx.OK|wx.ICON_ERROR)



    def HighlightOutliers(self,outliers):
        
        for cell in self.highlighted_outliers_cells:
            self.grid.SetCellBackgroundColour(cell[0],cell[1], self.setting.defaultColor)

        
        for var in outliers:    
            
            positions=outliers[var]['outliers']
            col=outliers[var]['index']

            for i in range(len(positions)):
                self.grid.SetCellBackgroundColour(positions[i],col, self.setting.outlierColor)
                self.highlighted_outliers_cells.append((positions[i],col))

        

    def OnExit(self,event):
        sys.exit(0)
        
    def OnPreprocess(self,event):
        dialog=PreprocessDialog(self)
        code=dialog.ShowModal()
       
            
    def OnTrain(self,event):
        
        #Validar datos
        dialog=CreateTaskDialog(self)
        dialog.Show()
        

    def updateColors(self):
        
        independent=self.controller.get_independent_indexes().getResponse()['data']
        targets=self.controller.get_target_indexes().getResponse()['data']

       
        rows,cols=self.controller.get_data_shape().getResponse()['data']

        if rows<100:
            for row in range(rows):
                for col in range(cols):
                    if col in targets:
                        self.grid.SetCellBackgroundColour(row, col, self.setting.targetColor)
                        self.highlighted_cols.append([row,col])
                    elif col in independent:
                        self.grid.SetCellBackgroundColour(row, col, self.setting.independentColor)
                        self.highlighted_cols.append([row,col])
                    else:
                        self.grid.SetCellBackgroundColour(row, col, self.setting.defaultColor)
        
       
    def enableButtons(self,val):
        self.clean_data_button.Enable(val)
        self.clear_set_button.Enable(val)
        self.statistics_button.Enable(val)
        self.summary_button.Enable(val)
        self.plot_data_button.Enable(val)
        #self.preprocess_data_button.Enable(val)
        self.neurofuzzy_button.Enable(val)
        self.prediction_button.Enable(val)
        self.results_button.Enable(val)
        #self.next_button.Enable(val)
        self.transform_data_button.Enable(val)

    def OnOpenFile(self,event):
        try:
            response=IOManage.LoadFile(self,event).getResponse()
            if response['status']==Status.OK:
                pathname=response['data']
                conf={'sep':',','dec':'.','pathname':pathname}
                dialog=LoadFileDialog(self,conf)
                code=dialog.ShowModal()

                if code==wx.ID_OK:
                    self._OnClearGrid()
                    df,filename=IOManage.load_file(conf)
                                     
                    response=self.controller.load_content(df,filename).getResponse()
                    if response['status']==Status.OK:
                        
                        
                        dlg=None
                        if df.shape[0]>50:
                            
                            dlg = wx.ProgressDialog("Escribiendo en el Grid", "Progreso", maximum=df.shape[1], parent=self, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
                        
                            self.updateGrid(response['data']['data'],dlg.Update)
                            dlg.Update(df.shape[1],"Finished")
                            dlg.Destroy()
                            self.grid.Raise()
                            
                        else:
                            self.updateGrid(response['data']['data'])

                        self.filename=response['data']['file']
                        
                        self.SetStatusText(str(" Working on "+self.filename))
        except Exception as exc:
            wx.MessageBox("You probably have selected a wrong loading file configuration. Be careful with separator and decimal characters. Try again.","Error",wx.ICON_ERROR)
            print(exc)
            self.OnOpenFile(event)
            """
            
            file=response['data']['df']
            name=response['data']['filename']
            response=self.controller.load_content(file,name).getResponse()
            if response['status']==Status.OK:
                
                self.ClearGrid()
                self.updateGrid(response['data']['data'])
                self.filename=response['data']['file']
                
                self.SetStatusText(str(" Working on "+self.filename))
            """

           
 
    def OnCellEdit(self,event):
        row,col=event.GetRow(),event.GetCol()
    

        response=self.controller.update_data_position(row,col,self.grid.GetCellValue(row,col)).getResponse()

        if not response['status'] == Status.OK:
            self.grid.SetCellValue(row,col,str(self.controller.get_position(row,col).getResponse()['data']))
            wx.MessageBox(response['data'],"Error",wx.OK|wx.ICON_ERROR)
        else:
            self.grid.SetCellBackgroundColour(row, col, wx.Colour('#FFFFFF'))
            

    def OnClearGrid(self,event):
        
        code=wx.MessageBox("Are you sure you want to clear the grid ? ","Warning",wx.OK|wx.CANCEL|wx.CANCEL_DEFAULT|wx.ICON_WARNING)
    
        if code==wx.OK:
            self._OnClearGrid()
    
    def _OnClearGrid(self):
        self.ClearGrid()
        self.controller.clear_data()

        for coords in self.highlighted_outliers_cells:
            self.grid.SetCellBackgroundColour(coords[0], coords[1], wx.WHITE)

        self.hidden_columns=[]
        self.identifier_cols=[]

        self.enableButtons(False)
        self.restoreStatus()
        self.override_warning=True

    def ClearDataStructures(self):
        self.int_variable_names=[]
        self.float_variable_names=[]
        self.string_variable_names=[]


    def ClearGrid(self):
        self.ClearDataStructures()
        
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
        self.SetStatusText(message,2)
        task=self.controller.get_task_name().getResponse()
        if task['status']==Status.OK:
            self.SetStatusText("Task: "+task['data'],1)
    
    def updateStatusTask(self,taskname):
        self.SetStatusText("Task: "+taskname,1)


    def restoreStatus(self):
        self.SetStatusText(" None existing file")
        self.SetStatusText("None task",1)
        self.SetStatusText("None data",2)


    def updateGrid(self,df,updater=None):
        
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
                    align=True
                    
                    if value=="" or value=="nan":
                        self.grid.SetCellBackgroundColour(j, i, self.setting.NanColor)
                        self.highlighted_cells.append([i,j])
                    
                    elif Validator.check_float(df.loc[j][i]) and not Validator.check_integer(df.loc[j][i]):
                        align=False
                        value=str(np.round(df.loc[j][i],3))
                    elif Validator.check_integer(df.loc[j][i]):
                        align=False

                    if align:
                        self.grid.SetCellAlignment(j,i,wx.ALIGN_CENTER,wx.ALIGN_CENTER)
                    else:
                        self.grid.SetCellAlignment(j,i,wx.ALIGN_RIGHT,wx.ALIGN_RIGHT)

                    self.grid.SetCellValue(j,i,value)

            if updater!=None:
                updater(i,f"Loading data")
                   
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
                    setIDColumn=menu.Append(wx.ID_ANY,"Set/Unset as an identifier column")

                    self.Bind(wx.EVT_MENU,lambda event: self.OnChangeName(event,col),changeName)
                    self.Bind(wx.EVT_MENU,lambda event: self.OnDeleteColumn(event,col),deleteColumn)
                    self.Bind(wx.EVT_MENU,lambda event: self.OnHideColumn(event,col),hideColumn)
                    self.Bind(wx.EVT_MENU,lambda event: self.OnSetAsIS(event,col),setIDColumn)
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


    def OnSetAsIS(self,event,col):
    
        names=[self.names[col]]
        cols=self.grid.GetSelectedCols()
        for col in cols:
            name=self.names[col]
            if not name in names:
                names.append(name)

        action=""
        message=""
        for name in names:
            if name in self.identifier_cols:
                self.controller.set_col_as_id(name,remove=True)
                self.identifier_cols.remove(name)
                action="unset"
                
            else:
                self.controller.set_col_as_id(name,remove=False)
                self.identifier_cols.append(name)
                action="set"
            
            message=message+str(name)+" is now "+action+" as identifier\n"
        
        wx.MessageBox(message,"Info")
    
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

                new_highlighted=[]
                for cell in self.highlighted_outliers_cells:
                    self.grid.SetCellBackgroundColour(cell[0],cell[1],self.setting.defaultColor)
                    shift=0
                    itself=False
                    for col in cols:
                        if col < cell[1]:
                            shift+=1
                        elif col==cell[1]:
                            itself=True

                    shape=self.controller.get_data_shape().getResponse()['data']

                    if not itself or shape[1]==1:
                        self.grid.SetCellBackgroundColour(cell[0],cell[1]-shift,self.setting.outlierColor)
                        new_highlighted.append((cell[0],cell[1]-shift))
                self.highlighted_outliers_cells=new_highlighted

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
                    #Si hay alguna resaltada, elimino el color
                
                new_highlighted=[]
                for cell in self.highlighted_outliers_cells:
                    self.grid.SetCellBackgroundColour(cell[0],cell[1],self.setting.defaultColor)
                    shift=0
                    itself=False
                    for col in rows:
                        if col < cell[0]:
                            shift+=1
                        elif col==cell[0]:
                            itself=True

                    shape=self.controller.get_data_shape().getResponse()['data']

                    if not itself or shape[0]==1:
                        self.grid.SetCellBackgroundColour(cell[0]-shift,cell[1],self.setting.outlierColor)
                        new_highlighted.append((cell[0]-shift,cell[1]))
                self.highlighted_outliers_cells=new_highlighted
                    
                
                

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
        
    def OnShowIdentifierCols(self,event):
        if len(self.identifier_cols)==0:
            wx.MessageBox("There is no columns set as identifier")
        else:
        
            dialog=ShowIdentifierColsDialog(self)
            code=dialog.ShowModal()
            #if code==wx.OK:
                
    def OnAboutUs(self,event):
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName("NeuroRule ")
        aboutInfo.SetVersion("1.0")
        aboutInfo.SetIcon(wx.Icon("./front/resources/img/logo_128x128.png"))
        aboutInfo.SetDescription("Data mining program")
        aboutInfo.SetCopyright("(C) Brais Iglesias-2023")
        #aboutInfo.SetLicense("https://www.gnu.org/licenses/gpl-2.0.html")
        aboutInfo.AddDeveloper("Brais Iglesias Otero")
        #aboutInfo.AddDocWriter("Brais Iglesias Otero")
        #aboutInfo.SetWebSite('https://es.linkedin.com/in/brais-iglesias-otero-475897214')
        wx.adv.AboutBox(aboutInfo)
        #dialog=AboutUsDialog(self)
        #dialog.ShowModal()


    def OnImportTask(self,event):
        pathname=IOManage.GetPathImport(self,message="Select a task file",wildcard=WILCARD_TASK).getResponse()
        
        if pathname['status']==Status.OK:
            pathname=pathname['data']
            response=self.controller.import_task(pathname).getResponse()
        
            if response['status']!=Status.OK:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
            else:
                self.restore()

    def restore(self):
        response=self.controller.get_data().getResponse()
        if response['status']==Status.OK:
            df=response['data']
            self.updateGrid(df)
            self.updateColors()

    def OnFileSaveAsMenu(self,evt):
        
        path=self.filename
        arr=self.filename.split("\\")
        name=arr[len(arr)-1]
        response=self.IO.OnSaveAs(self,message="Save summary",wildcard="(*.csv)|*.csv|(*.xlsx)|*.xlsx",dir=path,file=name).getResponse()

        if response['status']==Status.OK:
            pathname=response['data']
            response=self.controller.save_data(pathname).getResponse()
            if response['status']==Status.OK:
                wx.MessageBox("Filed saved on "+pathname,"Info")

    def OnFileSaveMenu(self,evt):
        code=wx.YES
        if self.override_warning and self.filename!="":
            code=wx.MessageBox("Are you sure you want to override "+self.filename,"Info",wx.YES|wx.NO|wx.NO_DEFAULT|wx.ICON_WARNING)
            self.override_warning=False
        
        if code==wx.YES:
            
            self.controller.save_data(self.filename)

    def OnShowHideOptions(self,evt):
        self.sizer_task.ShowItems(not self.showPredictionOptions.IsChecked())
        self.sizer_analysis.ShowItems(not self.showAnalysisOptions.IsChecked())
        self.sizer_data.ShowItems(not self.showDataOptions.IsChecked())
        self.sizer_preprocess.ShowItems(not self.showPreprocessOptions.IsChecked())
        
    def OnShowGeneralSettings(self,evt):
        dialog=SettingsDialog(self)
        code=dialog.ShowModal()
        
        if code==wx.ID_REFRESH:
            self.Refresh()

    def OnSaveTask(self,evt):
        response=self.controller.task_state().getResponse()

        if response['status']!=Status.UNEXISTING_TASK:
            
            path=IOManage.GetPath(self,"Path to save",WILCARD_TASK,defaultDir=self.setting.GetPath(),defaultname=response['data']['name']).getResponse()
            
            if path['status']==Status.OK:

                path=path['data']
                response=self.controller.save_task(path).getResponse()

                if response['status']==Status.OK:
                    wx.MessageBox("Succesfully saved in"+path)
                else:
                    wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)

        else:
            wx.MessageBox(response['data'],"Info")


    def OnCreateSet(self,evt):
        data={}
        dialog=CreateSetDialog(self,data)
        code=dialog.ShowModal()

        if code==wx.ID_APPLY:
            
            response=self.controller.create_empty_set(self.new_set).getResponse()
            
            if response['status']!=Status.OK:
                wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
            else:
                self.ClearGrid()
                
                self.updateGrid(response['data'])
                self.enableButtons(True)

    def OnHelpTask(self,evt):
        
        dialog=HelpDialog(self,file="./front/resources/help/task_help.json",title="Task help")
        dialog.ShowModal()
    
    def OnHelpData(self,evt):
        
        dialog=HelpDialog(self,file="./front/resources/help/data_help.json",title="Data help")
        dialog.ShowModal()

    def createMenuBar(self):
        menubar = wx.MenuBar()  
        menubar.SetFont(self.setting.font)

        fileMenu = wx.Menu()  
        importFileMenu=fileMenu.Append(wx.ID_NEW, '&Import file') 

        fileSaveMenu=wx.MenuItem(fileMenu,wx.ID_ANY,'&Save\tCtrl+S')
        #image = wx.Image('./front/resources/img/guardar.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        #wx.Bitmap.Rescale(image,wx.Size(16,16))
        #fileSaveMenu.SetBitmap(image)

        fileMenu.Append(fileSaveMenu)
        fileAsSaveMenu=fileMenu.Append(wx.ID_ANY,'&Save as\tCtrl+A',"Save current file")

        modelMenu= wx.Menu()
        modelMenu.Append(wx.ID_ANY, '&Options')

        settingsMenu= wx.Menu()
        generalSettings=settingsMenu.Append(wx.ID_ANY, '&General Settings')

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
        item=wx.MenuItem(dataMenu,wx.ID_ANY,'&Show identifier columns')
        showIdentifier=dataMenu.Append(item)
        createSetOption=dataMenu.Append(wx.ID_ANY,"&Create set")
        clearDataOptiondata=dataMenu.Append(wx.ID_ANY,"&Clear data")
        helpDataOption=dataMenu.Append(wx.ID_ANY,"&Help")
        #dataMenu.AppendSubMenu(preprocessSubmenu,"Data processing")
        #dataMenu.AppendSubMenu(analyzeSubmenu,"Data analysis")

        viewMenu=wx.Menu()
        item=wx.MenuItem(viewMenu,wx.ID_ANY,'&Show hidden columns')
        
        viewOptionsMenu=wx.Menu()
        self.showPredictionOptions=viewOptionsMenu.AppendCheckItem(wx.ID_ANY,'&Hide prediction options',help="")
        self.showAnalysisOptions=viewOptionsMenu.AppendCheckItem(wx.ID_ANY,'&Hide analysis options')
        self.showDataOptions=viewOptionsMenu.AppendCheckItem(wx.ID_ANY,'&Hide data options')
        self.showPreprocessOptions=viewOptionsMenu.AppendCheckItem(wx.ID_ANY,'&Hide preprocess options')

        showHidden=viewMenu.Append(item)
        viewMenu.AppendSubMenu(viewOptionsMenu,"Display options")        

        helpMenu = wx.Menu()  
        aboutUsOption=helpMenu.Append(wx.ID_ABOUT, '&About us')
        

        taskMenu = wx.Menu()  
        importTaskOption=taskMenu.Append(wx.ID_ANY, '&Import task\tCtrl+D')
        saveTaskOption=taskMenu.Append(wx.ID_ANY, '&Save as')
        helpTaskOption=taskMenu.Append(wx.ID_ANY, '&Help')


        #Key events
        entries = [wx.AcceleratorEntry() for i in range(3)]

        entries[0].Set(wx.ACCEL_CTRL, ord('D'), importTaskOption.GetId())
        entries[1].Set(wx.ACCEL_CTRL, ord('A'), fileAsSaveMenu.GetId())
        entries[2].Set(wx.ACCEL_CTRL, ord('S'), fileSaveMenu.GetId())

        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        menubar.Append(fileMenu, '&File') 
        menubar.Append(dataMenu,"&Data")
        #menubar.Append(modelMenu,'&Model')
        menubar.Append(taskMenu,'&Task')
        menubar.Append(viewMenu,'&View')  
        menubar.Append(settingsMenu,'&Settings') 
        menubar.Append(helpMenu, '&Help')

        self.Bind(wx.EVT_MENU,self.OnShowHidden,showHidden)
        self.Bind(wx.EVT_MENU,self.OnAboutUs,aboutUsOption)
        self.Bind(wx.EVT_MENU,self.OnShowIdentifierCols,showIdentifier)
        self.Bind(wx.EVT_MENU,self.OnImportTask,importTaskOption)
        self.Bind(wx.EVT_MENU,self.OnFileSaveAsMenu,fileAsSaveMenu)
        self.Bind(wx.EVT_MENU,self.OnFileSaveMenu,fileSaveMenu)
        self.Bind(wx.EVT_MENU,self.OnOpenFile,importFileMenu)
        self.Bind(wx.EVT_MENU,self.OnShowHideOptions,self.showPredictionOptions)
        self.Bind(wx.EVT_MENU,self.OnShowHideOptions,self.showAnalysisOptions)
        self.Bind(wx.EVT_MENU,self.OnShowHideOptions,self.showDataOptions)
        self.Bind(wx.EVT_MENU,self.OnShowHideOptions,self.showPreprocessOptions)
        self.Bind(wx.EVT_MENU,self.OnShowGeneralSettings,generalSettings)
        self.Bind(wx.EVT_MENU,self.OnClearGrid,clearDataOptiondata)
        self.Bind(wx.EVT_MENU,self.OnSaveTask,saveTaskOption)
        self.Bind(wx.EVT_MENU,self.OnCreateSet,createSetOption)
        self.Bind(wx.EVT_MENU,self.OnHelpTask,helpTaskOption)
        self.Bind(wx.EVT_MENU,self.OnHelpData,helpDataOption)
       
        self.SetMenuBar(menubar)  
