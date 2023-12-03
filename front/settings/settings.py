""" Class for managing the app settings"""
import platform
import os
from os import path
import xml.etree.ElementTree as ET
from pathlib import Path
import wx


class Settings():
    """
        Clase para almacenar los ajustes de la pantalla
        Ajustes:
            tamaño de celdas
            tamaño de letra
    """
    def __init__(self):
        """
            Method constructor of the class
        """
        self.file="nrl_settings.xml"
        if path.exists(self.file):
            self._parse_content(file=self.file)
        else:
            user_path=str(os.path.expanduser("~"))
            sistema = platform.system()
            if sistema=="Windows":
                neurorule_path=user_path+"\\NeuroRule"
            else:
                neurorule_path=user_path+"/NeuroRule"
            settings={'height_cell_size':19,'width_cell_size':80,'font_size':10
                  ,'initial_rows':20,'pvalue_threshold':0.05,'default_path':neurorule_path
                  ,'target_color':wx.Colour("#ad9e72"),'independent_color':wx.Colour("#5a8f68")
                  ,'default_color':wx.Colour("#ffffff"),'outlier_color':wx.Colour("#c9be83")
                  ,'nan_color':wx.Colour("#c76d6f")}
            self._initialize(settings)
        self.font = wx.Font(int(self.font_size), wx.FONTFAMILY_DEFAULT
                            , wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    def _parse_content(self,file):
        tree = ET.parse(file)
        root = tree.getroot()
        self.root_node=root
        settings={}
        for child in root:
            val=child.text
            if val is None:
                val=""
            settings[child.tag]=val
        self._initialize(settings)

    def update_conf(self):
        """
            Function that calls the build xml
        """
        self._build_xml()

    def _initialize(self,settings):
        """
            Function that initialize the settings with the values from a dictionary

            Args:
                - settings: dictionary of the elements of the settings
        """
        self.height_cell_size=int(settings['height_cell_size'])
        self.width_cell_size=int(settings['width_cell_size'])
        self.font_size=int(settings['font_size'])
        self.initial_rows=int(settings['initial_rows'])
        self.pvalue_threshold=float(settings['pvalue_threshold'])
        self.default_path=settings['default_path']
        self.target_color=wx.Colour(settings['target_color'])
        self.independent_color=wx.Colour(settings['independent_color'])
        self.default_color=wx.Colour(settings['default_color'])
        self.outlier_color=wx.Colour(settings['outlier_color'])
        self.nan_color=wx.Colour(settings['nan_color'])

    def get_default_path(self):
        """
            Function that returns the path that is currently setted as defaultt
        """
        return Path(self.default_path).name
    
    def _build_xml(self):
        """
            Function that builds the xml for the settings and writes it to the file
        """
        root = ET.Element("conf")
        ET.SubElement(root, "height_cell_size").text = str(self.height_cell_size)
        ET.SubElement(root, "width_cell_size").text = str(self.width_cell_size)
        ET.SubElement(root, "font_size").text = str(self.font_size)
        ET.SubElement(root, "initial_rows").text = str(self.initial_rows)
        ET.SubElement(root, "pvalue_threshold").text = str(self.pvalue_threshold)
        ET.SubElement(root, "default_path").text = self.default_path
        ET.SubElement(root, "target_color").text =self.target_color.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "independent_color").text = self.independent_color.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "default_color").text = self.default_color.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "outlier_color").text = self.outlier_color.GetAsString(wx.C2S_HTML_SYNTAX)
        ET.SubElement(root, "nan_color").text = self.nan_color.GetAsString(wx.C2S_HTML_SYNTAX)
        tree = ET.ElementTree(root)
        tree.write(self.file)
