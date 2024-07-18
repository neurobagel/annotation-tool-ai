from pydantic import BaseModel


class IsAboutBase(BaseModel):  # type: ignore
    Label: str
    TermURL: str
