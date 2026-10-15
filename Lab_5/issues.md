# Static Code Analysis Issues

This document records issues found in the original `movie_reviews.py` during static analysis with Pylint, Bandit, and Flake8, along with the fixes applied.

| # | Tool | Original issue | Severity | Fix applied |
|---|---|---|---|---|
| 1 | Bandit | `B324`: MD5 was used to generate a review identifier. MD5 is not suitable for security-sensitive hashing. | High | Replaced `hashlib.md5` with `hashlib.sha256`. The identifier remains a deterministic demo ID, not an authentication token. |
| 2 | Bandit | `B104`: The stream host was set to `0.0.0.0`, which binds to all network interfaces. | Medium | Changed `STREAM_HOST` to `127.0.0.1` so the demo binds to the local machine only. |
| 3 | Bandit | `B105`: A hard-coded moderator password (`reviews-demo`) was present in the source code. | Low | Removed the unused hard-coded password constant. No password is needed by this demonstration. |
| 4 | Bandit | `B311`: The standard `random` module was used to select the featured movie. | Low | Replaced `random.choice` with `secrets.choice` to avoid Bandit's use-of-non-cryptographic-randomness warning. |
| 5 | Pylint | The module and functions lacked docstrings, and function/parameter names did not follow `snake_case`. | Code quality | Added a module docstring and function docstrings; renamed functions and parameters to `snake_case`. |
| 6 | Pylint | `featured` was flagged for not following constant naming conventions, and `pickFeatured` used a global variable. | Code quality | Removed the global `featured` variable; `pick_featured()` now returns the selected movie directly. |
| 7 | Pylint | An unnecessary `else` followed a `return` in `averageRating`, and a `range(len(...))` loop was used. | Code quality | Simplified the conditional return and used `enumerate()` to iterate through movie titles. |
| 8 | Flake8 | Formatting violations included missing whitespace around an operator, insufficient blank lines before a function, insufficient spacing before an inline comment, and missing whitespace after a comma. | Style | Reformatted the affected lines to comply with Flake8's style checks. |
| 9 | `rate_movie` robustness | A rating for a title not present in the movie collection could cause a key lookup error. | Reliability | Added a check for missing movie titles and return `False` after printing a helpful message. |
| 10 | `pick_featured` robustness | Choosing a featured movie from an empty collection could raise an exception. | Reliability | Added an empty-collection check; the function returns `None` if there are no movies. |

## Verification after fixes

- **Pylint:** `10.00/10` (previous score: `5.47/10`).
- **Bandit:** No issues identified; 0 high, 0 medium, and 0 low severity findings.
- **Flake8:** The after-report file is empty, which indicates no Flake8 violations were reported.

## Notes

The original Bandit findings were recorded as one high-severity issue, one medium-severity issue, and two low-severity issues. The Pylint and Flake8 findings were primarily code-quality and formatting issues. The additional robustness fixes prevent errors for unknown movie titles and an empty movie collection.
