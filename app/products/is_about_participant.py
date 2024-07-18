from pydantic import Field
from app.products.is_about_base import IsAboutBase


class IsAboutParticipant(IsAboutBase):
    Label: str = Field(default="Subject Unique Identifier")
    TermURL: str
