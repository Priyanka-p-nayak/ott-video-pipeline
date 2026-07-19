"""SQLAlchemy model representing a single viewer analytics event."""

from sqlalchemy import Column, Integer, String, DateTime
from app.analytics.db import Base


class ViewerEvent(Base):
       """Represents one row in the viewer_events table."""

       __tablename__ = 'viewer_events'

       id = Column(Integer, primary_key=True, autoincrement=True)
       video_id = Column(String, nullable=False, index=True)
       event_type = Column(String, nullable=False)
       event_timestamp = Column(DateTime, nullable=False)
       kafka_partition = Column(Integer, nullable=True)
       kafka_offset = Column(Integer, nullable=True)

       def __repr__(self):
           return f"<ViewerEvent(video_id={self.video_id}, event={self.event_type})>"