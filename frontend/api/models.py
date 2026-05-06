from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from api.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False, default="txt")
    content = Column(Text)