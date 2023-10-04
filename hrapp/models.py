from pydantic import BaseModel, Field
from typing import List, Optional

class Languages(BaseModel):
    known_languages: List[str] = Field (..., example="English, French, German")
        
class TechnologySkills(BaseModel):
    programming: List[str] = Field (..., example="Java, C, C++, Oracle")
        
class Education(BaseModel):
    institute: str = Field (..., example="IIT, NIIT")
    course: str = Field (..., example="B.Sc, M.Sc, B.Tech")    
    academic_achievement: List[str] = Field (None, example="Awarded presidents medal, university rank holder")
        
class WorkExperience(BaseModel):
    company: str = Field (..., example="Sapient")
    employement_start_date: str = Field (..., example="2002")
    employement_end_date: str = Field (..., example="2004")
    jobtitle: str = Field (..., example="Senior Engineer, Senior Programmer")
    technologies: List[str] = Field (None, example="Java, SQL, PL-SQL, C, C++")
    projects: List[str] = Field(None, example="projects or assignments worked on while employed with the company")
    
class Candidate(BaseModel):
    name: str = Field (..., example="Rahul Jain")
    email: str = Field (None, example="rsjain1978@gmail.com")
    
    experience: List[WorkExperience]
    education: List[Education]
    languages: List[Languages]
#     techskills: List[TechnologySkills]