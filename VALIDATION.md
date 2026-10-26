# Validation: langchain-flowspeech 0.2.0

Date: 2026-10-26. Validation was performed in an isolated migration checkout.

## Commands and results

- Initial state: clean local clone on codex/public-api-v1; no user changes overwritten.
- Python 3.12.14; httpx 0.28.1, pytest 8.4.2, pydantic 2.12.3, langchain-core 1.0.1.
- Source: .venv/bin/python -m pytest -q --basetemp=.test-tmp -> 95 passed (0.57s).
- Build: .venv/bin/python -m build --no-isolation -> wheel and sdist succeeded.
- Backend/tooling: hatchling 1.27.0, build 1.3.0, twine 6.2.0.
- Metadata: .venv/bin/python -m twine check dist/*.whl dist/*.tar.gz -> both PASSED.
- Installed wheel with pip --no-index --no-deps --force-reinstall.
- Wheel suite: .venv/bin/python -m pytest -q -o pythonpath= --basetemp=.test-tmp -> 95 passed (0.58s).
- Import origins explicitly verified under .venv/lib/python3.12/site-packages, not src.
- API/tool sync + async behavior, legacy dialogue mapping, usage/quota semantics and unknown tool options covered.
- .venv/bin/python -m pip check -> no broken requirements.
- git diff --check -> clean.

Initial combined dependency installation encountered incompatible LangChain/Dify
Pydantic/packaging constraints; resolved using separate virtual environments.
Only binary dependency wheels were installed. No unreviewed source install hooks
were executed. Network sandbox denial was resolved through the approved dependency
download escalation. The original server workspace was read-only.

## Artifacts

- dist/langchain_flowspeech-0.2.0-py3-none-any.whl: 13155 bytes, 8 members
  SHA-256: 1a7e9f1352bf20a0047a16ee074892974604dc89b468cac45a46a65428bc1af2
- dist/langchain_flowspeech-0.2.0.tar.gz: 18977 bytes, 16 members
  SHA-256: 4fcc5c3b5f88a00155b2bda09a6b95c5d364f03fcdc0c4b156ceda34dda03e2f

scripts/verify_artifacts.py verified metadata/version, archive path safety, member
allowlists and secret patterns. No secret-pattern matches or unintended runtime
files were found. No .env, .git, virtualenv, cache, executable tooling or reference
wheel is included. Wheels were built from the generated sdists by python-build.

The three vendored v1 adapters are byte-identical:
e17b79351d7e32627db9aa9e05c2ac7a09d22432f7b5a290f7ff0461fa9d3966

## Coverage

- Single and multi-speaker request mapping; rejection of legacy model/source/speed/format/speakers fields.
- Bearer authentication only on API requests; stable UUID and byte-identical body across transport/429/retryable-503 retries.
- Quota, voices, request-ID recovery lookup, job status and cancellation.
- queued -> running -> merging -> settling -> success; 200 replay; failed/cancelled terminal jobs.
- Retry-After seconds and HTTP dates; rate-limited polling; bounded retries.
- Missing/mismatched UUIDs, unknown status, malformed metadata/usage, deleted or absent results, nested API errors.
- Invalid credentials/configuration; HTTPS and embedded-credential checks; refused API redirects.
- Credential-free audio redirects even with intentionally polluted injected auth/headers/cookies.
- Size-bounded downloads, invalid/truncated WAV, download retries without a second create request.
- Total deadline before waiting, capped request budgets, real-time slow transport and slow streamed download deadlines.
- Socket connect/connect_ex blocked automatically in every test. All generated audio is a synthetic local WAV fixture.

## Remaining limitations

No production generation, paid credits, real API credentials, upstream pushes, package
publication, email or PR modification were used. Public metadata/archive downloads
were read-only. No end-to-end production generation is claimed.
The configured local deadline stops the caller waiting; a single in-flight HTTP
request can finish cleanup afterward. It cannot submit a retry or another recording.
An accepted server job may continue and should be recovered with its original UUID.

The source contract currently returns subscription while the migration contract
names entitlement. The adapters preserve the top-level payload and LangChain maps
either field. This was verified by reading the original server, without modifying it.

## Changed files

- .gitignore
- README.md
- docs/langchain/flowspeech.mdx
- pyproject.toml
- src/langchain_flowspeech/client.py
- src/langchain_flowspeech/tools.py
- src/langchain_flowspeech/_v1.py
- tests/test_client.py
- tests/test_tools.py
- tests/test_v1_contract.py
- tests/conftest.py
- scripts/verify_artifacts.py
- CHANGELOG.md
- RELEASE.md
- VALIDATION.md

Generated dist/, local .venv/.tools, synthetic test outputs and artifact extraction
directories are ignored and not source changes. No commits or upstream writes
were made. See RELEASE.md for exact coordinator release steps.
