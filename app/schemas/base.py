# app/schemas/base.py
from pydantic import BaseModel, ConfigDict

class ORMModel(BaseModel):
    # Pydantic v2 style (preferred over inner Config):
    model_config = ConfigDict(from_attributes=True)

class InputModel(BaseModel):
    # For request bodies; no special config needed
    pass
