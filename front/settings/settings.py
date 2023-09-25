
import wx

class Settings():
    """
        Clase para almacenar los ajustes de la pantalla
        Ajustes:
            tamaño de celdas
            tamaño de letra
    """
    def __init__(self):
        self.height_cell_size=19
        self.width_cell_size=80
        self.font_size=10
        self.initial_rows=20
        self.pvalue_threshold=0.05

        self.font = wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        
        self.targetColor="#ad9e72"
        self.independentColor="#5a8f68"
        self.defaultColor="#ffffff"
        self.outlierColor="#c9be83"
        self.NanColor="#c76d6f"

    def SetCellSize(self,height,width):
        self.height_cell_size=height
        self.width_cell_size=80
    
    def SetFontSize(self,height,width):
        self.height_cell_size=height
        self.width_cell_size=80

    def SetInitialRows(self,initial_rows):
        self.initial_rows=initial_rows

    def GetCellSize(self):
        return self.height_cell_size,self.width_cell_size
        