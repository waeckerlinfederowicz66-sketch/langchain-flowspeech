from __future__ import annotations

from pathlib import Path
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from langchain_flowspeech.client import FlowSpeechClient, FlowSpeechSpeaker


class FlowSpeechTextToSpeechInput(BaseModel):
    text: str = Field(description="Text or speaker-labelled dialogue to synthesize.")
    voice_name: str = Field(default="Kore", description="Default FlowSpeech voice name.")
    speakers: list[FlowSpeechSpeaker] | None = Field(
        default=None,
        description="Optional explicit speaker-to-voice assignments for dialogue.",
    )
    output_path: str = Field(
        default="flowspeech-output.wav",
        description="Local path where the generated WAV audio should be saved.",
    )


class FlowSpeechTextToSpeechTool(BaseTool):
    """LangChain tool that generates speech audio with FlowSpeech."""

    name: str = "flowspeech_text_to_speech"
    description: str = (
        "Generate human-like text-to-speech audio with FlowSpeech and save it as a WAV file."
    )
    args_schema: Type[BaseModel] = FlowSpeechTextToSpeechInput

    api_key: str | None = Field(default=None, exclude=True)
    base_url: str = "https://flowspeech.io"
    timeout: float = 80.0

    _client: FlowSpeechClient | None = PrivateAttr(default=None)

    def _get_client(self) -> FlowSpeechClient:
        if self._client is None:
            self._client = FlowSpeechClient(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    def _run(
        self,
        text: str,
        voice_name: str = "Kore",
        speakers: list[FlowSpeechSpeaker] | None = None,
        output_path: str = "flowspeech-output.wav",
        **_: Any,
    ) -> dict[str, Any]:
        result = self._get_client().generate_speech(
            text=text,
            voice_name=voice_name,
            speakers=speakers,
        )
        saved_path = result.save(output_path)
        return {
            "output_path": str(Path(saved_path)),
            "mime_type": result.mime_type,
            "sample_rate": result.sample_rate,
            "num_channels": result.num_channels,
            "bits_per_sample": result.bits_per_sample,
            "quota": result.quota.model_dump(by_alias=True) if result.quota else None,
        }

    async def _arun(self, *_: Any, **__: Any) -> dict[str, Any]:
        raise NotImplementedError("FlowSpeechTextToSpeechTool currently supports sync use.")
