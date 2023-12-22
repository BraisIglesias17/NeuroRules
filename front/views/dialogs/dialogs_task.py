import sys
import os 
import wx
import threading
import time
import wx.html2
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from front.IO.IOManage import IOManage
from back.respuestas import Status
from back.saver import Saver
from back.validation.validation import Validator
from ...plots import plot_barplot,plot_barplot_object
from ...constants import WILCARD_TASK,WILDCARD_TEXT_FILE
from ..functions import get_task_name
from ..dialogs.dialogs_general import HelpDialog
##
# Dialog for displaying the detail of a task
##
class DetailsDialog(wx.Dialog):
    def __init__(self,parent,task):
        
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Task details")

        self.SetFont(parent.GetFont())
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 10)


        sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Details"), wx.HORIZONTAL)
        sizer_3.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 10)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5.Add(sizer_6, 0, wx.ALL, 10)

        sizer_7b = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7b, 1, wx.ALL | wx.EXPAND, 5)

        label_name = wx.StaticText(self, wx.ID_ANY, "Name: ")
        sizer_7b.Add(label_name, 0, 0, 0)

        task_name = wx.StaticText(self, wx.ID_ANY, task['name'])
        sizer_7b.Add(task_name, 0, 0, 0)

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

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.Center()
        self.Layout()

