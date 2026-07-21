import base64

import httpx
import pytest

from langchain_flowspeech import FlowSpeechApiError, FlowSpeechClient, FlowSpeechSpeaker


def test_generate_speech_sends_public_api_shape() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "audioBase64": base64.b64encode(b"RIFFdemo").decode(),
                    "mimeType": "audio/L16;rate=24000",
                    "sampleRate": 24000,
                    "numChannels": 1,
                    "bitsPerSample": 16,
                    "quota": {
                        "limit": 10000,
                        "used": 10,
                        "remaining": 9990,
                        "resetAt": "2026-07-31T15:59:59.999Z",
                        "isGuest": False,
                    },
                },
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        client = FlowSpeechClient(
            api_key="test-key",
            base_url="https://flowspeech.io",
            http_client=http_client,
        )
        result = client.generate_speech(
            text="Speaker A: Hello",
            speakers=[FlowSpeechSpeaker(speaker="Speaker A", voice_name="Kore")],
        )

    assert captured["url"] == "https://flowspeech.io/api/ai/text-to-speech"
    assert captured["auth"] == "Bearer test-key"
    assert '"originalText":"Speaker A: Hello"' in captured["json"]
    assert '"speaker":"Speaker A"' in captured["json"]
    assert result.audio_bytes == b"RIFFdemo"
    assert result.quota is not None
    assert result.quota.remaining == 9990


def test_check_quota() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "quota": {
                        "limit": 100,
                        "used": 25,
                        "remaining": 75,
                        "resetAt": "2026-07-31T15:59:59.999Z",
                        "isGuest": False,
                    }
                },
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = FlowSpeechClient(api_key="test-key", http_client=http_client)
        quota = client.check_quota()

    assert quota.limit == 100
    assert quota.remaining == 75


def test_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FLOWSPEECH_API_KEY", raising=False)

    with pytest.raises(FlowSpeechApiError, match="API key is required"):
        FlowSpeechClient()
