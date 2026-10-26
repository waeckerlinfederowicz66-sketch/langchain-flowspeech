from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._v1 import ApiError, V1Client, make_input

FlowSpeechApiError = ApiError


class FlowSpeechSpeaker(BaseModel):
    """Legacy dialogue assignment; use explicit segments for arbitrary dialogue."""
    speaker: str | None = None
    voice_name: str = "Kore"
    model_config = ConfigDict(extra="forbid")

    def to_api(self) -> dict[str, str]:
        return {"voiceName": self.voice_name, **({"speaker": self.speaker} if self.speaker else {})}


class FlowSpeechQuota(BaseModel):
    remaining: float
    reserved: float
    available: float
    entitlement: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None
    # Legacy fields remain readable but are not supplied by v1.
    limit: int | None = None
    used: int | None = None
    reset_at: str | None = Field(default=None, alias="resetAt")
    is_guest: bool | None = Field(default=None, alias="isGuest")
    model_config = ConfigDict(populate_by_name=True)


class FlowSpeechTtsResult(BaseModel):
    """Downloaded WAV, encoded locally for the historical audio_base64 interface."""
    audio_base64: str = Field(alias="audioBase64")
    mime_type: str = Field(default="audio/wav", alias="mimeType")
    sample_rate: int = Field(default=24000, alias="sampleRate")
    num_channels: int = Field(default=1, alias="numChannels")
    bits_per_sample: int = Field(default=16, alias="bitsPerSample")
    quota: FlowSpeechQuota | None = None
    job_id: str
    request_id: str
    result_url: str
    usage: dict[str, Any]
    model_config = ConfigDict(populate_by_name=True)

    @property
    def audio_bytes(self) -> bytes:
        return base64.b64decode(self.audio_base64, validate=True)

    def save(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(self.audio_bytes)
        return output_path


def speech_input(text, voice_name, speakers, segments, original_text):
    if original_text is not None and original_text != text:
        raise ValueError("original_text is no longer supported unless equal to text")
    if segments is not None:
        if speakers:
            raise ValueError("Use segments or speakers, not both")
        return make_input(text, voice_name, segments)
    if not speakers:
        return make_input(text, voice_name)
    assignments = [FlowSpeechSpeaker.model_validate(s) for s in speakers]
    if len(assignments) == 1 and not assignments[0].speaker:
        return make_input(text, assignments[0].voice_name)
    voices = {}
    for assignment in assignments:
        if not assignment.speaker or assignment.speaker in voices:
            raise ValueError("Dialogue speakers require unique nonempty labels")
        voices[assignment.speaker] = assignment.voice_name
    turns = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        label, separator, utterance = line.partition(":")
        if not separator or label.strip() not in voices:
            raise ValueError("Each dialogue line must start with a configured speaker label; otherwise use segments")
        label = label.strip()
        turns.append({"speaker": label, "text": utterance.strip(), "voiceName": voices[label]})
    return make_input(segments=turns)


class FlowSpeechClient(V1Client):
    """Synchronous v1 client; async methods offload bounded I/O to a worker thread."""

    def check_quota(self) -> FlowSpeechQuota:
        payload = self.quota()
        return FlowSpeechQuota.model_validate({
            **payload["quota"], "entitlement": payload.get("entitlement", payload.get("subscription")),
            "limits": payload.get("limits"),
        })

    def list_voices(self) -> list[dict[str, Any]]:
        return self.voices()

    def generate_speech(self, *, text: str | None = None,
                        speakers: list[FlowSpeechSpeaker] | None = None,
                        voice_name: str = "Kore", original_text: str | None = None,
                        segments: list[dict[str, str]] | None = None,
                        request_id: str | None = None) -> FlowSpeechTtsResult:
        job, audio, request_id = self.generate(
            speech_input(text, voice_name, speakers, segments, original_text), request_id=request_id)
        return FlowSpeechTtsResult(
            audio_base64=base64.b64encode(audio).decode("ascii"),
            job_id=job["id"], request_id=request_id, result_url=job["result"]["url"], usage=job["usage"])

    async def agenerate_speech(self, **kwargs) -> FlowSpeechTtsResult:
        return await asyncio.to_thread(self.generate_speech, **kwargs)

    async def acheck_quota(self) -> FlowSpeechQuota:
        return await asyncio.to_thread(self.check_quota)

    async def alist_voices(self) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self.list_voices)