##
# Dialog to configure the model rule generating task
##
class RuleGeneratinglDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Rule generation model")
        self.SetFont(parent.GetFont())
        #T O DO: LOAD ON CHANGE VARIABLE CURRENT SELECTIONS
        #TO DO: LOAD CONFIGURATION IF EXISTS
        #TO DO: VALIDATIONS (NSETS!=0 TEST SIZE!=0 AND !=1)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.shape=parent.controller.get_data_shape().get_response()['data']
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

        self.classification_params={'criterion':'gini','splitter':'best','max_depth':None}
        self.regression_params={'max_inputs':0,'mf_inputs':2,'mf_outputs':2,'autpo':True,'learning_rate':0.05}
        response=self.controller.get_target_process_type().get_response()

        if response['status']==Status.OK:
            
            self.type_list=response['data']
            for variable in response['data']:
                self.names.append(variable)
                self.display_list.append(variable+" - "+response['data'][variable])
                model="DecisionTree"
                params=self.classification_params
                if response['data'][variable]=="regression":
                    self.regression_vars.append(variable)
                    model="Neurofuzzy"
                    params=self.regression_params
                self.model_selection[variable]={'model':[model],'params':params}
                
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)

        response=self.controller.get_available_models().get_response()
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

        ## regresion notebook

        sizer_rg_1 = wx.BoxSizer(wx.HORIZONTAL)

        sizer_rg_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_rg_1.Add(sizer_rg_2, 1, wx.EXPAND, 0)

        sizer_rg_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_rg_2.Add(sizer_rg_3, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        sizer_rg_4 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_regression, wx.ID_ANY, "Max inputs"), wx.VERTICAL)
        sizer_rg_3.Add(sizer_rg_4, 0, wx.ALL, 20)

        self.spin_max_inputs = wx.SpinCtrl(self.notebook_regression, wx.ID_ANY, "2", min=1, max=3)
        sizer_rg_4.Add(self.spin_max_inputs, 0, wx.ALL, 5)

        sizer_rg_5 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_regression, wx.ID_ANY, "Input membership functions"), wx.VERTICAL)
        sizer_rg_3.Add(sizer_rg_5, 0, wx.ALL, 20)

        self.spin_input_mf = wx.SpinCtrl(self.notebook_regression, wx.ID_ANY, "2", min=2, max=3)
        sizer_rg_5.Add(self.spin_input_mf, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer_rg_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_rg_2.Add(sizer_rg_6, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        sizer_rg_7 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_regression, wx.ID_ANY, "Learning rate"), wx.VERTICAL)
        sizer_rg_6.Add(sizer_rg_7, 0, wx.ALL, 20)

        self.spin_learning_rate = wx.SpinCtrlDouble(self.notebook_regression, wx.ID_ANY, initial=0.05, inc=0.05,min=0.0, max=10.0)
        self.spin_learning_rate.SetDigits(2)
        sizer_rg_7.Add(self.spin_learning_rate, 0, wx.ALL, 5)

        sizer_rg_8 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_regression, wx.ID_ANY, "Output membership functions"), wx.VERTICAL)
        sizer_rg_6.Add(sizer_rg_8, 0, wx.ALL, 20)

        self.spin_output_mf = wx.SpinCtrl(self.notebook_regression, wx.ID_ANY, "2", min=2, max=3)
        sizer_rg_8.Add(self.spin_output_mf, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer_rg_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_rg_2.Add(sizer_rg_9, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.checkbox_automatic = wx.CheckBox(self.notebook_regression, wx.ID_ANY, "Auto")
        sizer_rg_9.Add(self.checkbox_automatic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        ##

        self.notebook_classification = wx.Panel(self.notebook_type, wx.ID_ANY)
        self.notebook_type.AddPage(self.notebook_classification, "Classification")

        ## clasification notebook

        sizer_cls_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_cls_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_cls_1.Add(sizer_cls_2, 1, wx.EXPAND, 0)

        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_classification, wx.ID_ANY, "Criterion"), wx.VERTICAL)
        sizer_cls_2.Add(sizer_6, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        self.cb_criterion = wx.Choice(self.notebook_classification, wx.ID_ANY, choices=["Gini","Entropy","Log loss"])
        self.cb_criterion.SetSelection(0)
        sizer_6.Add(self.cb_criterion, 0, wx.ALL | wx.EXPAND, 5)

        sizer_cls__3 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_classification, wx.ID_ANY, "Splitter"), wx.VERTICAL)
        sizer_cls_2.Add(sizer_cls__3, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        self.cb_splitter = wx.Choice(self.notebook_classification, wx.ID_ANY, choices=["Best","Random"])
        self.cb_splitter.SetSelection(0)
        sizer_cls__3.Add(self.cb_splitter, 0, wx.ALL | wx.EXPAND, 5)

        sizer_cls__4 = wx.StaticBoxSizer(wx.StaticBox(self.notebook_classification, wx.ID_ANY, "Max depth"), wx.VERTICAL)
        sizer_cls_2.Add(sizer_cls__4, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        self.spin_max_depth = wx.SpinCtrl(self.notebook_classification, wx.ID_ANY, "0", min=0, max=100)
        sizer_cls__4.Add(self.spin_max_depth, 0, wx.ALL | wx.EXPAND, 5)

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

        self.notebook_classification.SetSizer(sizer_cls_1)
        self.notebook_regression.SetSizer(sizer_rg_1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnContinue,self.button_OK)
        #self.Bind(wx.EVT_COMBOBOX,self.OnChangeValidation,self.combo_box_validation)
        #self.Bind(wx.EVT_COMBOBOX,self.OnChangeOutput,self.combo_box_targets)
        #self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_classification)
        #self.Bind(wx.EVT_LISTBOX,self.OnSelectModel,self.list_box_models_regression)
        self.Bind(wx.EVT_CHECKBOX,self.OnSelectAuto,self.checkbox_automatic)
        
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Center()
        self.Layout()

    def OnContinue(self,evt):
        
        name,cancel=get_task_name(self)

        if not cancel:
            response=self.controller.create_task(name,self.model_selection,self.validation,True).get_response()
        
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

    def OnSelectAuto(self,event):
        value=self.checkbox_automatic.IsChecked()
        self.spin_output_mf.Enable(not value)
        self.spin_input_mf.Enable(not value)
        self.spin_max_depth.Enable(not value)
        self.spin_learning_rate.Enable(not value)
        self.classification_params['auto']=value
##
# Dialog for predicting, it shows the fields to the input variables and displays the output obtained
##
class PredictDialog(wx.Dialog):
    def __init__(self,parent,variable,model,inputs,submodel=None):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Predictions on "+variable)
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.nominals=parent.string_variable_names
        self.inputs=inputs
        self.n_inputs=len(inputs)    
        self.variable=variable
        self.model=model
        self.submodel=submodel
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

        response=self.controller.get_prediction(self.variable,self.model,values,self.submodel).get_response()

        if response['status']!=Status.OK:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
        elif response['status']==Status.OK:
            
            if Validator.check_parse_float(response['data'][0]):
                value=np.round(response['data'],3)[0]
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
                renderer.SetPrecision(2)
                self.grid_inputs.SetCellRenderer(row,1,renderer)
                
                self.grid_inputs.SetCellValue(row,1,"0.0")

##
# Shows the result of neurofuzzy or neuroclassifier model
##                
class RulesResultsDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Neurofuzzy result")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.setting=parent.setting
        self.outputs=[]
        self.types=[]
        response=self.controller.get_target_process_type().get_response()
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

        self.models=self.controller.get_variable_models().get_response()['data']
        self.submodels={}
        i=0
        for output in self.outputs:
            self.submodels[output]=self.models[output][0].submodels

        outputs=self._custom_outputs()

        self.cb_selections=[]
        metadata=self.controller.get_task_metadata().get_response()['data']
        self.saved=metadata['saved']
        self.path=metadata['path']

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

        self.rules_text_ctrl=wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_WORDWRAP | wx.TE_READONLY)
        self.sizer_7.Add(self.rules_text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        

        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Model Information"), wx.HORIZONTAL)

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

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        asterico= "" if self.saved else "*"
        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "Save"+asterico)
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
        self.SetSize(1000,700)
        self.Center()
        self.Layout()

    def OnPredict(self,evt):
        variable=self.lb_outputs.GetStringSelection().split('  ')[0]
        inputs=self.controller.get_inputs_task().get_response()['data']
        submodel=self.cb_submodel.GetStringSelection().split(' - ')[0]
        inputs=self.submodels[variable][submodel]['inputs']
        model="Neurofuzzy"
        if variable in self.string_variable_names:
            model="DecisionTree"
        dialog=PredictDialog(self,variable,model,inputs,submodel={'submodel':submodel,'inputs':inputs})
        dialog.ShowModal()

    def OnDetails(self,evt):
        dialog=DetailsDialog(self,self.controller.get_task_metadata().get_response()['data'])
        dialog.ShowModal()

    def ClearGrid(self):
        for i in range(self.validation_grid.GetNumberCols()):
            for j in range(self.validation_grid.GetNumberRows()):
                self.validation_grid.SetCellValue(j,i,"")
                self.validation_grid.SetCellBackgroundColour(j,i,self.validation_grid.GetDefaultCellBackgroundColour())
                self.validation_grid.SetRowLabelValue(j,"")

    def OnExportToFile(self,evt):
        index=self.lb_outputs.GetSelection()
        variable=self.lb_outputs.GetString(index).split("  ")[0]
        submodel=self.cb_submodel.GetValue().split(" - ")[0]
        
        response=self.controller.get_text_reports(variable).get_response()
        try:
            content=response['data']['Neurofuzzy']
        except Exception as exc:
            content=response['data']['DecisionTree']

        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,default_folder=self.setting.get_default_path(),default_name=(submodel+"_"+variable)).get_response()

        if path['status']==Status.OK:
            path=path['data']
            response=self.controller.save_file(content,path).get_response()
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
                tmp=tmp+"  ("+str(np.round(r2,1))+")"
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
        try:
            model.plot_r2_evolution()
            
        except Exception:
            
            wx.MessageBox("This plot is not available for neuroclassifier","Warning",wx.ICON_WARNING)

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
        model_type=self.types[evt.GetSelection()]

        model=evt.GetString().split("  ")[0]
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
        
        self.rules_text_ctrl.SetValue(rules_formatted)
    

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
        taskname=self.controller.get_task_name().get_response()
        if taskname['status']==Status.OK:
            taskname=taskname['data']

            if not self.saved:
                pathname=IOManage.GetPath(self,"Select a path",WILCARD_TASK,default_folder=self.setting.get_default_path(),default_name=taskname).get_response()
                
                if pathname['status']==Status.OK:
                    pathname=pathname['data']
                else:
                    cancel=True

            else:
                pathname=self.path

            if not cancel:
                response=self.controller.save_task(pathname).get_response()

                if response['status']==Status.OK:
                    wx.MessageBox("Succesfully saved in "+pathname,"Info")
                    self.button_SAVE.SetLabel("Save")
                    self.saved=True
                    self.path=pathname
                else:
                    wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)

        else:
            wx.MessageBox(taskname['data'],"Error",wx.ICON_ERROR)

