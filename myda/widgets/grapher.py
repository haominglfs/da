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
from pyecharts.charts import Bar,BMap,Line,Pie
from pyecharts import options as opts
from pyecharts.globals import BMapType, ChartType

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


def pie(**kwargs):
    df = kwargs['data_frame']
    x = kwargs['x']
    df = df.groupby(by=[x]).size()
    height = str(int(0.6 * QtWidgets.QDesktopWidget().screenGeometry().height())) + 'px'
    pie = (Pie(init_opts=opts.InitOpts(height=height))
    .add("", [list(z) for z in zip(df.index.tolist(), df.tolist())])
    .set_global_opts(
        title_opts=opts.TitleOpts(title="饼图")
        ,legend_opts=opts.LegendOpts(pos_bottom='1%')
        ,)
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    .render())

def line(**kwargs):
    df = kwargs['data_frame']
    x = kwargs['x']
    y = kwargs['y(sum)']
    df = df[[x,y]].groupby(by=[x]).sum()
    xvals = df.index.tolist()
    yvals = df[y].tolist()
    ystr = y.replace('(','[')
    ystr = ystr.replace(')',']')
    line = Line().add_xaxis(xvals).add_yaxis(ystr,yvals).set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=40)))
    line.render()


def bar(**kwargs):
    df = kwargs['data_frame']
    x = kwargs['x']
    df = df.groupby(by=[x]).size()
    xvals = df.index.tolist()
    yvals = df.tolist()
    bar = Bar().add_xaxis(xvals).add_yaxis("数量", yvals)
    bar.render()


def bmap(**kwargs):
    df = kwargs['data_frame']
    pos = kwargs['pos']
    value = kwargs['value']
    df = df.groupby(by=[pos],as_index=False).sum()
    addresses = df[pos].tolist()
    values = df[[pos,value]].values

    geo_coord_list = get_latlng(addresses)
    height = str(int(0.6 * QtWidgets.QDesktopWidget().screenGeometry().height()))+'px'
    bmap = BMap(is_ignore_nonexistent_coord=True,init_opts=opts.InitOpts(height=height))
    for item in geo_coord_list:
        bmap.add_coordinate(item[0],item[2],item[1])

    bmap.add_schema(
        baidu_ak='t6FhPX8kta44hnWYUb9wN3sam3p2G6AG'
        ,center=[104.114129, 37.550339]
        # ,map_style={
        #             "styleJson": [
        #                 {
        #                     "featureType": "road",
        #                     "elementType": "all",
        #                     "stylers": {
        #                         "lightness": 20
        #                     }
        #                 }, {
        #                     "featureType": "highway",
        #                     "elementType": "geometry",
        #                     "stylers": {
        #                         "visibility": "off"
        #                     }
        #                 }, {
        #                     "featureType": "railway",
        #                     "elementType": "all",
        #                     "stylers": {
        #                         "visibility": "off"
        #                     }
        #                 }, {
        #                     "featureType": "local",
        #                     "elementType": "labels",
        #                     "stylers": {
        #                         "visibility": "off"
        #                     }
        #                 }, {
        #                     "featureType": "water",
        #                     "elementType": "all",
        #                     "stylers": {
        #                         "color": "#d1e5ff"
        #                     }
        #                 }, {
        #                     "featureType": "poi",
        #                     "elementType": "labels",
        #                     "stylers": {
        #                         "visibility": "off"
        #                     }
        #                 }, {
        #                     "featureType": "land",
        #                     "elementType": "all",
        #                     "stylers": {
        #                         "color": "#cfe2f3ff",
        #                         "lightness": -50,
        #                         "saturation": -8
        #                     }
        #                 }, {
        #                     "featureType": "water",
        #                     "elementType": "all",
        #                     "stylers": {
        #                         "color": "#0b5394ff",
        #                         "weight": "8",
        #                         "lightness": 41,
        #                         "saturation": 13
        #                     }
        #                 }
        #             ]
        #         }
       )
    bmap.add_control_panel(
        copyright_control_opts=opts.BMapCopyrightTypeOpts(position=3),
        maptype_control_opts=opts.BMapTypeControlOpts(
            type_=BMapType.MAPTYPE_CONTROL_DROPDOWN
        ),
        scale_control_opts=opts.BMapScaleControlOpts(),
        overview_map_opts=opts.BMapOverviewMapControlOpts(is_open=True),
        navigation_control_opts=opts.BMapNavigationControlOpts(),
        geo_location_control_opts=opts.BMapGeoLocationControlOpts(),
    )
    bmap.add(type_="effectScatter"
             ,series_name="仪器"
             ,data_pair=values
             ,label_opts=opts.LabelOpts(is_show=False))
    bmap.render()

schemas = [Schema(name='bmap',
                  args=[ColumnArg(arg_name='pos'),
                        ColumnArg(arg_name='value')],
                  label='地图',
                  function=bmap,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/map.svg')),
            Schema(name='bar',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y(个数)')],
                  label='柱图',
                  function=bar,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/bar.svg')),
            Schema(name='pie',
                  args=[ColumnArg(arg_name='x')],
                  label='饼图',
                  function=pie,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/pie.svg')),
            Schema(name='line',
                  args=[ColumnArg(arg_name='x'),
                        ColumnArg(arg_name='y(sum)')],
                  label='线图',
                  function=line,
                  icon_path=os.path.join(myda.__path__[0], 'resources/images/plotly/line.svg'))
           ]