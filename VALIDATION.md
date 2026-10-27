# Validation: langchain-flowspeech 0.2.1

Fresh local run on 2026-10-27 with Python 3.12.14. This section applies only
to the 0.2.1 candidates below; historical 0.2.0 results are preserved separately.

- Source suite: 205 passed.
- Fresh extracted-sdist suite: 205 passed.
- Installed-wheel suite with pytest source paths disabled: 205 passed.
- Installed import and distribution-metadata checks resolved to the fresh wheel
  target and confirmed version 0.2.1, not an editable or source checkout.
- Built a fresh sdist and built the wheel from that sdist using build 1.3.0 and
  hatchling 1.27.0. Twine 6.2.0 checks passed for both archives.
- Exact archive-member allowlists, wheel RECORD hashes, package/source byte
  equality, credential patterns, private paths, identity strings and public API
  terminology checks passed. No old active endpoint was found. Legacy URL
  literals in rejection tests were classified explicitly as negative fixtures.
- Tests used synthetic WAV data and mock transports; autouse fixtures blocked
  socket connections. No production calls, paid generation or credentials used.

## Candidate SHA-256

- dist/langchain_flowspeech-0.2.1-py3-none-any.whl:
  7f9114792a9c6758eda625c0bb47d08cd037bd4004a82002dadfc2bc79a73fa2
- dist/langchain_flowspeech-0.2.1.tar.gz:
  0ecfc1779d91690c54ce8dc5ec163da5428898897ad21efffd65d419a01b18e1

Full commands, logs, member hashes and import proofs are in the coordinator's
verification-0_2_1-run3 evidence directory. python-handoff.json records final source
manifests and publication gates. Earlier failed local runs remain available as
diagnostic evidence, not as final validation. VALIDATION.md itself is deliberately
outside the sdist allowlist; README, CHANGELOG and RELEASE instructions are included.

## Remaining Gates

No commit, push, tag, workflow dispatch or publication was performed. The coordinator
must authorize each remote write separately, confirm registry availability, review
workflow trigger and artifact-consistency risks, verify final source/artifact hashes,
and obtain passing remote CI for supported Python versions. Local execution covered
Python 3.12 only. Do not infer remote CI or publication success from these checks.

# Historical Validation: 0.2.0

The record below is preserved verbatim and is not evidence for 0.2.1.

# Validation: langchain-flowspeech 0.2.0

Date: 2026-10-26. Final release-gate follow-up in an isolated migration checkout.
Both source and actual final artifacts pass 165 tests (previous baseline 95).
The final archives supersede all earlier local 0.2.0 candidates.

## Commands and results

- Python 3.12.14; httpx 0.28.1 and pytest 8.4.2. LangChain core 1.0.1, pydantic 2.12.3.
- Source: .venv/bin/python -m pytest -q --basetemp=.test-tmp/release-gate-ids
  -> 165 passed (0.64s).