##
# Shows the result of cross validation
## 
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
##
# Shows the result of predicting model
## 
class ResultsDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Results dialog")
        self.SetFont(parent.GetFont())
        self.controller=parent.controller
        self.setting=parent.setting
        self.outputs=[]
        response=self.controller.get_target_process_type().get_response()
        
        self.currentMetrics={}
        self.currentModel={}
        self.currentValidation=None
        
        if response['status']==Status.OK:
            self.outputs=list(response['data'].keys())
        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)


        self.models=self.controller.get_variable_models().get_response()['data']

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

        self.validation_grid=wx.grid.Grid(self, wx.ID_ANY)
        self.validation_grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.validation_grid.CreateGrid(4, 2)
        self.validation_grid.SetRowLabelValue(0, "")
        self.validation_grid.SetRowLabelValue(1, "")
        self.validation_grid.SetRowLabelValue(2, "")
        self.validation_grid.SetRowLabelValue(3, "")
        self.validation_grid.SetColLabelValue(0, "Testing")
        self.validation_grid.SetColLabelValue(1, "Training")

        sizer_7.Add(self.validation_grid, 0, wx.ALL, 10)
        
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

        self.button_DETAILS = wx.Button(self, wx.ID_APPLY, "Details")
        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_SAVE = wx.Button(self, wx.ID_SAVE, "Save*")
        self.button_SAVE.SetDefault()
        sizer_2.AddButton(self.button_SAVE)

        sizer_2.AddButton(self.button_DETAILS)

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
        self.Bind(wx.EVT_BUTTON,self.OnDetailsTask,self.button_DETAILS)
        sizer_2.Realize()   

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        #self.SetSize(600,500)
        self.Center()
        self.Layout()

    
    def OnDetailsTask(self,evt):
        dialog=DetailsDialog(self,self.controller.get_task_metadata().get_response()['data'])
        dialog.ShowModal()
    
    def OnPlotPrecision(self,evt):
        model=self.cb_model.GetStringSelection()
        output=self.lb_outputs.GetStringSelection()

        response=self.controller.get_model_plot(output,model).get_response()

        if response['status']==Status.OK:
            figure=response['data']
            figure.show()
        else:
            wx.MessageBox(response['data'],"Error",wx.ICON_ERROR)
        

    def OnExportToFile(self,evt):
        index=self.lb_outputs.GetSelection()
        variable=self.lb_outputs.GetString(index)
        model=self.cb_model.GetValue()
        response=self.controller.get_text_reports(variable).get_response()

        content=response['data'][model]
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,default_folder=self.setting.get_default_path(),default_name=(model+"_"+variable)).get_response()

        if path['status']==Status.OK:
            #save officialy
            path=path['data']
            response=self.controller.save_file(content,path).get_response()
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
                inputs=self.controller.get_inputs_task().get_response()['data']
                dialog=PredictDialog(self.Parent,variable,model,inputs)
                code=dialog.ShowModal()

    def OnSaveTask(self,evt):
        
        cancel=False
        taskname=self.controller.get_task_name().get_response()
        if taskname['status']==Status.OK:
            taskname=taskname['data']

            if not self.saved:
                pathname=IOManage.GetPath(self,"Select a path",WILCARD_TASK,default_folder=self.setting.get_default_path(),default_name=taskname).get_response()
                
                if pathname['status']==Status.OK:
                    pathname=pathname['data']
                else:
                    cancel=True

            else:
                pathname=self.path

            if not cancel:
                response=self.controller.save_task(pathname).get_response()

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
        
        response=self.controller.get_output_info(output).get_response()
        
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

