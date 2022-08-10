# This file is for viewers that don't need anything beyond
# the standard CDS updating (the new toolbar, etc.)

from math import ceil, floor

from glue.config import viewer_tool
from glue_jupyter.bqplot.scatter import BqplotScatterView
from glue_jupyter.bqplot.histogram import BqplotHistogramView
from numpy import linspace

from cosmicds.components.toolbar import Toolbar

def cds_viewer(viewer_class, name=None, viewer_tools=None, label=None, state_cls=None):
    class CDSViewer(viewer_class):

        __name__ = name
        __qualname__ = name
        _state_cls = state_cls or viewer_class._state_cls
        inherit_tools = viewer_tools is None
        tools = viewer_tools or viewer_class.tools
        LABEL = label or viewer_class.LABEL

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ignore_conditions = []
            self.nticks = 7
            self.scale_x.observe(self._on_xaxis_change, names=['min', 'max'])

        def initialize_toolbar(self):
            self.toolbar = Toolbar(self)

            for tool_id in viewer_tools:
                mode_cls = viewer_tool.members[tool_id]
                mode = mode_cls(self)
                self.toolbar.add_tool(mode)

        def ignore(self, condition):
            self.ignore_conditions.append(condition)

        def add_data(self, data):
            if any(condition(data) for condition in self.ignore_conditions):
                return False
            return super().add_data(data)

        def add_subset(self, subset):
            if any(condition(subset) for condition in self.ignore_conditions):
                return False
            return super().add_subset(subset)

        def _on_xaxis_change(self, change):
            args = { 'x' + change["name"] : change["new"] }
            self.update_ticks(**args)

        def update_nticks(self, nticks):
            if nticks == self.nticks:
                return
            self.nticks = nticks
            self.update_ticks()

        def update_ticks(self, xmin=None, xmax=None):
            tick_spacings = [2000, 1500, 1000, 500, 250, 100, 50]
            xmin = xmin or self.state.x_min
            xmax = xmax or self.state.x_max
            x_range = xmax - xmin
            frac = int(x_range / self.nticks)
            spacing = next((t for t in tick_spacings if frac > t), 50)
            self.set_tick_spacing(spacing)

        def set_tick_spacing(self, spacing):
            xmin, xmax = self.state.x_min, self.state.x_max
            tmin = ceil(xmin / spacing) * spacing
            tmax = floor(xmax / spacing) * spacing
            n = int((tmax - tmin) / spacing) + 1
            self.axis_x.tick_values = list(linspace(tmin, tmax, n))
        
    return CDSViewer


CDSScatterView = cds_viewer(
    BqplotScatterView,
    name='CDSScatterView',
    viewer_tools=[
        'bqplot:home',
        'bqplot:rectzoom',
        'bqplot:rectangle'
    ],
    label='2D scatter'
)

CDSHistogramView = cds_viewer(
    BqplotHistogramView,
    name='CDSHistogramView',
    viewer_tools=[
        'bqplot:home',
        'bqplot:xzoom',
        'bqplot:xrange'
    ],
    label='Histogram'
)
