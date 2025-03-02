from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List, Optional
from pydantic import BaseModel, RootModel, Field


class WordParts(BaseModel):
    type: Optional[str] = None
    formality: Optional[str] = None

class StringList(RootModel):
    root: List[WordParts]

parser = PydanticOutputParser(pydantic_object=StringList)

prompt = PromptTemplate.from_template(
    """
    Extract unique Japanese words from these lyrics:
    {lyrics}
    
    {format_instructions}
    """,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

print(prompt.format(lyrics="Hello World"))