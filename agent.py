# agent.py
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.search import search_knowledge
from tools.extract import extract_requirements
from tools.generate import generate_response
import json
from datetime import datetime
import streamlit as st

# === LLM ===
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# === TOOLS ===
tools = [search_knowledge, extract_requirements, generate_response]

# === PROMPT (updated) ===
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a Digital Worker at a CRO. Use tools strictly in order:

1) extract_requirements(rfp_text=<full text>) -> dict with 'key_requirements': list[str]
2) search_knowledge(query=<dict from step 1 or list[str]>) -> str of cited snippets
3) generate_response(requirements=<dict from step 1 or list[str]>, context=<str from step 2>)

Rules:
- Cite sources.
- No hallucinations.
Current date: {current_date}
"""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# === AGENT ===
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# === AUDIT LOGGING ===
# agent.py (FINAL VERSION)
def run_with_audit(rfp_text: str, trace_placeholder=None, draft_placeholder=None):
    start_time = datetime.now()

    # Reset trace
    if trace_placeholder:
        with trace_placeholder.container():
            st.subheader("Live Reasoning (ReAct)")

    # Step 1: Extract
    with trace_placeholder.container():
        with st.spinner("1. Extracting requirements..."):
            req_result = extract_requirements.invoke({"rfp_text": rfp_text})
            st.markdown("**extract_requirements** → Done")

    # Step 2: Search
    query = f"{req_result.get('project_type', '')} {req_result.get('client', '')} budget {req_result.get('budget_range', '')}"
    with trace_placeholder.container():
        with st.spinner("2. Searching knowledge base..."):
            context = search_knowledge.invoke({"query": query})
            st.markdown("**search_knowledge** → Found relevant docs")

    # Step 3: Generate
    with trace_placeholder.container():
        with st.spinner("3. Generating response..."):
            draft = generate_response.invoke({"requirements": req_result, "context": context})
            st.markdown("**generate_response** → Draft ready")

    # Audit
    audit = {
        "rfp_id": f"RFP-{start_time.strftime('%Y%m%d-%H%M')}",
        "timestamp": start_time.isoformat(),
        "duration_seconds": (datetime.now() - start_time).total_seconds(),
        "tool_calls": ["extract_requirements", "search_knowledge", "generate_response"],
        "sources_cited": [line.split("[")[1].split("]")[0].split(" | ")[0] for line in context.split("\n---\n") if
                          "[" in line],
        "final_output": draft
    }

    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps(audit) + "\n")

    return draft, audit