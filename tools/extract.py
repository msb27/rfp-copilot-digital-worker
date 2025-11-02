# tools/extract.py
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# Define structured output
class RFPRequirements(BaseModel):
    client: str = Field(..., description="Client name")
    project_type: str = Field(..., description="Type of project (e.g., Phase III, RWE)")
    scope: str = Field(..., description="High-level scope of work")
    budget_range: str = Field(..., description="Budget or range, e.g., $2M–$3M")
    timeline: str = Field(..., description="Expected duration, e.g., 18 months")
    submission_deadline: str = Field(..., description="RFP submission deadline")
    key_requirements: list[str] = Field(..., description="List of 3–5 must-have requirements")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert RFP analyst. Extract structured requirements from the RFP text. Be precise and complete."),
    ("human", "{rfp_text}")
])

structured_llm = llm.with_structured_output(RFPRequirements)
extract_chain = extraction_prompt | structured_llm

@tool
def extract_requirements(rfp_text: str) -> dict:
    """
    Extract structured requirements from raw RFP text.
    Returns JSON with client, scope, budget, timeline, etc.
    """
    try:
        result = extract_chain.invoke({"rfp_text": rfp_text[:10000]})  # Truncate if too long
        return result.dict()
    except Exception as e:
        return {"error": str(e), "raw_text": rfp_text[:500]}