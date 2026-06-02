import httpx

from backend.config import settings


SYSTEM_PROMPT_TEMPLATE = """你是一个 PostgreSQL SQL 专家。你的任务是将用户的自然语言查询转换为 SQL 语句。

当前数据库的表结构如下：

{table_metadata}

约束：
1. 只生成 SELECT 查询
2. 如果用户需求包含排序但未说明方向，默认使用 DESC
3. 使用 PostgreSQL 兼容的 SQL 语法
4. 只返回 SQL 语句本身，不要有任何解释、注释或 markdown 标记
5. 如果要查询所有列，使用 *，不要列出每个列名
6. 如果查询条件涉及 LIKE，使用标准的 PostgreSQL LIKE 语法"""


async def generate_sql(db_name: str, natural_text: str, metadata_json: str) -> str:
    """
    调用 LLM 将自然语言转换为 SQL。
    支持 OpenAI 兼容 API 和 Ollama 原生 API 两种模式。
    """
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(table_metadata=metadata_json)

    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Try OpenAI-compatible endpoint first
        openai_url = f"{settings.llm_base_url}/chat/completions"
        openai_body = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_text},
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        }

        response = await client.post(openai_url, headers=headers, json=openai_body)

        if response.status_code == 404:
            # Fallback: Ollama native API (/api/chat)
            ollama_url = f"{settings.llm_base_url.replace('/v1', '')}/api/chat"
            ollama_body = {
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": natural_text},
                ],
                "stream": False,
                "options": {"temperature": 0.1},
            }
            response = await client.post(ollama_url, json=ollama_body)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
        else:
            # OpenAI-compatible response
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise ValueError("LLM 返回为空，未生成 SQL")
            content = choices[0].get("message", {}).get("content", "").strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) >= 3:
                content = "\n".join(lines[1:-1]).strip()

        if not content:
            raise ValueError("LLM 生成的 SQL 为空")

        return content
