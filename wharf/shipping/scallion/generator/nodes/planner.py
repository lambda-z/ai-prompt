from __future__ import annotations

import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from generator.config import settings
from generator.prompts import render_prompt
from generator.state import GraphState


# 这里是一个简化的 policy brief（你也可以在调用时动态注入更完整的规则）
_POLICY_BRIEF = "遵守软件工程与安全最佳实践；不得输出危险指令；仅生成与任务相关的文件内容。"


def _make_task_state_json(state: GraphState) -> str:
    safe = {
        "package_name": state.get("package_name"),
        "output_root": state.get("output_root"),
        "revision_count": state.get("revision_count", 0),
        "last_error": state.get("last_error", ""),
    }
    return json.dumps(safe, ensure_ascii=False)


def planner_node(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    revision_count = int(state.get("revision_count", 0))
    last_error = state.get("last_error", "")

    # 当校验失败时，把错误回喂给 user_input 以促使模型修正输出 JSON
    if last_error:
        user_input = (
            f"{user_input}\n\n"
            f"上次输出未通过校验，错误如下：{last_error}\n"
            f"请修正并只输出一个 JSON 对象（key=文件路径, value=文件内容字符串）。"
        )

    prompt_text = render_prompt(
        user_input=user_input,
        policy_brief=_POLICY_BRIEF,
        user_name="Theo Miller",
        user_role="engineer",
        output_pref="json-filemap-only",
        memory_summary="",
        task_state_json=_make_task_state_json(state),
        last_tool_output="",
        remaining=0,
        iter_left=max(0, 3 - revision_count),
    )

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )

    # 关键点：把整个 XML prompt 当作 HumanMessage 发给模型
    # 因为模板已经在 system 区块里规定“只输出 JSON”。
    resp = llm.invoke([HumanMessage(content=prompt_text)])

    return {
        **state,
        "prompt_text": prompt_text,
        "raw_json_text": resp.content,
        "revision_count": revision_count + (1 if last_error else 0),
    }
