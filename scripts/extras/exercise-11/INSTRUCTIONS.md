# Exercise 0x11 - Code Review - Application Overview & Risk Assessment

## Objective
Gather initial context about the application, what it does, how it does it, and what risks we should be thinking about to start our code review.

## Instructions
### 1. Pull down code to analyze
For this exercise, we will be looking at an open source project known as _BHIMA_

```sh
git clone https://github.com/third-culture-software/bhima
```

### 2. Start notes
Make a fresh copy of the _/data/scr_template.md_ file.

```sh
cp data/scr_template.md bhima_scr.md
```

Start the code review by retrieving the latest commit number for BHIMA.

```sh
% cd bhima
% git rev-parse HEAD
28253bf29eef295d5b2e95cfaf240c9169b92378
```

Record the commit number into _bhima\_scr.md_
```text
We assessed commit `#28253bf29eef295d5b2e95cfaf240c9169b92378`
``` 

### 3. Behavior
Open up the BHIMA _README.md_ file and start by filling out the behavior analysis section of the code review template. Limit your time to a few minutes and what can be quickly gleaned from the README.

```text
## Behavior

* What does it do? (business purpose)
* Who does it do this for? (internal / external customer base)
* What kind of information will it hold?
* What are the different types of roles?
* What aspects concern your client/customer/staff the most?
```

### 4. Tech Stack
Now move on to the Tech Stack section of the template, utilize any information from README and open up packages.json for more possibilities.

```text
## Tech Stack

* Framework & Language
* 3rd party components, Examples:
  * Building libraries
  * External Depedencies
  * JavaScript widgets
* Datastore
```

### 5. Brainstorming / Risks
This is all about creativity. Given what you know of the application's purpose and tech stack, fill in 3-4 risks that are apparent. This is a free-form exercise, so anything goes from personnel attacks (e.g. phishing, password theft) to technical vulnerabilities (outdated packages).

```text
## Brainstorming / Risks

* Here is what the feature or product is supposed to do... what might go wrong?
* Okay - based on the tech stack, I've realized that the:
  * ...
```