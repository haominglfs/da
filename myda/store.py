import os
from dataclasses import dataclass, field
from typing import List, Union
import pandas as pd
from myda.utils import get_logger
from PyQt5 import QtWidgets
import  codecs
from xlsx2csv import Xlsx2csv

logger = get_logger(__name__)


class GuiDataFrame:
    def __init__(self, df: pd.DataFrame, name: str = 'Untitled'):
        super().__init__()
        df = df.copy()
        self.dataframe = df
        self.dataframe_original = df
        self.name = name
        self.grapher: Union["Grapher", None] = None


@dataclass
class Store:
    data: List[GuiDataFrame] = field(default_factory=list)
    navigator: Union["Navigator", None] = None
    mainWin: Union["MainWin", None] = None
    selected_pd: Union[GuiDataFrame, None] = None

    def import_dataframe(self, path):
        if not os.path.isfile(path):
            logger.warning("Path is not a file: " + path)
        elif path.endswith(".csv"):
            filename = os.path.split(path)[1].split('.csv')[0]
            df = pd.read_csv(path, engine='python',encoding='utf-8')
            self.add_dataframe(df, filename)
        elif path.endswith(".xlsx"):
            uppath = os.path.split(path)[0]
            filename = os.path.split(path)[1].split('.xlsx')[0]
            Xlsx2csv(path, outputencoding='utf-8').convert(uppath+filename+".csv")
            # Xlsx2csv(path, outputencoding="gbk").convert(uppath+filename+".csv")
            df = pd.read_csv(uppath+filename+".csv", engine='python',encoding='utf-8')
            # for sheet_name in df_dict.keys():
            #     df_name = f"{filename} - {sheet_name}"
            #     self.add_dataframe(df_dict[sheet_name], df_name)
            self.add_dataframe(df, filename)

        else:
            logger.warning("Can only import csv / xlsx. Invalid file: " + path)

    def add_dataframe(self, df: Union[pd.DataFrame],
                      name: str = "Untitled"):
        # 转换成gdf
        gdf = GuiDataFrame(df)
        gdf.name = name

        self.data.append(gdf)
        if gdf.grapher is None:
            from myda.widgets.grapher import Grapher
            gdf.grapher = Grapher(gdf)
            self.mainWin.stacked_widget.addWidget(gdf.grapher)

        # Add to nav
        shape = df.shape
        shape = str(shape[0]) + " X " + str(shape[1])

        item = QtWidgets.QTreeWidgetItem(self.navigator, [name, shape])
        self.navigator.itemSelectionChanged.emit()
        self.navigator.setCurrentItem(item)
        # self.navigator.apply_tree_settings()

    def get_gdf(self, name):
        return next((x for x in self.data if x.name == name), None)

    def select_gdf(self, name):
        gdf = self.get_gdf(name)
        grapher = gdf.grapher
        self.mainWin.stacked_widget.setCurrentWidget(grapher)
