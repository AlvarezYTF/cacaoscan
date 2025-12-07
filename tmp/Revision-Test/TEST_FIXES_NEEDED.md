# Test Fixes Needed

## Critical Issues

### 1. training_tasks TypeError
**Error**: `TypeError: train_model_task() takes 3 positional arguments but 4 were given`

**Root Cause**: When calling Celery tasks with `bind=True`, we need to properly unwrap the function and pass arguments correctly.

**Solution**: Use consistent pattern:
```python
# Get the wrapped function (may need multiple levels)
original_func = train_model_task
while hasattr(original_func, '__wrapped__'):
    original_func = original_func.__wrapped__

# Call with self as first argument
result = original_func(mock_task, 'job-id', config_dict)
```

### 2. test_log_user_registration_without_request
**Error**: `AssertionError: assert False`

**Fix**: Verify that the LoginHistory record is actually created. May need to check the correct field names.

### 3. fincas_app management commands
- `test_validate_sql_identifier_invalid`: Regex pattern mismatch
- `test_handle_correct_foreign_key`: StopIteration error

### 4. reports views
- Logger AttributeError
- HTTP status code mismatches (500 vs 200)

### 5. training commands
- KeyError: 'hybrid'
- CommandError issues
- Pickling errors

## Next Steps

1. Fix training_tasks TypeError by ensuring consistent unwrapping pattern
2. Fix registration service assertion
3. Fix fincas commands
4. Fix reports views
5. Fix training commands

