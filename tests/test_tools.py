import asyncio

import pytest
from pydantic import ValidationError

from langchain_flowspeech.tools import FlowSpeechTextToSpeechTool
from test_client import wrap
from test_v1_contract import JOB, REQUEST, factory, job, response, wav_bytes


@pytest.mark.parametrize("asynchronous", [False, True])
def test_tool_saves_audio(factory, tmp_path, asynchronous):
    core, _, _, _ = factory([response(job())])
    tool = FlowSpeechTextToSpeechTool()
    tool._client = wrap(core)
    output = tmp_path / "speech.wav"
    data = {"text": "Hello", "output_path": str(output), "request_id": REQUEST}
    result = asyncio.run(tool.ainvoke(data)) if asynchronous else tool.invoke(data)
    assert output.read_bytes() == wav_bytes()
    assert result["job_id"] == JOB and result["request_id"] == REQUEST
    assert result["mime_type"] == "audio/wav" and result["quota"] is None


def test_tool_rejects_obsolete_options():
    with pytest.raises(ValidationError):
        FlowSpeechTextToSpeechTool().invoke({"text": "Hi", "speed": 2})
