import solara

from cosmicds.state import GLOBAL_STATE


@solara.component
def SpeechSynthesizer():

    speech = GLOBAL_STATE.value.speech.model_dump()

    @solara.component_vue("SpeechSynthesizer.vue")
    def _SpeechSynthesizer(
        speech,
    ):
        pass

    return _SpeechSynthesizer(speech=speech)
