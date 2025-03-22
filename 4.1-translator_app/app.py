import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langserve import add_routes

load_dotenv()
model_name = 'gpt-4o-mini'

# Create the model instance
model = ChatOpenAI(model=model_name)
parser = StrOutputParser()

# Set up the components
system_template = "Translate the following text into Japanese:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# Chain components
chain = prompt_template | model | parser

app = FastAPI(title="LangChain English to Japanese Translation API", version="1.0")
add_routes(app, chain, path="/chain")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
