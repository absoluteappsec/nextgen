from dotenv import load_dotenv
import os
import git

# LangChain core
from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Your tools
from view_file_tools import ViewFileTool, ViewFileLinesTool
from view_directory_tools import (
    DirectoryListingTool,
    FileListingTool,
    DirectoryStructureTool,
)

load_dotenv()

# ------------------------------------------------------------------------------
# Git Repo Setup
# ------------------------------------------------------------------------------
repo_url = "https://github.com/railsbridge/bridge_troll.git"
repo_path = "./exercise-16a/repo"

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned Bridge Troll into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")


# ------------------------------------------------------------------------------
# LLM + Tools
# ------------------------------------------------------------------------------
LLM = ChatBedrock(
    model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
    model_kwargs={"temperature": 0.6},
)

TOOLS = [
    ViewFileTool(),
    ViewFileLinesTool(),
    DirectoryListingTool(),
    FileListingTool(),
    DirectoryStructureTool(),
]


# ------------------------------------------------------------------------------
# STEP 1: Context Gathering (WITH TOOLS, AGENT-BASED)
# ------------------------------------------------------------------------------
# NOTE FOR STUDENTS:
# Replace the top of CONTEXT_PROMPT_TEMPLATE with your own context-gathering
# instructions. The agent wiring + tools are provided for you.
CONTEXT_PROMPT_TEMPLATE = """You are gathering context about how auditing and logging works
in an application.

The code lives under ./exercise-16a/repo. Use the available tools to explore the
repository and gather simple notes about where and how auditing and logging appears to
be implemented (e.g., policies, controllers, etc.).

User task:
{input}

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a response to say to the Human,
or if you do not need to use a tool,
you MUST use the format:

Thought: Do I need to use a tool? No
Final Answer: [your response here]

Begin!

New input: {input}
{agent_scratchpad}
"""

context_prompt = PromptTemplate.from_template(CONTEXT_PROMPT_TEMPLATE)
context_agent = create_react_agent(LLM, TOOLS, context_prompt)
context_executor = AgentExecutor(
    agent=context_agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True,
)


def _run_context(task: str) -> dict:
    """Run the context-gathering step and wrap output in a dict for LCEL."""
    result = context_executor.invoke({"input": task})
    summary = result.get("output", str(result))
    print("\n[STEP 1 OUTPUT] Context Summary:\n", summary)
    return {"context": summary}


context_step = RunnableLambda(_run_context)


# ------------------------------------------------------------------------------
# STEP 2: Assessment Plan (NO TOOLS, PURE LCEL)
# ------------------------------------------------------------------------------
plan_prompt = ChatPromptTemplate.from_template(
    """You are writing a simple auditing and logging review plan.

Here is the context you gathered in Step 1:
---
{context}
---

Using ONLY this context, write a short, clear plan for reviewing
auditing and logging in this application. Keep it brief and easy to understand.

This plan MUST cover the following points:
- [ ] If an exception occurs, does the application fails securely?
- [ ] Do error messages reveal sensitive application or unnecessary execution details?
- [ ] Are Component, framework, and system errors displayed to end user?
- [ ] Does exception handling that occurs during security sensitive processes release resources safely and roll back any transactions?
- [ ] Are relevant user details and system actions logged?
- [ ] Is sensitive user input flagged, identified, protected, and not written to the logs?
  - [ ] Credit Card #s, Social Security Numbers, Passwords, PII, keys
- [ ] Are unexpected errors and inputs logged?
  - [ ] Multiple login attempts, invalid logins, unauthorized access attempts
- [ ] Are log details should be specific enough to reconstruct events for audit purposes?
  - [ ] Are logging configuration settings configurable through settings or environment variables and not hard-coded into the source?
- [ ] Is user-controlled data validated and/or sanitized before logging to prevent log injection?

In your plan, start with a line like:
"This plan is based on the context gathered in Step 1 above."
"""
)

plan_step = (
    # Log exactly what context is being passed from Step 1 into Step 2
    RunnableLambda(
        lambda state: (
            print(
                "\n[STEP 1 OUTPUT → STEP 2 INPUT] Context:\n", state.get("context", "")
            ),
            state,
        )[1]
    )
    | plan_prompt
    | LLM
    | StrOutputParser()
    | RunnableLambda(lambda text: {"plan": text})
)


# ---------------------------------------------------------------------------
# STEP 3: Review (WITH TOOLS, AGENT-BASED)
# ---------------------------------------------------------------------------
REVIEW_PROMPT_TEMPLATE = """You are performing a in-depth auditing and logging review of
the app under ./exercise-16a/repo.

You have the following basic security assessment plan that you are going to
review now (this is the output of Prompt 2 / Step 2):

--- BEGIN ASSESSMENT PLAN FROM STEP 2 ---
{input}
--- END ASSESSMENT PLAN FROM STEP 2 ---

Follow this plan at a high level. Use tools to inspect all relevant
files or directories that seem related to auditing and logging. Then return
simple, high-level findings.

In your Final Answer, FIRST include a short line like:
"I used the assessment plan from Step 2 above to decide what to review."

After that line, do the following in order:

1) Print a short heading like "Plan from Step 2 used for this review:".
2) Immediately echo the full plan text you received (verbatim), so that it is
   clear to the reader what plan you followed.
3) Then, in a separate paragraph, briefly describe what you actually reviewed
   (which files/directories/policies) and what you found.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a response to say to the Human,
or if you do not need to use a tool,
you MUST use the format:

Thought: Do I need to use a tool? No
Final Answer: [your response here]

Begin!

New input: {input}
{agent_scratchpad}
"""

review_prompt = PromptTemplate.from_template(REVIEW_PROMPT_TEMPLATE)
review_agent = create_react_agent(LLM, TOOLS, review_prompt)
review_executor = AgentExecutor(
    agent=review_agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True,
)


def _run_review(state: dict) -> str:
    """Run the review step based on the plan from step 2.

    Expects a dict with a "plan" key from the previous LCEL step.
    """

    plan_text = state.get("plan", "")
    print("\n[STEP 2 OUTPUT → STEP 3 INPUT] Assessment Plan:\n", plan_text)
    result = review_executor.invoke({"input": plan_text})
    output = result.get("output", str(result))
    print("\n[STEP 3 OUTPUT] Review Findings:\n", output)
    return output


review_step = RunnableLambda(_run_review)


# ---------------------------------------------------------------------------
# FULL LCEL PIPELINE: task -> context -> plan -> review
# ---------------------------------------------------------------------------
full_chain = (
    RunnableLambda(lambda task: task)  # start from a plain string task
    | context_step
    | plan_step
    | review_step
)


def run_auditing_chain(task: str):
    print("\n🚀 Running 3-Step LCEL Auditing & Logging Chain...\n")
    result = full_chain.invoke(task)
    print("\n==============================")
    print("FINAL RESULT:\n", result)
    return result


if __name__ == "__main__":
    task = (
        "You are an expert code reviewer and application security auditor. Your task is to learn how auditing and logging functions work in the Bridge Troll application"
        "and perform an auditing and logging security review for possible gaps. Utilize all three steps of the LCEL framework to complete this task."
    )

    run_auditing_chain(task)
