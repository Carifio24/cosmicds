from numpy import isnan
from numpy.linalg import LinAlgError
from solara import Reactive

from cosmicds.utils import fit_line, line_mark


class LineFitHandler:

    def __init__(self, figure, **kwargs):
        self.lines = []
        self.slopes = []
        self.active = Reactive(False)
        self.figure = figure
        self._show_labels = kwargs.get("show_labels", True)

    def activate(self):
        if self.active.value:
            self._clear_lines()
        else:
            self._fit_to_traces()
        self.active.set(not self.active.value)
        print("end of activate")
        print(self.figure.data)
        print(id(self.figure))
        
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

    def _create_fit_line(self, trace):

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

    def _fit_to_trace(self, trace, add_marks=True):
        try:
            line, slope = self._create_fit_line(trace)
            if line is None:
                return
            if add_marks:
                line = self.figure.add_trace(line).data[-1]
            self.lines.append(line)
            self.slopes.append(slope)
        except (LinAlgError, SystemError) as e:
            print(e)
            pass

    def _fit_to_traces(self):
        self._clear_lines()
        for trace in self.figure.data:
            self._fit_to_trace(trace, add_marks=True)

    def _clear_lines(self):
        self.figure.data = [mark for mark in self.figure.data if mark not in self.lines]
        self.lines = []
        self.slopes = []

