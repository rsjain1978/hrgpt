import os
import openai
import json
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .models import Candidate

# Always use environment variables for API keys
os.environ['OPENAI_API_KEY'] = ''
openai.api_key = os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_pdf(filename):    
    loader = PyPDFLoader(filename)
    documents = loader.load_and_split() 
    resume = ""
    for doc in documents:
        resume += "\n" + doc.page_content

    return resume

def parse_and_analyze_resume(resume):
    query = HumanMessage(content=resume)
    llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

    functions = [
        {
            "name": "get_candidate_details_from_resume",
            "description": "useful to extract candidate details, their past experience from resume",
            "parameters": Candidate.schema()
        }
    ]

    response = llm([query], functions=functions, function_call="auto")

    arguments_str = response.additional_kwargs["function_call"]["arguments"]
    print (arguments_str)
    # arguments_dict = json.loads(arguments_str)

    # resume_metadata = json.dumps(arguments_dict)

    return arguments_str

def analyze_resume(resume_metadata, job_description):

    print (job_description)
    if 'Python Developer' in job_description:
        desired_job_description = "Highly recommended for technical roles due to Python experience."
    elif 'Project Manager' in job_description:
        desired_job_description = "Suitable for management roles due to project management skills."
    elif 'Data Scientist' in job_description:
        desired_job_description = "Recommended for roles requiring data analysis and machine learning skills."
    else:
        desired_job_description = "No specific recommendation available for this job description."


    hr_prompt_template = """
    You are an expert working in HR team and you need to make recommendation to short list a candidate based on their metadata below.

    Match these details against the Job Description and suggest if the candidate should be shortlisted for interview and is so why.

    Response back using mark up format only

    [JOB_DESCRIPTION]
    {JOB_DESCRIPTION}

    {META_DATA}
    """

    # prompt we want to use
    prompt = PromptTemplate(
        #input to the prompt
        input_variables=["META_DATA","JOB_DESCRIPTION"],
        template=hr_prompt_template
    )

    # llm we want to use
    chain = LLMChain(llm=ChatOpenAI(model="gpt-4"), prompt=prompt, verbose=True)

    # Run the analysis
    response = chain.run(
        {
        "META_DATA":resume_metadata,
        "JOB_DESCRIPTION":desired_job_description
        }
    )

    return response
