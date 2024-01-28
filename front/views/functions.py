import wx
import re

def get_task_name(window):
    ok=False
    taskname=""
    cancel=False

    while(not ok and not cancel):
        dialog=wx.TextEntryDialog(window,message="Entry a name for the task",caption="Task name")
        code=dialog.ShowModal()
                
        if code==wx.ID_OK:
            taskname=dialog.GetValue()
            ok=validate_name(taskname)
        elif code==wx.ID_CANCEL:
            cancel=True

        if not ok and not cancel:
            wx.MessageBox("Invalid task name, it can only contain alphanumeric characters, '-' and '_'. ","Error",wx.OK|wx.ICON_ERROR)
    
    return taskname,cancel

def validate_name(name):
    patron = r'^[a-zA-Z0-9_-]+$'
    ok=bool(re.match(patron, name))
    return ok

def validate_range(range):
    patron = r'^[\(\[]-?\d+(\.\d+)?,-?\d+(\.\d+)?[\)\]]+$'
    ok=bool(re.match(patron, range))
    return ok