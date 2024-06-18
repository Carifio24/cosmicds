from numpy import isnan
from numpy.linalg import LinAlgError
from plotly.graph_objects import Scatter
from solara import Reactive

from cosmicds.utils import fit_line, line_mark


class LineFitHandler:

    def __init__(self, figure, **kwargs):
        self.lines = []
        self.slopes = []
        self.active = Reactive(False)
        self.figure = figure
        self._show_labels = kwargs.get("show_labels", True)
        self._create_lines()

    def activate(self):
        if self.active.value:
            self._hide_lines()
        else:
            self._fit_to_traces()
        self.active.set(not self.active.value)
        print("end of activate")
        print(self.figure.data)
        print(id(self.figure))

    def _create_lines(self):
        self.scatters = [trace for trace in self.figure.data if isinstance(trace, Scatter)]
        for scatter in self.scatters:
            color = scatter.marker.color or "#000000"
            line = line_mark(0, 0, 0, 0, color)
            line.visible = False
            mark = self.figure.add_trace(line).data[-1]
            self.lines.append(mark)
        
    # The label displayed for each line

    def label(self, trace, line):
        slope = line.slope.value
        return f"Slope: {slope}" if not isnan(slope) else None

    def _refresh_if_active(self):
        if self.active.value:
            self._fit_to_traces()

    def _fit_line(self, trace):
        return fit_line(trace.x, trace.y)

    @property
    def x_range(self):
        return self.figure.layout.xaxis.range

    @property
    def show_labels(self):
        return self._show_labels

    @staticmethod
    def _get_layer_color(trace):
        return trace.marker.color

    @show_labels.setter
    def show_labels(self, show):
        if show != self._show_labels:
            self._show_labels = show
            self._refresh_if_active()

    def _line_for_scatter(self, trace):

        # Do the fit
        fit = self._fit_line(trace)
        if fit is None:
            return None, None
    
        # Create the fit line object
        # Keep track of this line and its slope
        # For now, the line spans from 0 to twice the edge of the viewer
        xrange = self.x_range
        if xrange is None:
            xrange = [0, 2]
        y = fit(xrange)
        slope = fit.slope.value
        label = self.label(trace, fit) if self.show_labels else None
        color = self._get_layer_color(trace)
        line = line_mark(xrange[0], y, xrange[1], y, color, label)
        return line, slope

    def _fit_to_scatter(self, scatter, mark):
        try:
            line, slope = self._line_for_scatter(scatter)
            if line is None:
                return
            json = line.to_plotly_json()
            json["visible"] = True
            mark.update(**json)
            self.slopes.append(slope)
        except (LinAlgError, SystemError) as e:
            print(e)
            pass

    def _fit_to_traces(self):
        self._hide_lines()
        for trace, line in zip(self.figure.data, self.lines):
            self._fit_to_scatter(trace, line)

    def _hide_lines(self):
        for line in self.lines:
            line.update(visible=False)
        self.slopes = []

