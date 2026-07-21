import base64

import httpx

from langchain_flowspeech.client import FlowSpeechClient
from langchain_flowspeech.tools import FlowSpeechTextToSpeechTool


def test_tool_saves_audio(tmp_path) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "audioBase64": base64.b64encode(b"RIFFtool").decode(),
                    "mimeType": "audio/L16;rate=24000",
                    "sampleRate": 24000,
                    "numChannels": 1,
                    "bitsPerSample": 16,
                },
            },
        )

    output_path = tmp_path / "speech.wav"
    tool = FlowSpeechTextToSpeechTool(api_key="test-key")
    tool._client = FlowSpeechClient(
        api_key="test-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = tool.invoke({"text": "Hello from FlowSpeech", "output_path": str(output_path)})

    assert output_path.read_bytes() == b"RIFFtool"
    assert result["output_path"] == str(output_path)
    assert result["sample_rate"] == 24000