- .venv/bin/python -m build --no-isolation -> sdist and wheel-from-sdist succeeded.
- Build tools: hatchling 1.27.0, build 1.3.0, twine 6.2.0.
- .venv/bin/python -m twine check dist/*.whl dist/*.tar.gz -> both PASSED.
- .venv/bin/python scripts/verify_artifacts.py dist/*.whl dist/*.tar.gz -> passed.
- .venv/bin/python -m pip install --no-index --no-deps --force-reinstall dist/*.whl
  -> final rebuilt wheel installed locally; no dependency downloads.
- .venv/bin/python -m pytest -q -o pythonpath= --basetemp=.test-tmp/release-final-wheel
  -> 165 passed (0.61s).
- Import origins explicitly verified under site-packages, not src. Installed
  adapter SHA-256 equals the reviewed source.
- .venv/bin/python -m pip check -> no broken requirements.
- git diff --check -> passed.
- Sync and async tool regressions preserve IDs on malformed WAV and write no file.

## Final artifacts

- dist/langchain_flowspeech-0.2.0-py3-none-any.whl: 13777 bytes, 8 members
  SHA-256: 2d7e9fecba7bf660da093ea351858f9c90e6c4d9df8b24b8899648d704625add
- dist/langchain_flowspeech-0.2.0.tar.gz: 22560 bytes, 18 members
  SHA-256: 3dce57f7ce7031d5c115b39e8fc892b433a12ec5b8610c68243d91b220384a5f

Archive inspection verified version metadata, safe member paths, forbidden
development files, secret patterns and private local path leakage. No matches
or unintended runtime files were found. Final artifact code was tested, not
only source. VALIDATION.md is intentionally excluded from these archives.

## Release-gate coverage

- 37 shared WAV tests cover RIFF length/chunk/padding bounds, PCM tag 1, 24000 Hz,
  mono 16-bit, block alignment 2, byte rate 48000, nonempty even data length,
  duplicate/missing format or data chunks, malformed extensions, ancillary chunks,
  every truncation offset and deadline checks during parsing.
- Malformed audio raises typed invalid_audio, keeps request/job/result recovery
  identifiers and cannot trigger another create or audio retry.
- 31 shared identifier tests require a valid requestId on submission, polling,
  lookup and cancellation; reject mismatches and normalize both expected and
  returned UUIDs before comparison. Successful results always contain requestId.
- Existing coverage includes single/multi input mapping, legacy-option rejection,
  stable idempotency/body retries, every pending and terminal status, result deletion,
  quota/voices, recovery, cancellation, API errors, Retry-After and total deadlines.
- Downloads are bounded and credential-free even with polluted injected clients
  and redirects. API redirects are refused. Slow transport/stream tests verify
  the caller's absolute deadline.
- Socket connect/connect_ex are blocked automatically in every test. HTTP uses
  fake transports; audio fixtures are locally synthesized, never production output.

## Shared adapter

All three source copies and their installed/extracted artifact copies are identical.

- Adapter SHA-256: f1e49e7eb2915eb7e796ab869d364e02c5987de8347b07aafef381b5a5764ade
- tests/test_wav_validation.py SHA-256: 36bd7ebfd01c0ffe389ecd42747abcee74576d24a4e704b15e75fa93721afbcc
- tests/test_job_identifiers.py SHA-256: cd6e76f062472482094cc3c7dfc004b033e58a00250a4c948192b5edd182ff80

The adapter and these tests are stable for reuse in the separately owned SDK.
No SDK or MCP files were changed by this worker.

## Contract verification

The original server was read-only. public-api.ts normalizes UUIDs, and
the job serializer always emits requestId. The WAV storage code emits
PCM 24000 Hz mono16, block alignment 2 and byte rate 48000. The quota response
contains subscription and limits alongside quota; entitlement is only an optional
compatibility alias, not a required field.

## Safety and limitations

No production requests, credentials, paid generation, email, commits, pushes,
publication or workflow/OIDC changes were made by this worker. Existing changes
were preserved. No end-to-end production verification is claimed.
A single in-flight HTTP request may finish cleanup after the local caller deadline;
it cannot submit a retry or another recording. Recover accepted jobs with their
original request/job UUID instead of submitting new input.

## Preserved release state

HEAD remains 42bfcf0554e1fad3a5b51488012271b1081f7b7b on codex/public-api-v1.
The coordinator's existing commit and reported pushed branch were preserved.
These release-gate changes are uncommitted; review and commit them separately,
then run CI before publishing. This worker did not commit or push.

## Changed files in this follow-up (10)

- src/langchain_flowspeech/_v1.py
- tests/test_wav_validation.py
- tests/test_job_identifiers.py
- tests/test_tools.py
- docs/langchain/flowspeech.mdx
- README.md
- CHANGELOG.md
- RELEASE.md
- VALIDATION.md
- scripts/verify_artifacts.py

Earlier migration files remain in place; this list only describes this release-gate
follow-up. Generated dist/, test outputs, environments and artifact extractions
are ignored build outputs. See RELEASE.md for coordinator-only release steps.
Confirm registry version availability and upload only the reviewed final hashes.
