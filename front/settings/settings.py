


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
        self.font_size=20
        self.initial_rows=20

        self.targetColor="#ad9e72"
        self.independentColor="#5a8f68"
        self.defaultColor="#ffffff"

        self.cleanSettings=[]
        self.preprocessSettings=[]
        self.modelSettings=[]

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
        


class CleanSettings():

    def __init__(self,name,delete_outliers,delete_missing,strategy_outliers,strategy_missing,highlight_outliers):
        
        self.name=name
        self.conf={'delete_outliers':delete_outliers,'delete_missing':delete_missing,'strategy_outliers':strategy_outliers,'strategy_missing':strategy_missing,'highlight_outliers':highlight_outliers}

    
    def getName(self):
        return self.name
    

    def getConfiguration(self):
        return self.conf