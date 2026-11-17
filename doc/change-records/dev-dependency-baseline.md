# Optional development dependency baseline

The published dev extra now requires `ruff>=0.17.5`,
`pytest-asyncio>=1.5.0` and `mypy>=2.4.1`, excluding versions below the
checked development baseline. The other four development floors, runtime
requirements and lockfiles are unchanged.

The development guide distinguishes the checked, reproducible hash lock
from `.[dev]`, whose lower bounds permit newer allowed releases.

At prepared revision `a0e12e6568b9c03c470d5fece5aa1e5839afc0fe`,
wheel/sdist builds, Twine and existing documentation checks passed.
Both artifact formats contain exactly the three new `Requires-Dist`
minima with `extra=dev`; the other seven requirements and all 22 runtime
files match the original base. Retained Ruff `Requires-Python` metadata
(`>=3.7`) and pytest-asyncio/Mypy metadata (`>=3.10`) fit the unchanged
project minimum (`>=3.11`). These focused developer packaging checks do
not establish final-head canonical or independent-review acceptance.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>
