# Validator

## Local Compatibility Check

```shell
uv run grader/grade.py
```

## Notes

- The grader is driven by `grader/spec.py`.
- This validator is driven by `grader/spec.py`.
- The repository includes only the published checks.
- The validator is useful for catching import errors, interface errors, and benchmark-case mistakes before shipping changes.
- Additional internal checks are not included in this repository, so local output should be treated as a compatibility signal rather than exhaustive certification.
