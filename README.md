# langchain-flowspeech

`langchain-flowspeech` provides LangChain tools for generating text-to-speech audio with [FlowSpeech](https://flowspeech.io/).

FlowSpeech is a context-aware text-to-speech service for human-like narration with emotion control, pause control, and multi-speaker voice configuration.

## Installation

```bash
pip install langchain-flowspeech
```

## Authentication

Create a FlowSpeech API key in your FlowSpeech account, then export it:

```bash
export FLOWSPEECH_API_KEY="..."
```

Do not commit API keys, cookies, session tokens, or provider credentials.

## Usage

```python
from langchain_flowspeech import FlowSpeechTextToSpeechTool

tool = FlowSpeechTextToSpeechTool()

result = tool.invoke({
    "text": "Welcome to FlowSpeech. This audio is generated from a LangChain tool.",
    "voice_name": "Kore",
    "output_path": "flowspeech-demo.wav",
})

print(result["output_path"])
print(result["mime_type"])
print(result["quota"])
```

## Multi-Speaker Speech

```python
from langchain_flowspeech import FlowSpeechSpeaker, FlowSpeechTextToSpeechTool

tool = FlowSpeechTextToSpeechTool()

result = tool.invoke({
    "text": "Speaker A: We can make this sound natural.\nSpeaker B: Great, let's use different voices.",
    "speakers": [
        FlowSpeechSpeaker(speaker="Speaker A", voice_name="Kore"),
        FlowSpeechSpeaker(speaker="Speaker B", voice_name="Puck"),
    ],
    "output_path": "conversation.wav",
})
```

## API Surface

The package uses the public FlowSpeech API:

- `GET /api/ai/text-to-speech/quota`
- `POST /api/ai/text-to-speech`

Responses include base64-encoded audio and metadata such as MIME type, sample rate, channel count, bit depth, and quota information.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest
```

## Publishing

This project is ready for PyPI packaging. Build locally with:

```bash
python -m pip install build
python -m build
```

For GitHub Actions trusted publishing, configure a PyPI trusted publisher for `waeckerlinfederowicz66-sketch/langchain-flowspeech`, then add a publishing workflow with `id-token: write`.

## Safety

This repository intentionally contains no secrets. Tests use mocked HTTP responses.
