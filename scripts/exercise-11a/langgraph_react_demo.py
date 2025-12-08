from langchain.agents import create_react_agent, AgentExecutor
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import git

# Import our custom tools
from view_file_tools import ViewFileTool, ViewFileLinesTool
from view_directory_tools import (
    DirectoryListingTool,
    FileListingTool,
    DirectoryStructureTool,
)

# TODO: Import your custom tool here
# from my_custom_tool import MyCustomTool


# Load environment variables
load_dotenv()

repo_url = "https://github.com/third-culture-software/bhima.git"
repo_path = "./repo"

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains a git repository.")
else:
    try:
        repo = git.Repo.clone_from(repo_url, repo_path)
        print(f"Repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")

# Define tools and LLM
tools = [
    ViewFileTool(),
    ViewFileLinesTool(),
    DirectoryListingTool(),
    FileListingTool(),
    DirectoryStructureTool(),
    # TODO: Add your custom tool here
    # MyCustomTool(),
]

llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.6},
)


# Define instructions and prompt
instructions = """
You are an agent designed to gather information about an application for security assessment planning.
The application source code is located at ./repo/

Your goal is to collect information in three key areas (from the security assessment template):

## 1. Behavior
Understand what the application does by answering:
- What does it do? (business purpose)
- Who does it do this for? (internal / external customer base)
- What kind of information will it hold?
- What are the different types of roles?
- What aspects concern client/customer/staff the most?

## 2. Tech Stack
Identify the technology components:
- Framework & Language (e.g., Rails/Ruby, Django/Python, mux/Golang, Node.js/Express, Angular/React)
- 3rd party components (building libraries, JavaScript widgets, webhook-dependent applications)
- Datastores (Postgresql, MySQL, Memcache, Redis, MongoDB, etc.)

## 3. Brainstorming / Risks
Brainstorm about potential concerns (NOT specific vulnerability finding):
- What are potential failure modes for this feature/product?
- What technology-specific risks should we think about?
  (e.g., "ORM might have SQLi risks", "template language might have XSS risks")
- General security concerns to explore later

NOTE: This is information gathering and brainstorming, NOT vulnerability scanning.
You are collecting context to understand the application before deeper security analysis.

### Process
1. Explore the repository to understand the codebase structure
2. Read documentation (README, package files, config files) to understand the app
3. Collect factual information about behavior and tech stack
4. Brainstorm potential risk areas to investigate

### **TOOLS**
You have access to file viewing and directory listing tools.

TODO: You can add your own custom tool here to enhance information gathering.

### **Output Format**
Your final response must be in JSON format with these fields:
- `behavior`: (object) What the app does, users, data types, roles, concerns
- `tech_stack`: (object) Frameworks, 3rd party components, datastores identified
- `brainstorming`: (array) List of potential risk areas and concerns to explore

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human,
or if you do not need to use a tool,
you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Your Final Answer should be in JSON format with these fields:

- behavior: (object) with keys: purpose, users, data_types, roles, concerns
- tech_stack: (object) with keys: framework_language, third_party_components, datastores
- brainstorming: (array) list of potential risk areas and security concerns to explore

Begin!

New input: {input}
{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(instructions)

# Create agent and executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)


# Simple LangGraph integration
from langgraph.graph import StateGraph, END
from typing import TypedDict


class AgentState(TypedDict):
    input: str
    output: str


def agent_node(state: AgentState) -> AgentState:
    """Run the ReAct agent via LangGraph node"""
    result = agent_executor.invoke({"input": state["input"]})
    return {"input": state["input"], "output": result["output"]}


# Create simple LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Compile the graph
langgraph_app = workflow.compile()


def analyze_application_with_langgraph(input_task: str) -> dict:
    """Analyze application using LangGraph wrapper around ReAct agent"""
    final_state = None
    for event in langgraph_app.stream({"input": input_task}, stream_mode="values"):
        print("[LangGraph stream event]", event)
        final_state = event

    return final_state


if __name__ == "__main__":
    print("🚀 Security Assessment Information Gathering Demo")
    print("=" * 50)

    # Task for autonomous information gathering
    analysis_task = """This is demo context for a LangGraph ReAct security assessment walkthrough.\n\nGather information about the application in ./repo/ by collecting:
    1. Behavior - What does it do, who uses it, what data does it handle, what roles exist, what are the main concerns?
    2. Tech Stack - What frameworks, languages, 3rd party components, and datastores are being used?
    3. Brainstorming - What potential risk areas and security concerns should we think about for this type of application?

    Start by exploring the directory structure, reading README files, package.json or requirements files, and configuration files.
    Focus on GATHERING INFORMATION, not finding specific vulnerabilities."""

    # LangGraph wrapped ReAct agent
    print("\n\n🔄 LangGraph ReAct Agent:")
    langgraph_result = analyze_application_with_langgraph(analysis_task)
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    print(langgraph_result)
