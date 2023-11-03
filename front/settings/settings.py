
import wx
import os
import os.path as path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import xml.etree.cElementTree as ET
import platform


class Settings():
    """
        Clase para almacenar los ajustes de la pantalla
        Ajustes:
            tamaño de celdas
            tamaño de letra
    """
    def __init__(self):
        file="nrl_settings.xml"

        if path.exists(file):
            self._parse_content(file=file)

        else:
            user_path=str(os.path.expanduser("~"))
            sistema = platform.system()

            if sistema=="Windows":
                neurorule_path=user_path+"\\NeuroRule"
            else:
                neurorule_path=user_path+"/NeuroRule"
            dict={'height_cell_size':19,'width_cell_size':80,'font_size':10,'initial_rows':20,'pvalue_threshold':0.05,'defaultPath':neurorule_path,'targetColor':wx.Colour("#ad9e72"),'independentColor':wx.Colour("#5a8f68"),'defaultColor':wx.Colour("#ffffff"),'outlierColor':wx.Colour("#c9be83"),'NanColor':wx.Colour("#c76d6f")}
            self._initialize(dict)
        
        self.font = wx.Font(int(self.font_size), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    def _parse_content(self,file):
        tree = ET.parse(file)
        root = tree.getroot()

        self.root_node=root

        dict={}
        for child in root:
            
            val=child.text
            if val==None:
                val=""
            dict[child.tag]=val
        
        self._initialize(dict)

    def update_conf(self):
        self._build_xml()

    def _initialize(self,dict):
        self.height_cell_size=int(dict['height_cell_size'])
        self.width_cell_size=int(dict['width_cell_size'])
        self.font_size=int(dict['font_size'])
        self.initial_rows=int(dict['initial_rows'])
        self.pvalue_threshold=float(dict['pvalue_threshold'])
        self.defaultPath=dict['defaultPath']

        self.targetColor=wx.Colour(dict['targetColor'])
        self.independentColor=wx.Colour(dict['independentColor'])
        self.defaultColor=wx.Colour(dict['defaultColor'])
        self.outlierColor=wx.Colour(dict['outlierColor'])
        self.NanColor=wx.Colour(dict['NanColor'])


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
    
    def _build_xml(self):
        

        root = ET.Element("conf")

        ET.SubElement(root, "height_cell_size").text = str(self.height_cell_size)
        ET.SubElement(root, "width_cell_size").text = str(self.width_cell_size)
        ET.SubElement(root, "font_size").text = str(self.font_size)
        ET.SubElement(root, "initial_rows").text = str(self.initial_rows)
        ET.SubElement(root, "pvalue_threshold").text = str(self.pvalue_threshold)
        ET.SubElement(root, "defaultPath").text = self.defaultPath
        ET.SubElement(root, "targetColor").text =self.targetColor.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "independentColor").text = self.independentColor.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "defaultColor").text = self.defaultColor.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "outlierColor").text = self.outlierColor.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "NanColor").text = self.NanColor.GetAsString(wx.C2S_HTML_SYNTAX)

        tree = ET.ElementTree(root)
        tree.write("nrl_settings.xml")

       