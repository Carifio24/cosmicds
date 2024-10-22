import os
from pydantic import BaseModel
from functools import cached_property
from glue_jupyter import JupyterApplication
from glue.core import DataCollection, Session
import solara
from glue.core import Data, DataCollection


update_db_init = True
# CDS_DISABLE_DB must exist, and have the value 'true' to disable writing to the database
if 'CDS_DISABLE_DB' in os.environ:
    # check if it has a value and if it True
    cds_disable_db = os.getenv("CDS_DISABLE_DB")
    if cds_disable_db.lower() == 'true':
        print("Disabling database updates.")
        update_db_init = False
else:
    print("Database updates enabled.")


class BaseState(BaseModel):
    def as_dict(self):
        return self.model_dump()

    def update(self, new):
        return self.model_copy(update=new)


class Student(BaseModel):
    id: int = None


class Classroom(BaseModel):
    class_info: dict | None = {}
    size: int = 0


class Speech(BaseModel):
    pitch: float = 1.0
    rate: float = 1.0
    autoread: bool = False
    voice: str | None = None


class BaseLocalState(BaseState):
    debug_mode: bool = True
    title: str
    story_id: str
    piggybank_total: int = 0


class GlobalState(BaseState):
    drawer: bool = True
    speed_menu: bool = False
    loading_status_message: str = ""
    student: Student = Student()
    classroom: Classroom = Classroom()
    update_db: bool = update_db_init
    show_team_interface: bool = False
    allow_advancing: bool = True
    speech: Speech = Speech()

    @cached_property
    def _glue_app(self) -> JupyterApplication:
        return JupyterApplication()

    @cached_property
    def glue_data_collection(self) -> DataCollection:
        return self._glue_app.data_collection

    @cached_property
    def glue_session(self) -> Session:
        return self._glue_app.session
    
    def add_or_update_data(self, data: Data):
        if data.label in self.glue_data_collection:
            existing = self.glue_data_collection[data.label]
            existing.update_values_from_data(data)
            return existing
        else:
            self.glue_data_collection.append(data)
            return data


GLOBAL_STATE = solara.reactive(GlobalState())
