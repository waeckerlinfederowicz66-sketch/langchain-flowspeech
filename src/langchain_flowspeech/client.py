from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field


class FlowSpeechApiError(RuntimeError):
    """Raised when the FlowSpeech API returns an error response."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class FlowSpeechSpeaker(BaseModel):
    """Voice assignment for a single-speaker or multi-speaker request."""

    speaker: str | None = Field(default=None, description="Speaker label in the input text.")
    voice_name: str = Field(default="Kore", description="FlowSpeech voice name.")

    def to_api(self) -> dict[str, str]:
        payload = {"voiceName": self.voice_name}
        if self.speaker:
            payload["speaker"] = self.speaker
        return payload


class FlowSpeechQuota(BaseModel):
    limit: int | None = None
    used: int | None = None
    remaining: int | None = None
    reset_at: str | None = Field(default=None, alias="resetAt")
    is_guest: bool | None = Field(default=None, alias="isGuest")

    model_config = ConfigDict(populate_by_name=True)


class FlowSpeechTtsResult(BaseModel):
    audio_base64: str = Field(alias="audioBase64")
    mime_type: str | None = Field(default=None, alias="mimeType")
    quota: FlowSpeechQuota | None = None
    sample_rate: int | None = Field(default=None, alias="sampleRate")
    num_channels: int | None = Field(default=None, alias="numChannels")
    bits_per_sample: int | None = Field(default=None, alias="bitsPerSample")

    model_config = ConfigDict(populate_by_name=True)

    @property
    def audio_bytes(self) -> bytes:
        return base64.b64decode(self.audio_base64)

    def save(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(self.audio_bytes)
        return output_path


class FlowSpeechClient:
    """Small HTTP client for the public FlowSpeech text-to-speech API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://flowspeech.io",
        timeout: float = 80.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("FLOWSPEECH_API_KEY")
        if not self.api_key:
            raise FlowSpeechApiError(
                "FlowSpeech API key is required. Set FLOWSPEECH_API_KEY or pass api_key."
            )
        self.base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "FlowSpeechClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "langchain-flowspeech/0.1.0",
        }

    def check_quota(self) -> FlowSpeechQuota:
        response = self._client.get(
            f"{self.base_url}/api/ai/text-to-speech/quota",
            headers=self._headers(),
        )
        payload = self._read_response(response)
        quota = payload.get("data", {}).get("quota")
        if not isinstance(quota, dict):
            raise FlowSpeechApiError("FlowSpeech quota response did not include quota data.")
        return FlowSpeechQuota.model_validate(quota)

    def generate_speech(
        self,
        *,
        text: str,
        speakers: list[FlowSpeechSpeaker] | None = None,
        voice_name: str = "Kore",
        original_text: str | None = None,
    ) -> FlowSpeechTtsResult:
        if not text.strip():
            raise ValueError("text must not be empty")

        speaker_payload = speakers or [FlowSpeechSpeaker(voice_name=voice_name)]
        response = self._client.post(
            f"{self.base_url}/api/ai/text-to-speech",
            headers=self._headers(),
            json={
                "text": text,
                "originalText": original_text or text,
                "speakers": [speaker.to_api() for speaker in speaker_payload],
            },
        )
        payload = self._read_response(response)
        data = payload.get("data")
        if not isinstance(data, dict) or not data.get("audioBase64"):
            raise FlowSpeechApiError("FlowSpeech response did not include audioBase64.")
        return FlowSpeechTtsResult.model_validate(data)

    @staticmethod
    def _read_response(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise FlowSpeechApiError(
                "FlowSpeech API returned a non-JSON response.",
                status_code=response.status_code,
            ) from exc

        if response.status_code >= 400:
            message = payload.get("message") if isinstance(payload, dict) else None
            raise FlowSpeechApiError(
                message or f"FlowSpeech API returned HTTP {response.status_code}.",
                status_code=response.status_code,
            )

        if not isinstance(payload, dict) or payload.get("code") != 0:
            message = payload.get("message") if isinstance(payload, dict) else None
            raise FlowSpeechApiError(message or "FlowSpeech API returned an error.")

        return payload
