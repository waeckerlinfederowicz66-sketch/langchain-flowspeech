from __future__ import annotations

import asyncio
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .client import FlowSpeechClient, FlowSpeechSpeaker


class FlowSpeechTextToSpeechInput(BaseModel):
    text: str | None = Field(default=None, description="Text, or one labelled speaker turn per line.")
    voice_name: str = Field(default="Kore", description="FlowSpeech voice name.")
    speakers: list[FlowSpeechSpeaker] | None = None
    segments: list[dict[str, str]] | None = Field(default=None, description="Explicit speaker/text/voiceName turns.")
    request_id: str | None = Field(default=None, description="UUID to reuse only for an unchanged recording.")
    output_path: str = "flowspeech-output.wav"
    model_config = ConfigDict(extra="forbid")


class FlowSpeechTextToSpeechTool(BaseTool):
    """Generate WAV audio through public API v1."""
    name: str = "flowspeech_text_to_speech"
    description: str = "Generate speech with FlowSpeech and save the completed WAV locally."
    args_schema: Type[BaseModel] = FlowSpeechTextToSpeechInput
    api_key: str | None = Field(default=None, exclude=True, repr=False)
    base_url: str = "https://flowspeech.io"
    timeout: float = 300.0
    _client: FlowSpeechClient | None = PrivateAttr(default=None)

    def _get_client(self) -> FlowSpeechClient:
        if self._client is None:
            self._client = FlowSpeechClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _run(self, text: str | None = None, voice_name: str = "Kore",
             speakers: list[FlowSpeechSpeaker] | None = None,
             output_path: str = "flowspeech-output.wav",
             segments: list[dict[str, str]] | None = None,
             request_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            raise ValueError("Unsupported synthesis options: " + ", ".join(sorted(kwargs)))
        result = self._get_client().generate_speech(text=text, voice_name=voice_name,
                                                  speakers=speakers, segments=segments, request_id=request_id)
        return {"output_path": str(result.save(output_path)), "mime_type": result.mime_type,
                "sample_rate": result.sample_rate, "num_channels": result.num_channels,
                "bits_per_sample": result.bits_per_sample, "quota": None,
                "job_id": result.job_id, "request_id": result.request_id,
                "result_url": result.result_url, "usage": result.usage}

    async def _arun(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._run, *args, **kwargs)
