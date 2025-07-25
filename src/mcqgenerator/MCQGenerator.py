import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from openai import OpenAI
import langchain
# from langchain.llms import OpenAI
from langchain.agents import AgentType
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain, SequentialChain
from langchain.callbacks import get_openai_callback
from langchain.prompts import PromptTemplate
import PyPDF2


# Load environment variables from the .env file
load_dotenv()

# Access the environment variables just lie you would with os.environ
key = os.getenv("API_KEY")

BASE_URL = os.getenv("BASE_URL")

llm = ChatOpenAI(api_key = key, base_url = BASE_URL, model_name = "gpt-3.5-turbo", temperature=0.5)

# Input prompt Template
template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice question for {subject} student in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforiming the text as well
Make sure to format your response like RESPONSE_JSON below and use it as a guide.\
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables = ["text", "number", "subject", "tone", "response_json"],
    template = template
)

quiz_chain = LLMChain(llm = llm, 
                      prompt = quiz_generation_prompt, 
                      output_key = "quiz", 
                      verbose = True)

# Reviews Prompt and Template

template2 = """
You are an expert english grammarian and writer. Given a multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for the complexity.
if the quiz is not at per with the cognitive and analytical abilities of the students.\
update the quiz question which need to be changed and change the tone such that it perfectly fit the student ability
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

Quiz_evaluation_prompt = PromptTemplate(
    input_variable = ["subject", "quiz"],
    template = template2
)

review_chain = LLMChain(
    llm = llm, 
    prompt = Quiz_evaluation_prompt,
    output_key = "review",
    verbose = True
)

# This an overall chain where we run the two chain in sequence
generate_evaluate_chain = SequentialChain(chains = [quiz_chain, review_chain],
                                          input_variables = ["text", "number", "subject", "tone", "response_json"],
                                          output_variables = ["quiz", "review"],
                                          verbose = True)

