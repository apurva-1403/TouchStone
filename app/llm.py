"""Single place that constructs the Gemini client.

All model calls go through Vertex AI using Application Default Credentials:
locally via `gcloud auth application-default login`, on Cloud Run via the
service's attached service account. No API keys in code or images.
"""
import threading

from google import genai
from google.genai import types

from app import config

_client: genai.Client | None = None
_lock = threading.Lock()


def client() -> genai.Client:
    """Process-wide client. Created once under a lock: a Client closes its HTTP connection when garbage-collected,
    so concurrent first calls must not each build (and then drop) their own instance."""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = genai.Client(
                    vertexai=True, project=config.GCP_PROJECT, location=config.GCP_LOCATION,
                    http_options=types.HttpOptions(
                        timeout=45_000,  # ms; fail rather than hang a request
                        # Back off on quota (429) and transient server errors instead of failing the answer.
                        retry_options=types.HttpRetryOptions(attempts=3, initial_delay=1.0, max_delay=8.0,
                                                             exp_base=2.0, jitter=1.0,
                                                             http_status_codes=[429, 500, 502, 503, 504]),
                    ),
                )
    return _client
