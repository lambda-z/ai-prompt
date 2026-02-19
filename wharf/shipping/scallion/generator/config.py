from __future__ import annotations

import os
from pydantic import BaseModel


class Settings(BaseModel):
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY", 'sk-23186f4963ab487199ac2eb22b4c65a5')
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    max_plan_revisions: int = int(os.getenv("MAX_PLAN_REVISIONS", "3"))


settings = Settings()
