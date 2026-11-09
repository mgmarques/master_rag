import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field

load_dotenv(override=True)

model = os.getenv("OPENAI_MODEL", "qwen2.5:7b")

llm = ChatOpenAI(
            model=model,  #  "tencent/hy3:free",  "gpt-4.1-mini"
            base_url="http://localhost:11434/v1", #"https://openrouter.ai/api/v1",
            api_key="olama", # os.getenv("OPENROUTER_API_KEY"),
            temperature=0
            )


documents = [
    Document(page_content="AcmeOrbit IT policy: Employees must return a borrowed laptop within 14 calendar days after the loan ends.", metadata={"source": "IT-LAPTOP-01"}),
    Document(page_content="AcmeOrbit travel policy: Expense claims must be submitted within 30 calendar days after travel.", metadata={"source": "TRAVEL-02"}),
    Document(page_content="AcmeOrbit security policy: Employees must use multifactor authentication for company accounts.", metadata={"source": "SECURITY-03"}),
]

embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
print(f"Vector store size: {len(vectorstore.store)} documents")

def retrieve_context(query: str, k: int = 1) -> str:
    hits = vectorstore.similarity_search(query, k=k)
    return "\n\n".join(f"Source: {d.metadata['source']}\n{d.page_content}" for d in hits)

class RouteDecision(BaseModel):
    needs_retrieval: bool = Field(description="True if the question requires AcmeOrbit internal policy facts")

class RAGState(TypedDict):
    question: str
    needs_retrieval: bool
    context: str
    answer: str

@tool
def search_company_policy(question: str) -> str:
    """Search AcmeOrbit internal policies. Use for any question about company rules or deadlines."""
    print("TOOL search_company_policy called with:", question)
    return retrieve_context(question)

tools = [search_company_policy]
llm_with_tools = llm.bind_tools(tools)

SYSTEM_B = ("You are an AcmeOrbit helpdesk assistant. "
            "For company policy questions, you MUST call search_company_policy before answering. "
            "Never invent company policies. Only state company-policy facts present in tool results; "
            "if absent, say 'I don't know'. Cite policy source IDs. "
            "Answer clearly and concisely.")

def agent_node(state: MessagesState):
    print("NODE agent")
    response = llm_with_tools.invoke([SystemMessage(content=SYSTEM_B)] + state["messages"])
    return {"messages": [response]}

# build the agentic RAG graph with tool usage
builder_b = StateGraph(MessagesState)
builder_b.add_node("agent", agent_node)
builder_b.add_node("tools", ToolNode(tools))
builder_b.add_edge(START, "agent")
builder_b.add_conditional_edges("agent", tools_condition)
builder_b.add_edge("tools", "agent")

agentic_rag_with_tool = builder_b.compile()

png_data = agentic_rag_with_tool.get_graph().draw_mermaid_png()
with open("agentic_rag_pluss_tools_graph.png", "wb") as f:
    f.write(png_data)

def run_agentic_rag(question: str):
    result = agentic_rag_with_tool.invoke(
        {"messages": [HumanMessage(content=question)]}, config={"recursion_limit": 12})
    return result

def print_agentic_rag_results(question, result):
    print("-"*60)
    print("Agentic RAG Results:")
    print("\nQUESTION:", question)
    print("\nFINAL ANSWER:", result["messages"][-1].content)

    print("\nTOOL CALLS:")
    tool_called = False

    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print("-", call["name"], call["args"])
                tool_called = True

    if not tool_called:
        print("None")

if __name__ == "__main__":
    print("-"*60)
    q = ("An AcmeOrbit employee's borrowed laptop loan ended on 2026-10-01. "
        "According to company policy, what is the return deadline date?")
    print("QUESTION:", q)

    print("-"*60)
    print("Invoke Agentic RAG with tools:")
    result = agentic_rag_with_tool.invoke(
        {"messages": [HumanMessage(content=q)]}, config={"recursion_limit": 12})

    print("-"*60)
    print("Run Agentic RAG:")
    result = run_agentic_rag(q)

    print_agentic_rag_results(q, result)