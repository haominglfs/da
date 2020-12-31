import pandas as pd
from pandasgui import show
from pandasgui.datasets import pokemon, titanic, all_datasets

df = pd.read_excel('仪器数据.xlsx')

show(df)