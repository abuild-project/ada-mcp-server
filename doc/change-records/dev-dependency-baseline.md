# Optional development dependency baseline

The published dev extra now requires `ruff>=0.17.5` and
`pytest-asyncio>=1.5.0`, excluding older versions below the checked development baseline.
The other five development floors, runtime requirements and lockfiles are
unchanged.

The development guide distinguishes the checked, reproducible hash lock
from .[dev], whose lower bounds permit newer allowed releases.

At prepared revision `b7741ee94175a5dc664df5b88b6005b546e720b7`,
wheel/sdist builds, Twine and existing documentation checks passed.
Both artifact formats contain the new Requires-Dist entries for extra=dev;
other requirements and runtime payloads match the base. Retained Ruff
and pytest-asyncio Requires-Python metadata (>=3.7 and >=3.10) fit the
unchanged project minimum >=3.11. These are focused developer packaging
checks; final-head canonical and independent-review acceptance is separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>
