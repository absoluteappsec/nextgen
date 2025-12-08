# Exercise 0x12 - AIxCode Review - AI-Enabled Application Overview & Risk Assessment

## Objective
Instead of performing the App Overview and Risk Assessment activities manually, utilize AI to both gather and summarize this information based on limited available resources.

## Instructions
### 1. Basic Example
For this exercise, we will be running the included scripts to analyze the README provided by Juice Shop.

Start by opening the _exercise-12/readme\_ingestion.py_ script and looking at the retrieval mechanism and prompt.

```py
# Stream the output in chunks for a chat-like experience
    for chunk in chain.stream({
        "question":"You are being provided the README file from a software project. Please provide a summary of the purpose of the application and any other relevant details you can think to share.", 
        "context": doc
    }):
        print(chunk, end="", flush=True)
```

Run the script to get a picture of what AI will tell us with the above prompt.

```sh
python exercise-12/readme_ingestion.py
```

Note that the initial respond _may not_ reflect the details we want for our application overview and risk assessment. Change the question to ask for the information in the source code review template (either pull the list directly from the template use the larger question and output from the _prompt-advanced.txt_ file). 

### 2. Advanced Example
The README provides limited information about the application and isn't always sufficient for our needs. Instead of relying just on that single source, let's expand out to code snippets and other useful data.

We will accomplish this by cloning the repository, creating a vectorized database of specific files, and querying the database about those files.

Open the _exercise-12/profile\_app.py_ script and review both data retrieval, vectorization, and prompt.

```py
for chunk in chain.stream(
    """Tell me the following information about the code base I am providing to you:
- What is the main purpose of the application?
- Web technologies used in the application?
- Any security concerns you can identify based on the code provided?
    """
    ):
    print(chunk, end="", flush=True)
```

Run the script to get a picture of what AI will tell us with the above prompt.

```sh
python exercise-12/profile_app.py
```

As in the basic example, this prompt is lacking structure. Utilize the examples from the secure code review template or the _prompt-advanced.txt_ file to improve the prompt. Run the script to refine the output.

### 3. Real World Code
Now that we've tried this against Juice Shop, change up the target to pull down and run the same analysis against BHIMA.

Replace the link to the Juice Shop README in _readme\_ingestion.py_ to the following:
```python
README_URL = 'https://raw.githubusercontent.com/third-culture-software/bhima/refs/heads/master/README.md'
```

Compare the results to your own manual analysis.

Now replace the repository link in _profile\_app.py_ with BHIMA. Alternatively, you could point the `local_path` repository to the previously downloaded BHIMA repository.
```python
repo_url = 'https://github.com/third-culture-software/bhima.git'
```

Compare the results of README to full code analysis.

