import solara

from typing import Callable, Optional


@solara.component_vue("MathJaxSupport.vue")
def MathJaxSupport(
    setup: Optional[Callable[[str], str]] = None,
    callback: Optional[Callable[[str, str], None]] = None
):
    pass
