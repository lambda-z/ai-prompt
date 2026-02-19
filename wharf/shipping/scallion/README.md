# LangGraph Package Generator

该工程使用 **LangGraph** 把「Prompt → 结构化 JSON 脚本 → 校验 → 执行（生成文件）」串成可控的状态机。

它会让 LLM 输出一个 JSON 对象：key 为文件路径，value 为文件内容字符串，然后在本地生成一个可 `pip install .` 安装、可放入 git 仓库并支持 `pip install git+...` 安装的 Python package（示例为 `greet_package`）。

---

## 目录结构（本仓库）

```
langgraph-package-generator/
  pyproject.toml
  .env.example
  app/
    main.py
  generator/
    __init__.py
    config.py
    prompts.py
    schema.py
    graph.py
    state.py
    nodes/
      __init__.py
      planner.py
      validator.py
      executor.py
      finalizer.py
    runtime/
      __init__.py
      fs.py
      sanitize.py
  tests/
    test_validator.py
```

---

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

配置环境变量：

```bash
cp .env.example .env
# 填写 OPENAI_API_KEY
```

---

## 运行（生成一个示例 package 到 ./out/）

```bash
python -m app.main --out ./out --name greet_package
```

你也可以传入自定义需求（会被注入到 Prompt 的 {user_input}）：

```bash
python -m app.main --out ./out --name greet_package --request "做一个最小包，函数 greet(name) 返回 Hello, name!"
```

生成完成后：

```bash
cd out/greet_package
pip install .
pytest -q
```

---

## 说明

- Planner：使用你提供的 XML Prompt 模板（做了必要的占位符替换），强制 LLM 只输出 JSON。
- Validator：对 LLM 输出做 JSON 解析 + Pydantic 校验 + 基本安全检查。
- Executor：把 JSON 中的文件写入磁盘，形成可安装 package。
- Finalizer：返回汇总信息（生成路径、文件数、错误等）。
