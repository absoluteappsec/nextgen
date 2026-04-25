# Exercise 0x21 - Code Review - Configuration Review

## Objective
Perform a comprehensive analysis of security configuration controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Configuration Review Checks

For this exercise, we will be reviewing framework and middleware configuration settings within the open source Bridge Troll application.

Add relevant injection checks from the _generic\_checks.md_ list to the template.

```text
## Configuration Review
- [ ] What are the interesting files used to configure the application and components?
- [ ] Are any endpoints enabled through configurations properly protected with authentication and authorization?
- [ ] Are security protections implemented in framework properly configured?
- [ ] Does the target language and framework version have any known security issues?
- [ ] Are configuration-controlled security headers implemented according to recommended best practices?
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.

If you are unfamiliar with the main framework or any middlewarae utilized by the application, ask ChatGPT or another LLM to help identify possible security issues.


### 2. Perform Cryptographic Review
For this exercise, examine the Bridge Troll code base manually and consider the following configuration issues.

```text
[ ] Vulnerable and Outdated Components
[ ] Password Complexity Settings
[ ] Session Expiration
```

Document all of your findings in _bridge\_troll\_scr.md_.
