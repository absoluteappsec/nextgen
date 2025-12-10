from dotenv import load_dotenv
import os
import git

from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Reuse the same simple file/directory tools from exercise-11a
from view_file_tools import ViewFileTool, ViewFileLinesTool
from view_directory_tools import (
    DirectoryListingTool,
    FileListingTool,
    DirectoryStructureTool,
)


# Load environment variables
load_dotenv()


# Bridge Troll repository (authorization-focused Rails app)
# NOTE: This script is intended to be run from the ./scripts directory.
# We therefore store the repo under the exercise-16a folder so it stays
# scoped to this exercise: ./scripts/exercise-16a/repo
repo_url = "https://github.com/railsbridge/bridge_troll.git"
repo_path = "./exercise-16a/repo"

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains the Bridge Troll git repository.")
else:
    try:
        repo = git.Repo.clone_from(repo_url, repo_path)
        print(f"Bridge Troll repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the Bridge Troll repository: {e}")


# Shared tools and LLM
TOOLS = [
    ViewFileTool(),
    ViewFileLinesTool(),
    DirectoryListingTool(),
    FileListingTool(),
    DirectoryStructureTool(),
]

LLM = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.5},
)


# ---------------------------------------------------------------------------
# STEP 1: Context Gathering (with tools)
# ---------------------------------------------------------------------------
# NOTE FOR STUDENTS:
# Replace the *top* part of CONTEXT_GATHERING_PROMPT with your own
# authorization-focused context gathering instructions. Keep it simple and
# focused. The ReAct / tool-calling boilerplate at the bottom should stay.
# ---------------------------------------------------------------------------
CONTEXT_GATHERING_PROMPT = """This is a context gathering prompt.

You are learning about how authorization works in an application.
Use tools to explore the code under ./exercise-16a/repo and gather simple notes
about where and how authorization seems to be implemented.

User task: {input}

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

context_prompt = PromptTemplate.from_template(CONTEXT_GATHERING_PROMPT)
context_agent = create_react_agent(LLM, TOOLS, context_prompt)
context_executor = AgentExecutor(
    agent=context_agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True,
)


def _run_context(task: str) -> str:
    """Run the context-gathering step and return a simple text summary."""
    result = context_executor.invoke({"input": task})
    # AgentExecutor returns a dict; we expect a main "output" field.
    return result.get("output", str(result))


context_step = RunnableLambda(_run_context)


# ---------------------------------------------------------------------------
# STEP 2: Authorization Assessment Plan (no tools)
# ---------------------------------------------------------------------------
# NOTE FOR STUDENTS:
# Replace the text in ASSESSMENT_PLAN_PROMPT with your own plan-generation
# instructions. It should take the raw context from step 1 and turn it into
# a short, clear plan for an authorization-focused security assessment.
# ---------------------------------------------------------------------------
ASSESSMENT_PLAN_PROMPT = """You are writing a very simple security assessment plan.

The following text is context gathered about how authorization works in an
application:

---
{context}
---

Based only on this context, write a short, basic plan for how you would
review authorization in this application. Keep it brief and easy to read.
"""

plan_prompt = PromptTemplate.from_template(ASSESSMENT_PLAN_PROMPT)
plan_parser = StrOutputParser()


def _wrap_context_for_plan(context_text: str) -> dict:
    return {"context": context_text}


plan_step = RunnableLambda(_wrap_context_for_plan) | plan_prompt | LLM | plan_parser


# ---------------------------------------------------------------------------
# STEP 3: Review Step (with tools)
# ---------------------------------------------------------------------------
# NOTE FOR STUDENTS:
# Replace the text in REVIEW_PROMPT with your own review instructions.
# It should use the assessment plan from step 2 and, when helpful, call
# tools to look at the code under ./exercise-16a/repo to perform a lightweight review.
# ---------------------------------------------------------------------------
REVIEW_PROMPT = """This is a very simple review prompt.

You are performing a lightweight authorization review of the application
under ./exercise-16a/repo.

You have the following basic security assessment plan that you are going
to review now (this is the output of Prompt 2 / Step 2):

--- BEGIN ASSESSMENT PLAN FROM STEP 2 ---
{input}
--- END ASSESSMENT PLAN FROM STEP 2 ---

Follow this plan at a high level. Use tools to inspect a few relevant
files or directories that seem related to authorization. Then return
simple, high-level findings.

In your Final Answer, FIRST include a short line like:
"I used the assessment plan from Step 2 above to decide what to review."

After that line, briefly describe what you actually reviewed (which
files/directories/policies) and what you found.

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

review_prompt = PromptTemplate.from_template(REVIEW_PROMPT)
review_agent = create_react_agent(LLM, TOOLS, review_prompt)
review_executor = AgentExecutor(
    agent=review_agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True,
)


def _run_review(plan_text: str) -> str:
    """Run the review step based on the plan from step 2."""
    result = review_executor.invoke({"input": plan_text})
    return result.get("output", str(result))


review_step = RunnableLambda(_run_review)


# ---------------------------------------------------------------------------
# FULL LCEL CHAIN: context -> plan -> review
# ---------------------------------------------------------------------------
full_chain = context_step | plan_step | review_step


def run_authorization_chain(task: str) -> str:
    """Run the full three-step LCEL chain for a given task string.

    This function calls each LCEL step explicitly so students can see
    where each prompt runs and what it produced.

    Steps:
    1) Context gathering (with tools)
    2) Assessment plan (no tools)
    3) Review (with tools)
    """

    print("\n--- STEP 1: Context Gathering (Prompt 1 Output) ---")
    context_text = context_step.invoke(task)
    print(context_text)

    print("\n--- STEP 2: Assessment Plan (Prompt 2 Output) ---")
    plan_text = plan_step.invoke(context_text)
    print(plan_text)

    print("\n--- STEP 3: Review (Prompt 3 Output) ---")
    review_text = review_step.invoke(plan_text)
    print(review_text)

    return review_text


if __name__ == "__main__":
    print("🚧 Exercise 16a - LCEL Authorization Chain Demo")
    print("=" * 60)

    demo_task = (
        "This is demo context: learn how authorization appears to work in the "
        "Bridge Troll application and perform a simple authorization review."
    )

    final_result = run_authorization_chain(demo_task)

    print("\n" + "=" * 60)
    print("FINAL RESULT (Step 3 Output):")
    print(final_result)
