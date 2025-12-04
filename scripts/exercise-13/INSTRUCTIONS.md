# Exercise 0x13 - Code Review - Information Gathering

## Objective
Dig deeper into the source code to uncover various coding patterns and techniques that help build understanding of the application architecture. Specifically, we want to understand the application data flow and how user interactions happen.

## Instructions
### 1. Pull down code to analyze
For this exercise, we will be adding a new project to the list that is purpose-built.

```sh
git clone https://github.com/absoluteappsec/skea_node
```

### 2. Start notes
Make a fresh copy of the _/data/scr_template.md_ for the _skea\_node_ application.

```sh
cp data/scr_template.md skea_node_scr.md
```

Start the code review by retrieving the latest commit number for BHIMA.

```sh
% cd skea_node
% git rev-parse HEAD
28253bf29eef295d5b2e94cfaf240c9169b92378
```

Record the commit number into _skea\_node\_scr.md_
```md
We assessed commit `#28253bf29eef295d5b2e94cfaf240c9169b92378`
``` 

### 3. Behavior/Tech Stack/Risk Analysis
Open up the skea_node _README.md_ file and start by filling out the Behavior, Tech Stack, and Risk Analysis sections of the code review template. Limit your time to a few minutes and what can be quickly gleaned from looking at the code base.

```text
## Behavior
...
## Tech Stack
...
## Brainstorming / Risks
```

### 4. Information Gathering - Route Mapping
This exercise (and portion of the code review methodology) is focused on identifying data flows coming into the application. For the *skea_node* application, start by looking in the _app.js_ file.

```javascript
var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var isAuthenticated = require('./auth.js')

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
...
```

This contains a few interesting patterns, including use of alternate files for both the `indexRouter` and `usersRouter`.

The _routes/index.js_ file gives us the first route (`/`) we need to copy into our notes:

```js
var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

module.exports = router;
```

Document this GET request to `/` in the _Mapping / Routes_ section of the template.

```text
## Mapping / Routes

- [ ] `GET / routes/index.js`
```

Continue this process for all routes in the application.

### 5. BHIMA Route Mapping
Once you have completed mapping routes for *skea_node*, switch to *BHIMA*. Since this is a large open source application, we will prioritize authentication routes for this exercise.

To identify BHIMA's authentication routes and controller files, start by combing through the _server/config/routes.js_ source and search for `login`.

```js
  // auth gateway
  app.post('/auth/login', auth.login);
  app.get('/auth/logout', auth.logout);
  app.post('/auth/reload', auth.reload);
```

Identify the affected controllers and document your findings in the template.