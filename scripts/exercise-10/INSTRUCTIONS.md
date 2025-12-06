# Exercise 0x10 - Testing LLM Outputs
## Objective
Build a Reliable Test Suite for LLM Evaluation

## Instructions
### 1. Open Test Script
Open _exercise-10/agentic\_test.py_ to observe the baseline tests provided.

This test is extremely simplistic and just performs a regex search of the response for the term is_insecure and true.

```py
    # Use regex to assert "is_insecure" is true or True
    assert re.search(r'"is_insecure"\s*:\s*true', response, re.IGNORECASE), \
        "The code should be marked as insecure."
```

While this gives us a simple case to test against, this could be more complete.

Run the script a few times and note the behavior.

```sh
python exercise-10/agentic_test.py
```

### 2. Add Integration Test
To start, create a test that checks for specific security findings and the positive case (hint: verify that is_insecure is false).

You will need to provide a positive case and will have to update the following input_code.

```py
input_code = """
    @login_required
    @user_passes_test(can_create_project)
    def update_user_active(request):
        user_id = request.GET.get('user_id')
        User.objects.filter(id=user_id).update(is_active=False)
    """
```

### 3. Unit Test (Bonus)
LLMs are notoriously bad at generating JSON in their output. Create a unit test that validates JSON or other output structure for correctness.
