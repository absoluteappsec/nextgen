# Exercise 0x14 - Code Review - Information Gathering / Authorization Functions

## Objective
Identify all authorization decorators and patterns within a targeted code base.

## Instructions
### 1. Pull down code to analyze
For this exercise, we will be adding an open source project known as Bridge Troll.

```sh
git clone https://github.com/railsbridge/bridge_troll
```

### 2. Start notes
Make a fresh copy of the _/data/scr_template.md_ for the _bridge\_troll_ application.

```sh
cp data/scr_template.md bridge_troll_scr.md
```

Start the code review by retrieving the latest commit number for BHIMA.

```sh
% cd bridge_troll
% git rev-parse HEAD
18253bf28eef295a5b2f94cfaf240c9169b92378
```

Record the commit number into _skea\_node\_scr.md_
```md
We assessed commit `#18253bf28eef295a5b2f94cfaf240c9169b92378`
``` 

### 3. Behavior/Tech Stack/Risk Analysis
As in previous exercises, fill out all of the relevant details for the Behavior, Tech Stack, and Risk Analysis sections.

Utilize AI scripts to perform this analysis to speed up the process. Spot check the findings and make adjustments as necessary.

### 4. Route Mapping
Before we get to authorization functions, identify the data flows coming into the application. Utilize previous context to find correct files.

### 5. Identify Authorization Functions
Now that you have completed mapping routes, move to authorization functions checklist. Answer the following questions to determine whether the analyzed function is an authorization function.

1. Identify the unique values used to identify an actor:
  * Sessions
  * API Tokens
  * Basic Authentication
  * JWTs
  * Something… else? 
2. Identify the purpose of the function:
  * Is it checking for user identity?
    * Authentication Check
  * Is it looking for a specific role? 
    * Role-Based Access Control (RBAC)
  * Is it doing some sort of HMAC verification for events?
    * Cross-Site Request Forgery (CSRF)

Document your findings under the `Mapping / Authorization Decorators` section of the template.

```text
## Mapping / Authorization Decorators

- [ ] `ensure_logged_in`
- [ ] `is_authenticated()`
```

Turn to the internet if you can't determine these functions for Bridge Troll.

# Exercise 0x14a - AIxCode Review - Authorization Functions

## Objective
Build an Agentic AI Tool to browse through application source and identify all authorization functions utilized by an application.

## Instructions
Utilize a pattern based on agentic tools previously seen and build out a new tool or tools that browses through a code base and identifies authorization functions. Hint, this could be command-line scripts, vector databases, or any other mechanism that makes sense.