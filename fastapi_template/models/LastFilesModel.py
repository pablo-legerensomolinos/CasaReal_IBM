from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import mapped_column
from pydantic import BaseModel
from typing import Optional

from fastapi_template.models.BaseModel import Base

class LastFiles(Base):
    __tablename__ = 'LAST_FILES'

    name = mapped_column(String, primary_key=True, name='NAME', nullable=False)
    cos_path = mapped_column(String, name='COS_PATH', nullable=False)
    timestamp = mapped_column(Integer, name='TIMESTAMP', nullable=False)


class LastFilesAPI(BaseModel):
    name: str
    cos_path: str
    timestamp: int