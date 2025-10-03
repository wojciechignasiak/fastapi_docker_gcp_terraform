#internal modules
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema

#3rd party libraries
from sqlmodel import SQLModel, Field, Relationship

#1st party libraries
from uuid import UUID, uuid4



class JobPositionSchema(SQLModel, table=True):
    __tablename__ = "job_position"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str

    candidates: list["CandidateSchema"] = Relationship(
        back_populates="job_positions",
        link_model=JobPositionCandidateSchema
        )