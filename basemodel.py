from pydantic import BaseModel

class URL(BaseModel):
    url: str

class NAME(BaseModel):
    name: str


class TRADEMARK(BaseModel):
    company_name: str
    company_cin: str

class APPSTORE(BaseModel):
    url: str

class PLAYSTORE(BaseModel):
    url: str