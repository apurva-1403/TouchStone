"""Local smoke test for Gemini (generation + embedding) via Vertex AI.

Requires Application Default Credentials:
    gcloud auth application-default login
Run from the repo root:
    python -m scripts.gemini_hello
"""
from app import config, llm


def main():
    c = llm.client()
    r = c.models.generate_content(model=config.AGENT_MODEL, contents="Reply with exactly: OK")
    print(f"generate  {config.AGENT_MODEL}: {r.text.strip()!r}")
    e = c.models.embed_content(model=config.EMBEDDING_MODEL, contents=["VPN drops every 30 minutes"])
    print(f"embed     {config.EMBEDDING_MODEL}: dim={len(e.embeddings[0].values)}")


if __name__ == "__main__":
    main()
