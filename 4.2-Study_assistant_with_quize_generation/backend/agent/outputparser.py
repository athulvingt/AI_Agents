from pydantic import BaseModel, Field
from typing import List

class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question based on the study material.")
    options: List[str] = Field(description="A list of 4 answer options.")
    answer: int = Field(description="The correct answer index.")

class SummaryQuizOutput(BaseModel):
    summary: str = Field(description="A brief  summary of the study material in key points")
    quiz: List[QuizQuestion] = Field(description="A list of quiz questions.")

# outputparser = PydanticOutputParser(pydantic_object=SummaryQuizOutput)
