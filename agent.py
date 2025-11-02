# agent.py
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.search import search_knowledge
from tools.extract import extract_requirements
from tools.generate import generate_response
import json
from datetime import datetime

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
def run_with_audit(rfp_text: str):
    print("\nDigital Worker Activated")
    print("=" * 60)

    start_time = datetime.now()
    result = agent_executor.invoke({
        "input": rfp_text,
        "current_date": start_time.strftime("%Y-%m-%d")
    })
    end_time = datetime.now()

    # Build audit trail
    audit = {
        "rfp_id": f"RFP-{start_time.strftime('%Y%m%d-%H%M')}",
        "timestamp": start_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "input_length": len(rfp_text),
        "tool_calls": [],
        "sources_cited": [],
        "final_output": result["output"]
    }

    # Extract tool calls from intermediate steps
    if "intermediate_steps" in result:
        for step in result["intermediate_steps"]:
            tool_name = step[0].tool if step[0].tool else "unknown"
            audit["tool_calls"].append(tool_name)
            # Extract sources from search tool
            if tool_name == "search_knowledge":
                output = step[1]
                sources = [line.split("[")[1].split("]")[0].split(" | ")[0] for line in output.split("\n---\n") if
                           "[" in line]
                audit["sources_cited"].extend(sources)

    # Save audit
    log_path = "audit_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(audit) + "\n")

    print(f"\nAudit saved to {log_path}")
    return result["output"], audit