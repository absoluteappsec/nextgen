# Exercise 0x05 - Chatbot Assistant
## Objective
Create a chatbot assistant that provides developers with organization-specific security advice. 

## Instructions
### 1. Create Vector Database
Open _exercise-05/load\_guide.py_ and view the steps to parsing a PDF into a vector database for a chatbot to query.

The initial script focuses only on the _Acme\_Co\_Security\_Guide.pdf_. Familiarize yourself with the content to determine how well the chatbot does is maintaining focus and sticking to the provided script.

Alternatively, find another guide (like the latest OWASP Top 10 PDF) and utilize that as the knowledgebase for your chatbot.

Build the vector database
```sh
python exercise-05/loadguide.py
```

### 2. Run Chatbot
Review and run the _chatbot.py_ script. Ask specific questions related to the content from the _Acme\_Co\_Security\_Guide.pdf_. Specifically, the chatbot is instructed to as follows: 

```py
chat_template = """
[...]

If you are not absolutely certain about a response which should only come
from the context, reply "I am sorry please reach out to the security team directly."

[...]
"""
```

Run and interact with the chatbot:

```sh
python exercise-05/chatbot.py
```

Given the above instruction, if the user's question is outside of the provided guide, the chatbot should respond with "I am sorry, please reach out to the security team directly." How easy (or hard) is it to get responses outside of the context provided in the PDF?

### 3. Implement Guardrails
Use your knowledge of prompt engineering to limit the chatbot to data contained in the provided context. What prompt engineering techniques would be effective to limit these interactions? _Hint: Reflexion may be useful here._

### 4. Bypass Prompt Injection
One of the instructors has attempted to prevent prompt injection based on risks identified by a client in the _chatbot\_prompti\_prevention\_example.py_ script. Review the protections and attempt to bypass these restrictions.