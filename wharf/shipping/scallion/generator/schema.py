from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict


class FileMap(BaseModel):
    """LLM 输出：一个文件路径到文件内容的映射。"""

    files: Dict[str, str] = Field(..., description="key=filepath, value=file content")