##
# Display options for predicting model
##
class PredictionModelDialog(wx.Dialog):
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Prediction model")
        self.SetFont(parent.GetFont())
        #TO DO: LOAD ON CHANGE VARIABLE CURRENT SELECTIONS
        #TO DO: LOAD CONFIGURATION IF EXISTS
        #TO DO: VALIDATIONS (NSETS!=0 TEST SIZE!=0 AND !=1)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.shape=parent.controller.get_data_shape().get_response()['data']
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

        response=self.controller.get_target_process_type().get_response()

        if response['status']==Status.OK:
            
            self.type_list=response['data']
            for variable in response['data']:
                self.names.append(variable)
                self.display_list.append(variable+" - "+response['data'][variable])
                if response['data'][variable]=="regression":
                    self.regression_vars.append(variable)
                self.model_selection[variable]={'model':'','params':None}
                
        else:
            wx.MessageBox("An error has occurred: "+response['data'],"Error",wx.OK|wx.ICON_ERROR)

        response=self.controller.get_available_models().get_response()
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

        self.list_box_models_regression = wx.ListBox(self.notebook_regression, wx.ID_ANY, choices=self.regression_models, style=wx.LB_MULTIPLE)
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

        self.list_box_models_classification = wx.ListBox(self.notebook_classification, wx.ID_ANY, choices=self.classification_models,style=wx.LB_MULTIPLE)
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
        
        self.shape=self.controller.get_data_shape().get_response()['data']

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
        

    def _clear_selections(self,listbox):
        for element in listbox.GetSelections():
            listbox.Deselect(element)

    def OnChangeOutput(self,evt):
        #self.list_box_models_classification.Deselect(self.list_box_models_classification.GetSelections())
        #self.list_box_models_regression.Deselect(self.list_box_models_regression.GetSelections())
        self._clear_selections(self.list_box_models_classification)
        self._clear_selections(self.list_box_models_regression)

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
                model=self.list_box_models_regression.GetSelections()
                grid=self.checkbox_1.GetValue()
            else:
                model=self.list_box_models_classification.GetSelections()
                grid=self.checkbox_auto_grid_class.GetValue()

            models=[self.list_box_models_regression.GetStrings()[i] for i in model]
            self.model_selection[variable]['model']=models
            self.model_selection[variable]['params']=grid
        else:
            if self.notebook_regression.IsShown():
                model=self.list_box_models_regression.GetSelections()
                for variable in self.model_selection:
                    if variable in self.regression_vars:
                        models=[self.list_box_models_regression.GetStrings()[i] for i in model]
                        self.model_selection[variable]['model']=models
                        self.model_selection[variable]['params']=self.checkbox_1.GetValue()

            elif self.notebook_classification.IsShown():
                model=self.list_box_models_classification.GetSelections()
                for variable in self.model_selection:
                    if not variable in self.regression_vars:
                        models=[self.list_box_models_classification.GetStrings()[i] for i in model]
                        self.model_selection[variable]['model']=models
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
                response=self.controller.create_task(name,self.model_selection,self.validation,False).get_response()

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

