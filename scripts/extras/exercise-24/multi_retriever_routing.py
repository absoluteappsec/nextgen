"""
Exercise 24: LCEL Multi-Retriever Routing

Demonstrates using an LLM to decide which vector store retriever to query
based on the user's question. Two FAISS retrievers are loaded:

  1. acmeco_sec_guide — Acme Co's security policy document (PDF)
  2. vtm_code         — VTM Django application source code

The LLM classifies each question, a RunnableBranch routes to the correct
retriever, and the answer is generated from the retrieved context.
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
)
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(SCRIPT_DIR, "..", "..", "..", "vector_databases")

# ------------------------------------------------------------------------------
# LLM & Embeddings
# ------------------------------------------------------------------------------
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.2,
)

embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

# ------------------------------------------------------------------------------
# Load the two FAISS vector stores
# ------------------------------------------------------------------------------
print("Loading vector stores...")

policy_db = FAISS.load_local(
    os.path.join(VECTOR_DB_DIR, "acmeco_sec_guide.faiss"),
    embeddings,
    allow_dangerous_deserialization=True,
)
policy_retriever = policy_db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 10},
)

code_db = FAISS.load_local(
    os.path.join(VECTOR_DB_DIR, "vtm_code.faiss"),
    embeddings,
    allow_dangerous_deserialization=True,
)
code_retriever = code_db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 10},
)

print("  - acmeco_sec_guide (security policy docs)")
print("  - vtm_code (Django application source)")

# ------------------------------------------------------------------------------
# Step 1: LLM-based classifier — decides which retriever to use
# ------------------------------------------------------------------------------
classify_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a query router. Given a user question, decide which knowledge "
            "base is most relevant. Reply with ONLY one of these two words:\n\n"
            "  policy — for questions about security policies, compliance, standards, "
            "guidelines, organizational rules, incident response procedures, or "
            "approved tools and processes.\n\n"
            "  code — for questions about source code, vulnerabilities in code, "
            "Django views, models, URLs, authentication implementation, or how "
            "the application works.\n\n"
            "Reply with a single word: policy or code",
        ),
        ("human", "{question}"),
    ]
)

classify_chain = (
    classify_prompt | llm | StrOutputParser() | (lambda x: x.strip().lower())
)

# ------------------------------------------------------------------------------
# Step 2: RunnableBranch routes to the correct retriever
# ------------------------------------------------------------------------------


def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def retrieve_policy(input_dict):
    docs = policy_retriever.invoke(input_dict["question"])
    print(f"  [Router] -> policy retriever ({len(docs)} docs)")
    return format_docs(docs)


def retrieve_code(input_dict):
    docs = code_retriever.invoke(input_dict["question"])
    print(f"  [Router] -> code retriever ({len(docs)} docs)")
    return format_docs(docs)


retriever_branch = RunnableBranch(
    (lambda x: x["topic"] == "policy", RunnableLambda(retrieve_policy)),
    RunnableLambda(retrieve_code),  # default: code
)

# ------------------------------------------------------------------------------
# Step 3: Classify, retrieve, answer
# ------------------------------------------------------------------------------
answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an application security engineer. Answer the question using "
            "ONLY the provided context. If the context does not contain enough "
            "information, say so.\n\n<context>\n{context}\n</context>",
        ),
        ("human", "{question}"),
    ]
)


def classify_and_retrieve(input_dict):
    question = input_dict["question"]
    topic = classify_chain.invoke({"question": question})
    print(f"  [Classifier] question classified as: {topic}")
    context = retriever_branch.invoke({"question": question, "topic": topic})
    return {"context": context, "question": question}


full_chain = (
    RunnableLambda(classify_and_retrieve) | answer_prompt | llm | StrOutputParser()
)

# ------------------------------------------------------------------------------
# Interactive chat
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Multi-Retriever Routing Demo")
    print("=" * 60)
    print("Ask about security POLICY or application CODE.")
    print("The LLM decides which knowledge base to query.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ")
            if question.strip().lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            if not question.strip():
                continue

            print()
            for chunk in full_chain.stream({"question": question}):
                print(chunk, end="", flush=True)
            print("\n")

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
