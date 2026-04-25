# Exercise 0x19 - Code Review - Injection

## Objective
Perform a comprehensive analysis of input validation and output-encoding controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Injection Checks

For this exercise, we will be reviewing user data flows along with input validation and output encoding implementations within the open source Bridge Troll application.

Add relevant injection checks from the _generic\_checks.md_ list to the template.

```text
## Injection

### Input Validation
- [ ] Is all input is validated without exception?
- [ ] Do the validation routines check for known good characters and cast to the proper data type (integer, date, etc.)?
- [ ] Is the user data validated on the client or server or both (security should not rely solely on client-side validations that may be bypassed)?
  ...

### Output Encoding
- [ ] Do databases interactions use parameterized queries?
- [ ] Do input validation functions properly encode or sanitize data for the output context?
- [ ] How do framework-provided database ORM functions used?
- [ ] Does the source code use potentially-dangerous ORM functions? (.raw, etc)
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.


### 2. Perform Injection Checks
For this exercise, examine the Bridge Troll code base manually and consider the following vulnerability classes and track down if the code base is flawed.

```text
[ ] SQL Injection - Note the ways the ORM performs raw SQL queries
[ ] Cross-Site Scripting (Reflected)
[ ] Cross-Site Scripting (Stored)
[ ] URL Handling - Redirection
[ ] Server-Side Request Forgery
```

Document all of your findings in _bridge\_troll\_scr.md_.
