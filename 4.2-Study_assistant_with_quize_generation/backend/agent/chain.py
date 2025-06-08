from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

from .prompt import study_agent_prompt
from .outputparser import SummaryQuizOutput

load_dotenv()

chatgpt = ChatOpenAI(model='gpt-4o-mini', temperature=0)
parser = PydanticOutputParser(pydantic_object=SummaryQuizOutput)

prompt = PromptTemplate(
    template=study_agent_prompt,
    input_variables=["study_material"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

study_agent_chain = (prompt
           |
         chatgpt
           |
         parser)


