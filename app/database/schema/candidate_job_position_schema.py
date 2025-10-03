#3rd party libraries
from sqlmodel import SQLModel, Field

#1st party libraries
from uuid import UUID


class JobPositionCandidateSchema(SQLModel, table=True):
    __tablename__ = "job_position_candidate"

    job_position_id: UUID = Field(foreign_key="job_position.id", primary_key=True)
    candidate_id: UUID = Field(foreign_key="candidate.id", primary_key=True)

