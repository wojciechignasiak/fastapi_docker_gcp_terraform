#internal modules
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema

#3rd party libraries
from sqlmodel import SQLModel, Field, Relationship

#1st party libraries
from uuid import UUID, uuid4


class CandidateSchema(SQLModel, table=True):
    __tablename__ = "candidate"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str
    last_name: str

    job_positions: list["JobPositionSchema"] = Relationship(
        back_populates="candidates",
        link_model=JobPositionCandidateSchema
    )