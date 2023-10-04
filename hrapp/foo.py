from flask import Flask, request, jsonify, render_template
import os
import csv
from werkzeug.utils import secure_filename
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import openai
import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain import OpenAI

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def load_pdf(filename):    
    loader = PyPDFLoader(filename)
    documents = loader.load_and_split() 
    resume = ""
    for doc in documents:
        resume += "\n" + doc.page_content

    return resume

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_resumes():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    job_description = request.form['job_description']

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
    file.save(filename)
    print('Resume saved')

    resume = load_pdf(filename)

    print("Resume extracted")

    os.environ["OPENAI_API_KEY"] = "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"
    query = HumanMessage(content=resume)
    llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

    functions = [
        {
            "name":"get_candidate_details_from_resume",
            "description":"useful to extract candidate details, their past experience from resume",
            "parameters": Candidate.schema()
        }
    ]

    response = llm([query], functions=functions, function_call="auto")

    arguments_str = response.additional_kwargs["function_call"]["arguments"]
    arguments_dict = json.loads(arguments_str)
    
    resume_metadata=json.dumps(arguments_dict)

    print("Resume parsed")

    hr_prompt_template = """
    You are an expert working in HR team and you need to make recommendation to short list a candidate based on their metadata below. 

    Match these details against the Job Description and suggest if the candidate should be shortlisted for interview and is so why.

    [JOB_DESCRIPTION]
    We are looking for a Python Developer to join our engineering team and help us develop and maintain various software products.

    Python Developer responsibilities include writing and testing code, debugging programs and integrating applications with third-party web services. To be successful in this role, you should have experience using server-side logic and work well in a team.

    Ultimately, you’ll build highly responsive web applications that align with our business needs.

    Responsibilities
    Write effective, scalable code
    Develop back-end components to improve responsiveness and overall performance
    Integrate user-facing elements into applications
    Test and debug programs
    Improve functionality of existing systems
    Implement security and data protection solutions
    Assess and prioritize feature requests
    Coordinate with internal teams to understand user requirements and provide technical solutions
    Requirements and skills
    Work experience as a Python Developer
    Expertise in at least one popular Python framework (like Django, Flask or Pyramid)
    Knowledge of object-relational mapping (ORM)
    Familiarity with front-end technologies (like JavaScript and HTML5)
    Team spirit
    Good problem-solving skills
    BSc in Computer Science, Engineering or relevant field

    {META_DATA}
    """

    # prompt we want to use
    prompt = PromptTemplate(
        #input to the prompt
        input_variables=["META_DATA"],
        template=hr_prompt_template
    )

    # llm we want to use
    llm = OpenAI(temperature=0, verbose=True)

    # chain we want to use
    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run(META_DATA=resume_metadata)

    print("Resume analysed")
    print (response)

    return jsonify(success=True,message=response), 200

    # return jsonify(success=True,message='Yes'),

@app.route("/match_resumes", methods=["POST"])
def match_resumes():
    print("Matching..")

if __name__ == "__main__":
    app.run(debug=True)
