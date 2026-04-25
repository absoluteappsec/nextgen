# Exercise 0x17 - Code Review - Authentication Checks

## Objective
Perform a comprehensive analysis of authentication controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Authentication Checks

For this exercise, we will be reviewing authentication controls within the open source Bridge Troll application.

Add relevant authentication checks from the _generic\_checks.md_ list to the template.

```text
## Authentication

- [ ] What are the different authentication flows?
  - [ ] User Login
  - [ ] User Registration
  - [ ] Forgot Password
- [ ] How are users identified? What information do they have to provide?
  - [ ] Username, email, password, 2fa token, etc.
- [ ] Does the application implement strong password policies?
  ...
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.


### 2. Perform Authorization Checks
For this exercise, examine the Bridge Troll code base manually and consider the following vulnerability classes and track down if the code base is flawed.

```text
[ ] User/Email enumeration
[ ] Session Hijack
[ ] Authentication Bypass
[ ] Privilege Assignment
[ ] Session Token Generation
```

Document all of your findings in _bridge\_troll\_scr.md_.
