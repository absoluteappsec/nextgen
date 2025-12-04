# Exercise 1

## Objective
Familiarize yourself with different prompt engineering frameworks through implementation and replacement within the provided script.

The goal of the provided script is to query security information from the vector database previously generated from code for the open source Juice Shop project and to find out as much information about the application as possible.

## Instructions
### 1. Familiarize yourself with the prompt in the provided script
Open _exercise-01/prompt\_engineering.py_ and browse to the prompt.

```python
system_prompt_template = """
Analyze source code and provide detailed security and functional insights as requested.

Code for analysis:
{context}
"""
```
AND
```python
user_question = """
Tell me about the application, its functionality, libraries and framworks, and any potential security issues you can identify from the codebase provided in the context.
"""
```

### 2. Prompt Output
First, observe that the current prompt is ambiguous and not well defined. The lack of definition gives the LLM flexibility to be creative but results in a different answer each time we run the script. Since this prompt is not setup as a chat bot, run it 2 or 3 times and compare the answers.

Command:
```sh
python exercise-01/prompt_engineering.py
```
Output:
```text
Based on the code snippets provided, here's a comprehensive analysis of the OWASP Juice Shop application:

Application Overview:
- OWASP Juice Shop is an intentionally insecure web application designed for security training and awareness
- It's an open-source project hosted by OWASP, developed to demonstrate various web application security vulnerabilities
- Written primarily in TypeScript/Angular for frontend and Node.js/Express for backend
- Purposefully includes multiple security flaws to educate developers and security professionals
...
```

### 3. Manual Prompt Change
Think about the discussion on well-structured prompts and various frameworks. Change both the `system_prompt_template` and `user_question` instructions to a defined AI role and discrete task that you would like to accomplish.

For example:
```python
system_prompt_template = """
You are a expert security code review analyst, with experience analyzing all types of source code for security vulnerabilities. You are meticulous about confirming technical details with code-backed justifications. Query the provided source code and provide detailed insights as requested.

Code for analysis:
{context}
"""

user_question = """
Analyze the provided application and provide a detailed list of its purpose, functionality, and security impacting libraries and framworks. Identify possible potential security issues you can identify from the codebase provided in the context.
"""
```

Run the script a couple more times and compare the output with the previous prompt and question.

```sh
python exercise-01/prompt_engineering.py
```

### 4. Utilize a defined prompt
Defining the role and task gets us closer to the output we desire, but may also introduce additional creativity and unexpected output. Let's take one of the pre-defined framework scripts and compare the output. Copy the content of _prompts/2-ape.txt_ into both the `system_prompt_template` and `user_question` variable.

Run the script again and compare the output with the previous prompt and question. The APE example neglects defined roles and output is still fuzzy, so attempt to fix that in subsequent runs.

```sh
python exercise-01/prompt_engineering.py
```

### 5. Prompt Experimentation
There are a few examples of different prompt framworks (APE, RACE, COSTAR, Reflexion) in the _prompts_ folder. Review (and maybe run) each of them to compare output. For example, test out placement of the prompt layout in both the system prompt vs. the user question.

To complete this exercise, have the LLM output results in the following format:
```text
1. Application Overview
OWASP Juice Shop is an intentionally insecure web application designed as a comprehensive security training and awareness tool. Developed using modern web technologies, it serves as an educational platform for demonstrating and exploring various web application security vulnerabilities. The application simulates an e-commerce juice shop environment, allowing users to interact with products, create accounts, and perform various actions while intentionally incorporating security flaws that can be discovered and exploited during security testing and training.

2. Key Functionalities
- User Registration and Authentication: Allows users to create accounts, log in, and manage profile settings
- Product Browsing and Ordering: Enables users to view, select, and purchase juice products
- Photo Wall/Memory Sharing: Provides a feature for users to upload and share images with captions
- Two-Factor Authentication: Offers optional enhanced account security through 2FA setup
- Challenge and Score Tracking: Includes a scoring system for identifying and solving security challenges

3. Libraries and Frameworks Used
- Angular: Primary frontend framework for building the single-page application
- Express.js: Backend web application framework for Node.js
- RxJS: Reactive programming library for handling asynchronous operations
- Material Design: UI component library for consistent design and interactions
- NGX-Translate: Internationalization library for multi-language support

4. Potential Security Issues
- Broken Authentication: Multiple authentication-related vulnerabilities, including weak password policies and potential session management issues
- Cross-Site Scripting (XSS): Insufficient input validation and sanitization could allow script injection in user-controlled fields
- Insecure File Upload: The photo wall feature may lack proper file type and size validation, potentially enabling malicious file uploads
- Improper Access Controls: Potential authorization bypass vulnerabilities in user profile and administrative functions
- Security Misconfiguration: Intentional security flaws designed to demonstrate common configuration-related risks, which could be exploited in real-world scenarios

The application is explicitly designed to showcase security vulnerabilities, making it an excellent educational tool for cybersecurity professionals and developers to understand and learn about web application security risks.
```
