from ipyvuetify import VuetifyTemplate
from ipywidgets import widget_serialization
from traitlets import Dict, Instance
from ipywidgets import DOMWidget

from ...utils import load_template

class WWTWidgetLayout(VuetifyTemplate):
    template = load_template("wwt_widget_layout.vue", __file__).tag(sync=True)
    widget = Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)
    css_style = Dict().tag(sync=True)

    def __init__(self, wwt_widget, style=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.css_style = style or {'height': '300px'}
        self.widget = wwt_widget
