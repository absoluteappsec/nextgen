# Exercise 0x15a - Multi-Step Authorization Assessment with LCEL

## Objective
Build a **three-step LCEL (LangChain Expression Language) workflow** that chains simple prompts together to perform an authorization-focused security review.

The goal is for you (the student) to **edit and improve the prompts**, not the wiring. The code demonstrates how to:

- Take an initial task input.
- Run a **context-gathering step** (with tools) to learn about how authorization works in an application.
- Use that context to generate a **security assessment plan** (no tools needed here).
- Use that plan in a final **review step** (with tools) to perform a lightweight authorization review.

## Files

- `lcel_authorization_chain_demo.py` – Main LCEL demo script for exercise 16a
- `view_file_tools.py` – File viewing tools (same as exercise 11a)
- `view_directory_tools.py` – Directory/directory-structure tools (same as exercise 11a)

## What You Will Change

You will primarily edit **three prompts** in `lcel_authorization_chain_demo.py`:

1. **Context Gathering Prompt**
   - Currently a **very basic boilerplate** like "this is a context gathering prompt".
   - You should turn this into a focused prompt that gathers context about **authorization** in the target application.
   - This step can (and should) use the file/directory tools to explore the codebase.

2. **Assessment Plan Prompt**
   - Takes the output of the context-gathering step and produces a **security assessment plan** focused on authorization.
   - This is also simple boilerplate and meant to be replaced.

3. **Review Prompt**
   - Uses the assessment plan to perform a **lightweight authorization review**.
   - This step again has access to the file/directory tools, so it can inspect relevant files.

Keep the prompts **simple but explicit**. The purpose of this exercise is to understand **how LCEL chains steps together**, not to produce perfect prompts.

## How the LCEL Chain Works (High-Level)

The demo script wires three steps together:

1. **Step 1: Context Gathering (with tools)**
   - Input: a high-level task (e.g., "understand how authorization works in this app").
   - Runs an agent-like step that can call:
     - `view_file`
     - `view_file_lines`
     - `list_directories`
     - `list_files`
     - `show_directory_structure`
   - Output: a simple text summary of authorization-related context.

2. **Step 2: Authorization Assessment Plan (no tools)**
   - Input: the context output from Step 1.
   - Output: a simple plan (text) describing how you would assess authorization for this app.

3. **Step 3: Review (with tools)**
   - Input: the plan from Step 2.
   - Runs another agent-like step that can **again use the same tools** to look at the repository.
   - Output: a lightweight review result (again, simple text for the purposes of the exercise).

All three are wired together using **LCEL composition**, so that:

- Output of Step 1 feeds into Step 2.
- Output of Step 2 feeds into Step 3.

## Your Tasks

1. Run the demo script:

   ```sh
   python exercise-15a/lcel_authorization_chain_demo.py
   ```

2. Open `lcel_authorization_chain_demo.py` and:

   - **Rewrite the context-gathering prompt** so it does a good job of understanding authorization in the target app.
   - **Rewrite the assessment plan prompt** so it produces a concrete, structured plan.
   - **Rewrite the review prompt** so it uses the plan to drive a lightweight code review, calling the tools where helpful.

3. (Optional) Adjust how the chain is composed:

   - Add small transformations (e.g., extracting only certain fields from intermediate outputs).
   - Add additional intermediate prompts or steps.

## Key Concept

The main point of this exercise is to help you **learn LCEL** as a way to wire together multi-step, agentic workflows.

- Keep the prompts simple.
- Focus on how data flows from **context → plan → review**.
- Observe how the same tools are reused in Steps 1 and 3.
