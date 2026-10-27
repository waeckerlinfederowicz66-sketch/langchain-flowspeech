import asyncio
import json

import pytest

from langchain_flowspeech import FlowSpeechClient, FlowSpeechSpeaker
from test_v1_contract import JOB, REQUEST, factory, job, response, wav_bytes


def wrap(client):
    return FlowSpeechClient(api_key="test-only", http_client=client._client, download_client=client._download,
                            clock=client.clock, sleep=client.sleep)


def test_sync_client_legacy_dialogue(factory):
    core, calls, _, _ = factory([response(job())])
    result = wrap(core).generate_speech(text="Alice: Hello\nBob: Welcome", request_id=REQUEST,
        speakers=[FlowSpeechSpeaker(speaker="Alice"), FlowSpeechSpeaker(speaker="Bob", voice_name="Puck")])
    assert result.audio_bytes == wav_bytes() and result.job_id == JOB
    assert calls[0].headers["User-Agent"] == "flowspeech/0.2.1"
    assert result.quota is None and result.usage["chargedCredits"] == 5
    assert json.loads(calls[0].content)["input"]["segments"] == [
        {"speaker": "Alice", "text": "Hello", "voiceName": "Kore"},
        {"speaker": "Bob", "text": "Welcome", "voiceName": "Puck"}]


def test_async_client(factory):
    core, _, _, _ = factory([response(job())])
    result = asyncio.run(wrap(core).agenerate_speech(text="Hi", request_id=REQUEST))
    assert result.audio_bytes == wav_bytes()


def test_quota_preserves_new_fields(factory):
    core, _, _, _ = factory([response({"quota": {"remaining": 10, "reserved": 2, "available": 8},
                                      "subscription": {"plan": "basic"}, "limits": {"pending": 2}})])
    result = asyncio.run(wrap(core).acheck_quota())
    assert result.available == 8 and result.reserved == 2
    assert result.entitlement == {"plan": "basic"} and result.limits == {"pending": 2}


@pytest.mark.parametrize("kwargs", [
    {"text": "Hello", "original_text": "Different"},
    {"text": "No label", "speakers": [FlowSpeechSpeaker(speaker="A")]},
    {"text": "A: Hi", "speakers": [FlowSpeechSpeaker(speaker="A"), FlowSpeechSpeaker(speaker="A")]},
    {"text": "Hello", "speed": 2},
])
def test_unsupported_legacy_inputs_are_not_silently_dropped(factory, kwargs):
    core, calls, _, _ = factory([])
    with pytest.raises((ValueError, TypeError)):
        wrap(core).generate_speech(**kwargs)
    assert not calls
