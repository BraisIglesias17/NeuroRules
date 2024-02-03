import wx
import wx.html2
from front.IO.IOManage import IOManage
from back.respuestas import Status
from back.saver import Saver
from back.tracer import Trace
import copy
from ...constants import WILDCARD_TEXT_FILE,WILDCARD_DATA_FILE
from ..functions import validate_name
import wx.html2 as wxhtml2
import json
 
##
# Dialog for display information of the organization
##
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

##
# Dialog for manage the hidden columns
##  
class ShowHiddenDialog(wx.Dialog):
    def __init__(self,parent):
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

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "Show")
        sizer_2.AddButton(self.button_APPLY)
        self.button_APPLY.SetDefault()

        sizer_2.Realize()

        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_APPLY)

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.SetSize((300,300))
        self.Center()
        self.Layout()

    def OnApply(self,event):
        choices=self.list_box_1.GetSelections()
        if len(choices)==0:
            wx.MessageBox("You have not selected any variable","Info")
        else:
            self.parent.names_to_show=self.names[choices]
            
            self.EndModal(wx.OK)
            self.Destroy()

##
# Dialog for manage the identifier columns
##  
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

        self.Center()
        self.Layout()
        
    def OnApply(self,event):
            choices=self.list_box_1.GetSelections()
            if len(choices)==0:
                wx.MessageBox("You have not selected any variable","Info")
            else: 
                for var in choices:
                    self.parent.identifier_cols.remove(self.names[var])
                    self.parent.controller.set_col_as_id(self.names[var],remove=True)
                
                self.EndModal(wx.OK)
                self.Destroy()

