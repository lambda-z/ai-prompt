from __future__ import annotations

from generator.state import GraphState


def finalizer_node(state: GraphState) -> GraphState:
    err = state.get("last_error", "")
    if err:
        return {**state, "response": f"FAILED: {err}"}

    out_dir = state.get("generated_dir", "")
    written = state.get("written_files", [])

    msg = ["OK: package generated", f"dir: {out_dir}", f"files: {len(written)}"]
    # 列前 20 个，避免输出过长
    for p in written[:20]:
        msg.append(f"- {p}")
    if len(written) > 20:
        msg.append(f"... ({len(written) - 20} more)")

    return {**state, "response": "\n".join(msg)}
