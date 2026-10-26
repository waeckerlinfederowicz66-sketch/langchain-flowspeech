# Changelog

## 0.2.0 - 2026-10-26

- Migrate from legacy synchronous generation to public API v1 submit, poll and download.
- Add stable UUID idempotency, bounded retries, Retry-After, total deadlines and recovery IDs.
- Map single and explicit multi-speaker input; reject obsolete options and malformed responses.
- Validate success/deleted states, WAV metadata and downloaded audio; bound download sizes.
- Isolate download credentials across HTTPS redirects; reject API redirects.
- Update quota/voices handling, subscription requirements and error diagnostics.
- Add fake-transport contract tests and distribution verification.
- Support sync invoke and async ainvoke/agenerate_speech; retain local base64 compatibility.

The 0.2.0 release assets are prepared locally. Publication is a separate coordinator action.