##
# Dialog for picking the inputs and outputs for the taks
## 
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
        sizer_8.Add(self.button_add_input, 0, wx.LEFT | wx.RIGHT | wx.TOP , 10)

        self.button_remove_input = wx.Button(self, wx.ID_ANY, "Remove")
        sizer_8.Add(self.button_remove_input, 0,wx.ALL, 10)

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
        sizer_11.Add(self.button_add_output, 0,wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.button_remove_output = wx.Button(self, wx.ID_ANY, "Remove")
        sizer_11.Add(self.button_remove_output, 0, wx.ALL, 10)

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
            
            self.controller.set_independent_variables(self._get_indexes(self.independent_variables))
            self.controller.set_targets(self._get_indexes(self.targets))

            self.EndModal(wx.ID_APPLY)
            self.Destroy()

    def _get_indexes(self,group):
        toAdd=[]
        names=list(self.names)
        for element in group:
            toAdd.append(names.index(element))
        return toAdd

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

##
# Dialog for manage settings
## 
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


        self.default_path_ctrl = wx.TextCtrl(self, wx.ID_ANY,self.currentSettings.default_path,style=wx.TE_READONLY,size=(300,-1))
        sizer_6.Add(self.default_path_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.icon_folder_bitmap = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("./front/resources/img/guardar.png", wx.BITMAP_TYPE_ANY))
        sizer_6.Add(self.icon_folder_bitmap, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_colors = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Colors"), wx.HORIZONTAL)
        sizer_3.Add(sizer_colors, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_1 = wx.GridSizer(2, 2, 2, 2)
        sizer_colors.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_7, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Inputs")
        sizer_7.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.input_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,self.currentSettings.independent_color)
        
        sizer_7.Add(self.input_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_8, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Outputs")
        sizer_8.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.output_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,self.currentSettings.target_color)
        
        sizer_8.Add(self.output_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_9, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Missing values")
        sizer_9.Add(label_3, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.nan_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,colour=self.currentSettings.nan_color)
        
        sizer_9.Add(self.nan_color_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_10, 1, wx.EXPAND, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Outliers")
        sizer_10.Add(label_4, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.outliers_color_ctrl = wx.ColourPickerCtrl(self, wx.ID_ANY,colour=self.currentSettings.outlier_color)
        
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
        response=IOManage.get_path_folder(self,"Select a new path").get_response()
        if response['status']==Status.OK:
            self.default_path_ctrl.SetLabelText(response['data'])

    def OnApply(self,evt):
        font_size=self.font_size_ctrl.GetValue()

        if font_size<9 or font_size>20:
            wx.MessageBox("Invalid value for font size","Error",wx.ICON_ERROR)
        else:
            self.currentSettings.font_size=font_size
            self.currentSettings.default_path=self.default_path_ctrl.GetValue()
            self.currentSettings.independent_color=self.input_color_ctrl.GetColour()
            self.currentSettings.target_color=self.output_color_ctrl.GetColour()
            self.currentSettings.nan_color=self.nan_color_ctrl.GetColour()
            self.currentSettings.outlier_color=self.outliers_color_ctrl.GetColour()

            message="Configuration saved!"
            if self.restart:
                message=message+" You need to restart the program to see the changes."
            wx.MessageBox(message,"Info",wx.OK)
            self.currentSettings.update_conf()
            self.EndModal(wx.ID_REFRESH)
            self.Destroy()

##
# Dialog for creating a set or adding columns
## 
class CreateSetDialog(wx.Dialog):
    def __init__(self,parent,title):
        
        
        wx.Dialog.__init__(self,parent)
        self.SetTitle(title)
        self.SetFont(parent.GetFont())
        self.new_set=parent.new_set
        self.controller=parent.controller
        self.current_names=self.controller.get_names().get_response()['data']

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
            
            if name in self.current_names:
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

##
# Dialog for displaying context help
##
class HelpDialog(wx.Dialog):
    def __init__(self,parent,file,title):
    
        wx.Dialog.__init__(self,parent)
        
        self.SetTitle("Help dialog")
        self.SetFont(parent.GetFont())
        self.title=title
        f = open(file)
        self.content=json.load(f)
        f.close()

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)

        self.text_search = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.text_search.ShowCancelButton(True)
        sizer_4.Add(self.text_search, 0, wx.ALL, 10)

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

        self.Bind(wx.EVT_SEARCH,self.OnSearchOnFiles,self.text_search)
        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnChangeTreeSelection,self.tree)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetSize(700,600)
        self.Center()
        self.Layout()
    

    def OnSearchOnFiles(self,evt):
        pattern=evt.GetString()
        if pattern!='':
            self.location_file=""
            
            if self._explore_tree(self.content,pattern):
                with open(self.location_file, 'r') as file:
                    content = file.read()
                self.browser.SetPage(content, "")

            self.location_file=""

    def _explore_tree(self,tree,pattern):
        keys=list(tree.keys())
        for key in keys:
            if isinstance(tree[key]['content'],bool):
                self._explore_tree(tree[key]['child'],pattern)
            else:
                if self._findPattern(pattern,tree[key]['content']):
                    return True
                
        if self.location_file!='':
            return True
        
        return False

    def _findPattern(self,pattern:str,leaf):
        file=leaf['file']
        with open(file, 'r') as file:
            content = file.read()
        if pattern in content:
            self.location_file=leaf['file']
            return True
        return False
    


    def OnChangeTreeSelection(self,evt):
        try:
            itemId=self.tree.GetSelection()
            if self.root!=itemId:
                selection=self.tree.GetItemText(itemId)
                parent_item=self.tree.GetItemParent(self.tree.GetSelection())
                parent=self.tree.GetItemText(parent_item)
                path=''
                if parent_item==self.root:
                    if not isinstance(self.content[selection]['content'],bool):
                        path=self.content[selection]['content']['file']
                else:
                    path=self.content[parent]['child'][selection]['content']['file']
                
                if path!='':
                    with open(path, 'r') as file:
                        content = file.read()

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

##
# Dialog for loading file optionss
##
class LoadFileDialog(wx.Dialog):
    def __init__(self,parent,conf):
        
        super(LoadFileDialog, self).__init__(parent)
        
        self.SetTitle("Load file")
        self.SetFont(parent.GetFont())
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
        self.button_OK.SetDefault()

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)
        self.SetEscapeId(self.button_CANCEL.GetId())

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnChangePath,self.button_change_path)
        self.Bind(wx.EVT_BUTTON,self.OnApply,self.button_OK)

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
        response=IOManage.get_path_import(self,"Open file",WILDCARD_DATA_FILE).get_response()
        if response['status']==Status.OK:
            self.path.SetLabelText(response['data'])
            self._on_change_path(response['data'])

##
# Dialog for loading see trace
##
class TraceDialog(wx.Dialog):
    def __init__(self,parent):
       
        wx.Dialog.__init__(self,parent)
        self.SetTitle("Trace dialog")

        self.SetFont(parent.GetFont())
        self.settings=parent.setting
        self.controller=parent.controller

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_filter = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Filter by level"), wx.HORIZONTAL)
        sizer_1.Add(sizer_filter, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.cb_level=wx.ComboBox(self,id=wx.ID_ANY,value="all",choices=["all","INFO","ERROR","WARNING"], style=wx.CB_READONLY)

        sizer_filter.Add(self.cb_level,0,wx.ALL,5)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Logs"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.text_logs = wx.TextCtrl(self, wx.ID_ANY,"", style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer_3.Add(self.text_logs, 1, wx.ALL | wx.EXPAND, 10)

        for log in self._fill_text("all"):
            self.text_logs.AppendText(log)
        
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
        self.text_logs.SetLabelText("")
        for log in logs:
            self.text_logs.AppendText(log)

    def _fill_text(self,level):
        logs=[]
        trace=Trace()
        history=trace.get_log_history()
        for log in history:
            if level!="all":
                if log['level']==level:
                    logs.append(str(log['time'])+" - "+str(log['level'])+" - "+log['message']+"\n")
            else:
                logs.append(str(log['time'])+" - "+str(log['level'])+" - "+log['message']+"\n")
        return logs

    def OnSave(self,evt):
        path=IOManage.GetPath(self,"Save file",WILDCARD_TEXT_FILE,default_name="logs.txt",default_folder=self.settings.get_default_path()).get_response()
        
        if path['status']==Status.OK: 
            fullPath=path['data']
            content=""

            for i in range(self.text_logs.GetNumberOfLines()):
                content+=self.text_logs.GetLineText(i)+"\n"

            response=self.controller.save_file(content,path=fullPath).get_response()
            
            if response['status']==Status.OK:
                wx.MessageBox("File saved succesfully in "+fullPath,"Info")
            else:
                wx.MessageBox("An unexpected error has ocurred.","Error",wx.ICON_ERROR)
