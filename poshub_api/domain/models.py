from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StrictFloat, StrictStr


class OrderIn(BaseModel):
    customer_name: Annotated[StrictStr, Field(alias="nom_client", max_length=128)]
    total_amount: Annotated[StrictFloat, Field(alias="montant")]
    currency: Annotated[StrictStr, Field(alias="devise", pattern="^[A-Z]{3}$")]


class OrderOut(BaseModel):
    order_id: UUID = Field(alias="order")
    created_at: Annotated[datetime, Field(alias="created_at")]
    customer_name: Annotated[StrictStr, Field(alias="nom_client")]
    total_amount: Annotated[StrictFloat, Field(alias="montant")]
    currency: Annotated[StrictStr, Field(alias="devise")]
    created_by: Optional[str]
