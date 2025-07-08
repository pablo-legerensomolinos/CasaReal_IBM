from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from backend_database_query.env import Db2Config

class Base(DeclarativeBase):
    __table_args__ = {'schema': Db2Config.schema}