# Exercise 0x18 - Code Review - Auditing Checks

## Objective
Perform a comprehensive analysis of auditing controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Auditing Checks

For this exercise, we will be reviewing auditing and logging controls within the open source Bridge Troll application.

Add relevant auditing/logging checks from the _generic\_checks.md_ list to the template.

```text
## Auditing

- [ ] If an exception occurs, does the application fails securely?
- [ ] Do error messages reveal sensitive application or unnecessary execution details?
- [ ] Are Component, framework, and system errors displayed to end user?
- [ ] Does exception handling that occurs during security sensitive processes release resources safely and roll back any transactions?
- [ ] Are relevant user details and system actions logged?
  ...
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.


### 2. Perform Auditing/Logging Checks
For this exercise, examine the Bridge Troll code base manually and consider the following vulnerability classes and track down if the code base is flawed.

```text
[ ] Cryptographic Failures - Passwords and Session Tokens
[ ] Error Handling
[ ] Debug Messages
[ ] Log Injection
```

Document all of your findings in _bridge\_troll\_scr.md_.
