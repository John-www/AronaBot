import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


OLLAMA_GENERATE_URL = os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
DUNGEON_GM_MODEL = os.getenv("DUNGEON_GM_MODEL", os.getenv("RAG_OLLAMA_MODEL", "qwen2.5:3b"))
DUNGEON_GM_TIMEOUT = float(os.getenv("DUNGEON_GM_TIMEOUT", "6"))
AI_LOG_PATH = Path(os.getenv("DUNGEON_AI_LOG_PATH", "logs/dungeon_ai.jsonl"))


NARRATION_SYSTEM_PROMPT = """你是アロナ，Discord 文字地城遊戲的地城GM。

你的工作：
- 根據「已確定的遊戲事件資料」寫 50 到 100 字繁體中文旁白。
- 必須全程使用繁體中文，除了專有名稱「アロナ」外，不要使用日文、簡體中文或英文。
- 旁白要有地城氣氛，但要簡潔，不要拖戲。
- 不可改變任何數值。
- 不可新增遊戲選項。
- 不可替玩家做選擇。
- 不可說出程式沒有提供的結果。
- 不要使用 Markdown 表格。

回覆只輸出旁白本身。"""


CHAT_SYSTEM_PROMPT = """你是アロナ，Discord 文字地城遊戲的地城GM助手。

你只能回答與目前地城冒險有關的問題。
必須全程使用繁體中文，除了專有名稱「アロナ」外，不要使用日文、簡體中文或英文。
你可以根據玩家目前狀態、裝備、道具、怪物資訊給建議。
不可替玩家操作。
不可改變遊戲數值。
不可新增遊戲規則。
不可推測資料中沒有提供的數值或效果。
如果資料沒有提供怪物防禦力，就不要提怪物防禦力。
如果資料沒有提供裝備重量、副作用、行動遲滯，就不要提這些內容。
煙霧彈只用於逃跑，不會增加攻擊範圍；可對普通怪、精英怪、寶箱怪使用，不可對中Boss、大Boss、魔王使用。
皮甲只提供防禦，不提供抗性，也沒有體重懲罰。
不可回答地城以外的問題。

如果問題與地城無關，請只回答：
我不告訴你。"""


def ollama_generate(prompt, model=None, timeout=None, log_kind="generate"):
    started = time.perf_counter()
    used_model = model or DUNGEON_GM_MODEL
    payload = {
        "model": used_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.75,
            "num_predict": 120,
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout or DUNGEON_GM_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = (result.get("response") or "").strip()
            log_ai_call(log_kind, used_model, prompt, text, time.perf_counter() - started, "")
            return text
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        log_ai_call(log_kind, used_model, prompt, "", time.perf_counter() - started, repr(exc))
        return ""


def narrate_event(event_data, model=None):
    prompt = f"""{NARRATION_SYSTEM_PROMPT}

事件資料：
{event_data}

請產生旁白："""
    return clean_response(ollama_generate(prompt, model=model, log_kind="narration"))


def answer_gm_question(context, question, model=None):
    prompt = f"""{CHAT_SYSTEM_PROMPT}

目前地城狀態：
{context}

玩家問題：
{question}

請回答："""
    return clean_response(ollama_generate(prompt, model=model, log_kind="gm_chat"))


def clean_response(text):
    text = (text or "").strip()
    if not text:
        return ""
    # Keep Discord output compact and prevent the model from dumping long essays.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)[:500]


def log_ai_call(kind, model, prompt, response, elapsed_seconds, error):
    try:
        AI_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "model": model,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "prompt": prompt,
            "response": response,
            "error": error,
        }
        with AI_LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