##
# Shows the report of the task
##
class TaskReportDialog(wx.Dialog):
    def __init__(self,parent):

        wx.Dialog.__init__(self,parent)
        self.SetTitle("Task report")
        self.SetFont(parent.GetFont())
        self.parent=parent
        self.task_report=""
        self.controller=parent.controller
        self.task_report=self.controller.get_task_info().get_response()['data']

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

    def _activate_training(self,value):
        self.button_train.Enable(value)
        self.button_train_background.Enable(value)
        self.button_CANCEL.Enable(value)
        self.button_SAVE.Enable(value)

    def OnSave(self,evt):
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,default_folder=self.parent.setting.get_default_path()).get_response()

        if path['status']==Status.OK:
            
            saver=Saver(path['data'],content=self.label_report.GetLabelText())
            saver.save()
            wx.MessageBox("File saved succesfully in "+path['data'],"Info")

    def OnApply(self,event):
        targets=self.controller.get_target_indexes().get_response()['data']
        maximum=len(targets)*100
        print(maximum)
        self.progressBar = wx.ProgressDialog("Training in progress ... ", "Please, wait...",maximum=maximum,parent=self,style=wx.PD_APP_MODAL|wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
        #self.progressbar.Update(10,"Training in progress...")
        #self.execute_thread()
        thread = threading.Thread(target=self.execute_thread)
        thread.start()
    
    def OnApplyBg(self,evt):
        from plyer import notification
        pathname=IOManage.GetPath(self,"Select a path for the task",WILCARD_TASK,default_folder=self.parent.setting.get_default_path()).get_response()

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
        response=self.controller.execute_task(None).get_response()
        if response['status']==Status.OK:
            self.controller.save_task(pathname)

    def execute_thread(self):
        self._activate_training(False)
        response=self.controller.execute_task(self.update_progress).get_response()
     
        #wx.CallAfter(self.progressbar.Update,self.progressbar.GetRange())
        self.progressBar.Update(self.progressBar.GetRange())
        wx.CallAfter(self._callAfter,response)
        
    def _callAfter(self,response):
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


##
# General purpose info displayer
##
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