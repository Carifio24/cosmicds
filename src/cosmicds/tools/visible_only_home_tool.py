from cosmicds.config import register_tool
from glue_plotly.viewers.common.tools import PlotlyHomeTool


@register_tool
class PlotlyVisibleOnlyHomeTool(PlotlyHomeTool):

    tool_id = 'cosmicds:visible_only_home'

    def activate(self):
        with self.viewer.figure.batch_update():
            self.viewer.state.reset_limits(visible_only=True)
