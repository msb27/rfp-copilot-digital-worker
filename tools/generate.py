# tools/generate.py (FIXED)
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

template = """
You are a Senior Proposal Writer at a leading CRO. Write a professional, compliant RFP response.

Use this template:
{template}

Available context (from past wins and compliance):
{context}

Structured RFP requirements:
{requirements}

Rules:
- Never hallucinate claims
- Cite sources in [brackets]
- Follow Veeva/FDA rules exactly
- Be concise but compelling

Output only the final response in Markdown.
"""

prompt = ChatPromptTemplate.from_template(template)

# Load response template
with open("knowledge/templates/rfp_response_template.md", "r") as f:
    RESPONSE_TEMPLATE = f.read()

@tool
def generate_response(requirements: dict, context: str) -> str:
    """
    Generate a compliant, on-brand RFP response draft using template and context.
    """
    # === FIX 1: Validate and parse requirements ===
    if not isinstance(requirements, dict):
        try:
            requirements = json.loads(requirements) if isinstance(requirements, str) else {}
        except:
            requirements = {"error": "Invalid requirements format", "raw": str(requirements)[:200]}

    if not requirements:
        return "ERROR: `requirements` is empty. Did you call `extract_requirements` first?"

    # === FIX 2: Safe context ===
    context = context or "No context provided."

    chain = prompt | llm
    try:
        response = chain.invoke({
            "template": RESPONSE_TEMPLATE,
            "context": context,
            "requirements": json.dumps(requirements, indent=2)
        })
        return response.content
    except Exception as e:
        return f"Generation failed: {str(e)}"