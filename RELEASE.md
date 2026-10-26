# Release 0.2.0

## Coordinator steps

1. Review source changes, CHANGELOG.md and VALIDATION.md.
2. Confirm 0.2.0 is still unpublished on PyPI; 0.1.0 must not be overwritten.
3. Re-run the offline suite: python -m pytest -q.
4. Build with reviewed hatchling==1.27.0 and build==1.3.0:
   python -m build --no-isolation
5. Check metadata: python -m twine check dist/*.whl dist/*.tar.gz.
6. Install the wheel in an isolated environment and re-run tests against that
   installed package (override pytest pythonpath to exclude src).
7. Inspect wheel/sdist members and verify SHA-256 checksums from VALIDATION.md.
8. Only the coordinator may commit/tag/push and upload the reviewed artifacts:
   python -m twine upload dist/*.whl dist/*.tar.gz
   Use trusted publishing or a separately supplied PyPI credential; never put it
   in source, shell history, documentation or logs.

## Safety gates

No production API key or paid generation was used. Do not enable live generation
during routine packaging tests. Do not include .env, credentials, virtualenvs,
caches, tool executables, downloaded reference wheels or private content in releases.
Review VALIDATION.md for exact results and remaining integration limitations.

Preserve the existing 0.1.0 publication. Release 0.2.0 only after final coordinator
review of source, artifacts, registry availability and account authorization.
The worker has not pushed commits, published packages or changed any upstream PR.

The inspected server currently returns subscription where the migration contract
names entitlement; the adapters preserve/accept both. Confirm current public docs
and release notes with the coordinator. This does not affect generation.

## Reproducible tests

All network calls in the test suite are fake httpx transports. An autouse fixture
blocks socket connect/connect_ex, so a missing mock cannot consume credits.
The adapter is vendored independently in these three integrations; any future
contract fix must be applied to all copies and their matching contract tests.

