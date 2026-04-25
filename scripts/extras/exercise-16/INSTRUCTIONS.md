# Exercise 0x16 - Code Review - Authorization Checks

## Objective
Perform a comprehensive analysis of authorization controls, identifying any vulnerabilities or flaws in the targeted code base.

## Instructions
### 1. Add Authorization Checks

For this exercise, we will be reviewing authorization controls within the open source Bridge Troll application.

Add relevant authorization checks from the _generic\_checks.md_ list to the template.

```text
- [ ] Identify Roles
- [ ] Identify sensitive/privileged endpoints
- [ ] Identify authz expectations specific to the business purpose of the app
  * Can non-privileged users view, add, or alter accounts?
  * Is there functionality to add accounts with higher access levels than their own access?
  * How is separation of duties handled?
- [ ] Identify Authorization functions/filters
  * Do they take Tokens? Cookies? Custom or handled by a framework?
  ...
```

Make sure and curate this list to the checks that are valid for the code base being reviewed. Not all checks are appropriate.


### 2. Perform Authorization Checks
For this exercise, examine the Bridge Troll code base manually and consider the following vulnerability classes and track down if the code base is flawed.

* Insecure Direct Object Reference
* Privilege Escalation, Mass Assignment
* Cross-Site Request Forgery
* Sensitive Data Exposure

Document all of your findings in _bridge\_troll\_scr.md_.
