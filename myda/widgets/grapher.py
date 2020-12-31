from PyQt5 import QtCore, QtWidgets, QtGui
from myda.widgets.spinner import Spinner
from myda.widgets.dragger import Dragger
from myda.widgets.chart_viewer import ChartViewer
from myda.store import GuiDataFrame
from dataclasses import dataclass
from typing import List,Callable
import os
import myda
from myda.utils import get_logger
from myda.bmap_helper import get_latlng,convert_data
from pyecharts.charts import Bar
from pyecharts.charts import BMap
from pyecharts import options as opts

logger = get_logger(__name__)


@dataclass
class Arg:
    arg_name: str


@dataclass
class ColumnArg(Arg):
    pass


@dataclass
class OptionListArg(Arg):
    values: List[str]


@dataclass
class Schema:
    name: str
    args: List[Arg]
    label: str
    function: Callable
    icon_path: str

class Grapher(QtWidgets.QWidget):
    def __init__(self, df: GuiDataFrame):
        super().__init__()

        self.gdf = df
        self.workers = []

        self.plot_type_picker = QtWidgets.QListWidget()
        self.plot_type_picker.setViewMode(self.plot_type_picker.IconMode)
        self.plot_type_picker.setWordWrap(True)
        self.plot_type_picker.setSpacing(20)
        self.plot_type_picker.setResizeMode(self.plot_type_picker.Adjust)
        self.plot_type_picker.setDragDropMode(self.plot_type_picker.NoDragDrop)
        self.plot_type_picker.sizeHint = lambda: QtCore.QSize(500, 250)
        self.plot_type_picker.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        for schema in schemas:
            icon = QtGui.QIcon(schema.icon_path)
            text = schema.label
            item = QtWidgets.QListWidgetItem(icon, text)
            self.plot_type_picker.addItem(item)

        self.plot_type_picker.itemSelectionChanged.connect(self.on_type_changed)

        self.dragger = Dragger(sources=df.dataframe.columns,
                               destinations=[],
                               source_types=df.dataframe.dtypes.values.astype(str))
        self.dragger.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.chart_viewer = ChartViewer()
        self.chart_viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                         QtWidgets.QSizePolicy.Expanding)

        self.spinner = Spinner()
        self.spinner.setParent(self.chart_viewer)

        # layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.plot_type_picker, 0, 0)
        self.layout.addWidget(self.dragger, 1, 0)
        self.layout.addWidget(self.chart_viewer, 0, 1, 2, 1)
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)

        # signals
        self.dragger.finished.connect(self.on_dragger_finished)

    def on_type_changed(self):
        if len(self.plot_type_picker.selectedItems()) == 0:
            return

        self.selected_plot_label = self.plot_type_picker.selectedItems()[0].text()
        self.current_schema = next(filter(lambda schema: schema.label == self.selected_plot_label, schemas))
        arg_list = [arg.arg_name for arg in self.current_schema.args]

        self.dragger.set_destinations(arg_list)

    def on_dragger_finished(self):
        self.spinner.start()

        # df = flatten_df(self.pgdf.dataframe)
        df = self.gdf.dataframe
        kwargs = {"data_frame": df}
        for key, val in self.dragger.get_data().items():
            if type(val) == list and len(val) == 0:
                continue
            elif type(val) == list and len(val) == 1:
                kwargs[key] = val[0]
            elif type(val) == list and len(val) > 1:
                kwargs[key] = val
            else:
                kwargs[key] = val

        func = self.current_schema.function
        self.current_worker = Worker(func, kwargs)
        self.current_worker.finished.connect(self.worker_callback)
        self.current_worker.finished.connect(self.current_worker.deleteLater)
        self.current_worker.start()
        self.workers.append(self.current_worker)

    @QtCore.pyqtSlot(object)
    def worker_callback(self, fig):
        self.chart_viewer.set_figure()
        self.spinner.stop()


class Worker(QtCore.QThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, func, kwargs):
        d = {k: v for k, v in kwargs.items() if k != "data_frame"}
        logger.debug(f"Creating Worker. {func.__name__} {d}")
        QtCore.QThread.__init__(self)
        self.func = func
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(**self.kwargs)
            d = {k: v for k, v in self.kwargs.items() if k != "data_frame"}
            logger.debug(f"Finished Worker run. {self.func.__name__} {d}")
            self.finished.emit(result)
        except Exception as e:
            logger.error(e)
            self.finished.emit(None)


def bar(**kwargs):
    # bar = Bar().add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]).add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    bmap = BMap().add_schema(baidu_ak='t6FhPX8kta44hnWYUb9wN3sam3p2G6AG')
    bar.render()


def bmap(**kwargs):
    print(kwargs)
    df = kwargs['data_frame']
    pos = kwargs['pos']
    value = kwargs['value']
    df = df.groupby(by=[pos],as_index=False).sum()
    addresses = df[pos].tolist()
    values = df[[pos,value]].values

    geo_coord_list = get_latlng(addresses)
    # data = convert_data(values,geo_coord_map)

    print(addresses)
    print(values)
    # print(data)

    bmap = BMap(is_ignore_nonexistent_coord=True)
    for item in geo_coord_list:
        bmap.add_coordinate(item[0],item[1],item[2])

    bmap = BMap(is_ignore_nonexistent_coord=True)
    bmap.set_global_opts(init_opts=opts.InitOpts(height='1000px'))
    bmap.add_schema(baidu_ak='t6FhPX8kta44hnWYUb9wN3sam3p2G6AG',center=[104.114129, 37.550339])
    # bmap.add(type_="effectScatter",series_name="仪器",data_pair=data,label_opts=opts.LabelOpts(formatter="{c}"))
    bmap.add(type_="effectScatter"
             ,series_name="仪器"
             ,data_pair=values
             ,label_opts=opts.LabelOpts(is_show=False))
    bmap.render()

schemas = [Schema(name='bmap',
                  args=[ColumnArg(arg_name='pos'),
                        ColumnArg(arg_name='value')],
                  label='Histogram',
                  function=bmap,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-histogram.svg')),
           Schema(name='scatter',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='color'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Scatter',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-scatter.svg')),
           Schema(name='line',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='color'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Line',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-line.svg')),
           Schema(name='bar',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='color'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Bar',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-bar.svg')),
           Schema(name='box',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='color'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Box',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-box.svg')),
           Schema(name='violin',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='color'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Violin',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-violin.svg')),
           Schema(name='scatter_3d',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='z'),
                        ColumnArg(arg_name='color')],
                  label='Scatter 3D',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-scatter3d.svg')),
           Schema(name='density_heatmap',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='z'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Heatmap',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-heatmap.svg')),
           Schema(name='density_contour',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y'),
                        ColumnArg(arg_name='z'),
                        ColumnArg(arg_name='facet_row'),
                        ColumnArg(arg_name='facet_col')],
                  label='Contour',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-contour.svg')),
           Schema(name='pie',
                  args=[ColumnArg(arg_name='names'),
                        ColumnArg(arg_name='values')],
                  label='Pie',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-pie.svg')),
           Schema(name='scatter_matrix',
                  args=[ColumnArg(arg_name='dimensions'),
                        ColumnArg(arg_name='color')],
                  label='Splom',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/trace-type-splom.svg')),
           Schema(name='word_cloud',
                  args=[ColumnArg(arg_name='columns'),
                        ],
                  label='Word Cloud',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/word-cloud.png'))

           ]