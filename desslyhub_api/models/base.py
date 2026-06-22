from pydantic import BaseModel, ConfigDict


class DesslyHubModel(BaseModel):
    """Базовая модель: неизменяемая, заполняется по именам полей и по алиасам."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)
