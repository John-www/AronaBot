import asyncio
import html
import json
import os
import random
import re
import traceback
import urllib.error
import urllib.request
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from thesis_rag import CHUNKS_FILE, EMBEDDINGS_FILE, ask
import dungeon_ai
import dungeon_game as dungeon
from dungeon_db import delete_player, diagnostics as dungeon_db_diagnostics, load_player, save_player


PROJECT_DIR = Path(__file__).resolve().parent
TOKEN_ENV = "DISCORD_TOKEN"
DEFAULT_MODEL = os.getenv("RAG_OLLAMA_MODEL", "qwen2.5:3b")
DUNGEON_GM_MODEL = os.getenv("DUNGEON_GM_MODEL", DEFAULT_MODEL)
ALLOWED_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
OLLAMA_HEALTH_URL = "http://localhost:11434/api/tags"
LEGACY_SETTING_PATH = Path(os.getenv("LEGACY_BOT_SETTING", r"D:\PUclass\VStest\2B_ISNOTBOT-main\setting.json"))
NO_COLOR_IMAGE_PATH = Path(os.getenv("NO_COLOR_IMAGE_PATH", PROJECT_DIR / "newbotpic" / "NOH.png"))
CWA_WEEK_URL = "https://www.cwa.gov.tw/V8/C/W/County/MOD/wf7dayNC_NCSEI/ALL_Week.html"
CWA_WEEK_TIME_URL = "https://www.cwa.gov.tw/Data/js/fcst/week_TIME.js"

TAIWAN_COUNTIES = [
    "基隆市",
    "臺北市",
    "新北市",
    "桃園市",
    "新竹市",
    "新竹縣",
    "苗栗縣",
    "臺中市",
    "彰化縣",
    "南投縣",
    "雲林縣",
    "嘉義市",
    "嘉義縣",
    "臺南市",
    "高雄市",
    "屏東縣",
    "宜蘭縣",
    "花蓮縣",
    "臺東縣",
    "澎湖縣",
    "金門縣",
    "連江縣",
]

MEAL_OPTIONS = [
    "漢堡",
    "披薩",
    "拉麵",
    "壽司",
    "麥當勞",
    "肯德基",
    "便當",
    "滷肉飯",
    "雞肉飯",
    "牛肉麵",
    "鍋貼",
    "水餃",
    "炒飯",
    "炒麵",
    "燴飯",
    "咖哩飯",
    "義大利麵",
    "火鍋",
    "石鍋拌飯",
    "越南河粉",
    "雞排飯",
    "鐵板燒",
    "鹹酥雞",
    "自助餐",
    "小火鍋",
    "蚵仔煎",
    "肉圓",
    "滷味",
    "刈包",
    "焢肉飯",
    "排骨飯",
    "雞腿飯",
    "燒肉飯",
    "三寶飯",
    "叉燒飯",
    "燒臘飯",
    "海南雞飯",
    "油雞飯",
    "鴨肉飯",
    "鵝肉飯",
    "爌肉飯",
    "豬腳飯",
    "魚排飯",
    "虱目魚粥",
    "海鮮粥",
    "廣東粥",
    "皮蛋瘦肉粥",
    "陽春麵",
    "乾麵",
    "麻醬麵",
    "餛飩麵",
    "榨菜肉絲麵",
    "擔仔麵",
    "意麵",
    "米粉湯",
    "切仔麵",
    "羊肉羹",
    "魷魚羹",
    "肉羹麵",
    "土魠魚羹",
    "咖哩烏龍麵",
    "烏龍麵",
    "蕎麥麵",
    "豚骨拉麵",
    "味噌拉麵",
    "牛丼",
    "親子丼",
    "豬排丼",
    "天丼",
    "日式咖哩",
    "韓式泡菜鍋",
    "部隊鍋",
    "銅盤烤肉",
    "韓式炸雞",
    "韓式拌飯",
    "泰式打拋豬飯",
    "泰式綠咖哩",
    "泰式炒河粉",
    "海南雞",
    "沙威瑪",
    "墨西哥捲餅",
    "潛艇堡",
    "貝果三明治",
    "早午餐拼盤",
    "蛋包飯",
    "焗烤飯",
    "焗烤麵",
    "燉飯",
    "排餐",
    "牛排",
    "豬排飯",
    "炸豬排定食",
    "烤魚定食",
    "唐揚雞定食",
    "生魚片丼",
    "握壽司",
    "手捲",
    "涼麵",
    "雞絲飯",
    "米糕",
]

LATE_NIGHT_MEAL_OPTIONS = [
    "泡麵",
    "杯麵",
    "炒泡麵",
    "關東煮",
    "茶葉蛋",
    "御飯糰",
    "飯糰",
    "三明治",
    "熱狗堡",
    "微波便當",
    "微波義大利麵",
    "微波燴飯",
    "微波炒飯",
    "微波咖哩飯",
    "雞胸肉",
    "鹽水雞",
    "滷味",
    "麻辣燙",
    "鹹酥雞",
    "炸雞排",
    "甜不辣",
    "米血",
    "雞蛋豆腐",
    "大腸麵線",
    "蚵仔麵線",
    "臭豆腐",
    "蔥油餅",
    "蛋餅",
    "鐵板麵",
    "涼麵",
    "水餃",
    "鍋貼",
    "小火鍋",
    "麥當勞",
    "肯德基",
    "摩斯漢堡",
    "漢堡王",
    "達美樂",
    "必勝客",
    "披薩",
    "炸雞桶",
    "雞塊",
    "薯條",
    "沙威瑪",
    "牛肉捲餅",
    "燒烤",
    "串燒",
    "烤肉飯",
    "滷肉飯",
    "雞肉飯",
    "焢肉飯",
    "便當",
    "牛肉麵",
    "乾麵",
    "餛飩麵",
    "米粉湯",
    "廣東粥",
    "皮蛋瘦肉粥",
    "虱目魚粥",
    "粥品",
]

COUNTY_ALIASES = {
    "台北": "臺北市",
    "臺北": "臺北市",
    "台北市": "臺北市",
    "臺北市": "臺北市",
    "新竹": "新竹市",
    "嘉義": "嘉義市",
    "台中": "臺中市",
    "臺中": "臺中市",
    "台南": "臺南市",
    "臺南": "臺南市",
    "台東": "臺東縣",
    "臺東": "臺東縣",
    "連江": "連江縣",
    "馬祖": "連江縣",
}


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
DUNGEON_TREE_SYNCED = False
READY_MESSAGE_SENT = False


def load_legacy_settings():
    if not LEGACY_SETTING_PATH.exists():
        return {}
    try:
        with LEGACY_SETTING_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


LEGACY_SETTINGS = load_legacy_settings()


def is_allowed_channel(ctx):
    if not ALLOWED_CHANNEL_ID:
        return True
    return str(ctx.channel.id) == ALLOWED_CHANNEL_ID


async def reject_wrong_channel(ctx):
    if is_allowed_channel(ctx):
        return False
    await ctx.reply(
        "這個 RAG bot 目前只在指定頻道回應。\n"
        f"目前頻道 ID：`{ctx.channel.id}`\n"
        f"允許頻道 ID：`{ALLOWED_CHANNEL_ID}`"
    )
    return True


async def reject_wrong_interaction(interaction):
    if not ALLOWED_CHANNEL_ID:
        return False
    if str(interaction.channel_id) == str(ALLOWED_CHANNEL_ID):
        return False
    await interaction.response.send_message(
        f"這個 bot 目前只在指定頻道 `<#{ALLOWED_CHANNEL_ID}>` 回答。",
        ephemeral=True,
    )
    return True


def ollama_is_running():
    try:
        with urllib.request.urlopen(OLLAMA_HEALTH_URL, timeout=3) as response:
            return response.status == 200
    except urllib.error.URLError:
        return False


def fetch_text(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_tags(value):
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = value.replace("\u2002", " ").replace("&ensp;", " ")
    return re.sub(r"\s+", " ", value).strip()


def normalize_county_name(location):
    compact = re.sub(r"\s+", "", location or "")
    if not compact:
        return None
    compact = compact.replace("台", "臺")

    if compact in COUNTY_ALIASES:
        return COUNTY_ALIASES[compact]
    if compact.replace("臺", "台") in COUNTY_ALIASES:
        return COUNTY_ALIASES[compact.replace("臺", "台")]
    if compact in TAIWAN_COUNTIES:
        return compact

    city_name = f"{compact}市"
    county_name = f"{compact}縣"
    if city_name in TAIWAN_COUNTIES:
        return city_name
    if county_name in TAIWAN_COUNTIES:
        return county_name
    return None


def parse_weather_cell(cell_html):
    weather_match = re.search(r'title="([^"]+)"', cell_html)
    temp_match = re.search(r'<span class="tem-C is-active">(.+?)</span>', cell_html, re.DOTALL)
    weather = html.unescape(weather_match.group(1)).replace("天氣圖示,", "").strip() if weather_match else "未知"
    temp = strip_tags(temp_match.group(1)).replace(" - ", "-") if temp_match else "--"
    return {"weather": weather, "temp": temp}


def parse_cwa_week_table(page_html):
    table_match = re.search(r'<table[^>]+id="table1"[^>]*>(.*?)</table>', page_html, re.DOTALL)
    if not table_match:
        raise RuntimeError("中央氣象署一週預報格式已變更，找不到主要表格。")

    table_html = table_match.group(1)
    days = [
        strip_tags(match.group(1))
        for match in re.finditer(r'<th[^>]+id="day\d+"[^>]*>.*?<span[^>]*>(.*?)</span>', table_html, re.DOTALL)
    ]
    if not days:
        raise RuntimeError("中央氣象署一週預報格式已變更，找不到日期欄位。")

    forecasts = {}
    for body_match in re.finditer(r"<tbody>(.*?)</tbody>", table_html, re.DOTALL):
        body = body_match.group(1)
        county_match = re.search(r'<span class="heading_3">([^<]+)', body)
        if not county_match:
            continue
        county = strip_tags(county_match.group(1))

        day_row = re.search(r'<tr class="day">(.*?)</tr>', body, re.DOTALL | re.IGNORECASE)
        night_row = re.search(r'<tr class="night">(.*?)</tr>', body, re.DOTALL | re.IGNORECASE)
        if not day_row or not night_row:
            continue

        day_cells = re.findall(r'<td[^>]+headers="[^"]+ day\d+"[^>]*>(.*?)</td>', day_row.group(1), re.DOTALL)
        night_cells = re.findall(r'<td[^>]+headers="[^"]+ day\d+"[^>]*>(.*?)</td>', night_row.group(1), re.DOTALL)
        forecasts[county] = []
        for index, label in enumerate(days):
            forecasts[county].append(
                {
                    "date": label,
                    "day": parse_weather_cell(day_cells[index]) if index < len(day_cells) else None,
                    "night": parse_weather_cell(night_cells[index]) if index < len(night_cells) else None,
                }
            )

    return forecasts


def parse_cwa_week_time(time_js):
    from_match = re.search(r"'From_Time':\['([^']+)'\]", time_js)
    to_match = re.search(r"'To_Time':\['([^']+)'\]", time_js)
    if not from_match or not to_match:
        return None
    return f"{from_match.group(1)}~{to_match.group(1)}"


def is_rainy_weather(weather_text):
    return any(keyword in weather_text for keyword in ("雨", "雷"))


def read_cwa_week_weather(location):
    county = normalize_county_name(location)
    if not county:
        available = "、".join(TAIWAN_COUNTIES)
        return f"找不到 `{location}`，請輸入臺灣縣市，例如 `!天氣 新竹`。\n可用縣市：{available}"

    page_html = fetch_text(CWA_WEEK_URL, timeout=15)
    forecasts = parse_cwa_week_table(page_html)
    county_forecast = forecasts.get(county)
    if not county_forecast:
        raise RuntimeError(f"中央氣象署資料裡找不到 {county}。")

    try:
        valid_time = parse_cwa_week_time(fetch_text(CWA_WEEK_TIME_URL, timeout=10))
    except urllib.error.URLError:
        valid_time = None

    lines = [f"**{county} 一週天氣**"]
    if valid_time:
        lines.append(f"有效時間：{valid_time}")
    lines.append("資料來源：中央氣象署一週預報")

    for item in county_forecast:
        day_part = item["day"] or {"weather": "未知", "temp": "--"}
        night_part = item["night"] or {"weather": "未知", "temp": "--"}
        lines.append(
            f"{item['date']}：白天 {day_part['weather']} {day_part['temp']} C；"
            f"晚上 {night_part['weather']} {night_part['temp']} C"
        )

    if county == "臺北市" and len(county_forecast) > 1:
        tomorrow = county_forecast[1]
        tomorrow_weather = " ".join(
            part["weather"]
            for part in (tomorrow.get("day"), tomorrow.get("night"))
            if part
        )
        if is_rainy_weather(tomorrow_weather):
            lines.append("爛台北")

    return "\n".join(lines)


def random_existing_file(paths):
    candidates = [Path(path) for path in paths if Path(path).exists()]
    if not candidates:
        return None
    return random.choice(candidates)


def choose_option(default_options, options=None):
    candidates = options.split() if options else default_options
    candidates = [option.strip() for option in candidates if option.strip()]
    return random.choice(candidates)


def choose_meal(options=None):
    return choose_option(MEAL_OPTIONS, options)


def choose_late_night_meal(options=None):
    return choose_option(LATE_NIGHT_MEAL_OPTIONS, options)


def read_cpu_memory_status():
    try:
        import psutil
    except ImportError:
        return "尚未安裝 `psutil`，請執行 `python -m pip install psutil`。"

    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    memory = psutil.virtual_memory()
    memory_used_gb = memory.used / (1024**3)
    memory_total_gb = memory.total / (1024**3)
    return (
        "**電腦狀態**\n"
        f"CPU 核心數：{cpu_count}\n"
        f"CPU 使用率：{cpu_percent:.1f}%\n"
        f"RAM 使用率：{memory.percent:.1f}%\n"
        f"RAM 使用量：{memory_used_gb:.2f} / {memory_total_gb:.2f} GB"
    )


def read_gpu_status():
    try:
        from pynvml import (
            NVMLError,
            nvmlDeviceGetCount,
            nvmlDeviceGetFanSpeed,
            nvmlDeviceGetHandleByIndex,
            nvmlDeviceGetMemoryInfo,
            nvmlDeviceGetName,
            nvmlDeviceGetPowerState,
            nvmlDeviceGetTemperature,
            nvmlInit,
            nvmlShutdown,
        )
    except ImportError:
        return "尚未安裝 `pynvml`，請執行 `python -m pip install nvidia-ml-py`。"

    try:
        nvmlInit()
        lines = ["**GPU 狀態**"]
        for index in range(nvmlDeviceGetCount()):
            handle = nvmlDeviceGetHandleByIndex(index)
            memory = nvmlDeviceGetMemoryInfo(handle)
            name = nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode("utf-8", errors="replace")
            lines.extend(
                [
                    f"GPU {index}：{name}",
                    f"溫度：{nvmlDeviceGetTemperature(handle, 0)} C",
                    f"記憶體：{memory.used / (1024**3):.2f} / {memory.total / (1024**3):.2f} GB",
                    f"風扇：{nvmlDeviceGetFanSpeed(handle)}%",
                    f"Power state：P{nvmlDeviceGetPowerState(handle)}",
                ]
            )
        return "\n".join(lines)
    except Exception as exc:
        error_type = "NVIDIA NVML" if "NVMLError" in globals() and isinstance(exc, NVMLError) else "GPU"
        return f"{error_type} 檢測失敗：{exc}"
    finally:
        try:
            nvmlShutdown()
        except Exception:
            pass


def run_rag(question, model):
    from io import StringIO
    from contextlib import redirect_stdout

    output = StringIO()
    with redirect_stdout(output):
        ask(question, top_k=5, model=model)
    return output.getvalue().strip()


def split_message(text, limit=1900):
    if len(text) <= limit:
        return [text]

    parts = []
    current = []
    current_size = 0
    for paragraph in text.split("\n\n"):
        size = len(paragraph) + 2
        if current and current_size + size > limit:
            parts.append("\n\n".join(current))
            current = []
            current_size = 0
        current.append(paragraph)
        current_size += size

    if current:
        parts.append("\n\n".join(current))
    return parts


@bot.event
async def on_ready():
    global DUNGEON_TREE_SYNCED, READY_MESSAGE_SENT
    print(f">> RAG bot is online as {bot.user} <<")
    if not DUNGEON_TREE_SYNCED:
        try:
            synced = await bot.tree.sync()
            DUNGEON_TREE_SYNCED = True
            print(f">> Synced {len(synced)} slash commands <<")
        except Exception as exc:
            print(f">> Slash command sync failed: {exc} <<")
    if ALLOWED_CHANNEL_ID:
        print(f">> Restricted to channel {ALLOWED_CHANNEL_ID} <<")
        channel = bot.get_channel(int(ALLOWED_CHANNEL_ID))
        if channel and not READY_MESSAGE_SENT:
            await channel.send(
                "アロナ上~線~\n\n"
                "老師想做甚麼?\n"
                "`!help` - 查看一般指令。\n"
                "`!地城` - 查看地城測試說明。",
                view=HomeView(),
            )
            READY_MESSAGE_SENT = True


@bot.listen("on_interaction")
async def log_interaction(interaction):
    data = getattr(interaction, "data", {}) or {}
    print(f">> Interaction received: type={interaction.type} name={data.get('name')} user={interaction.user} <<")


@bot.command(name="ping")
async def ping(ctx):
    if await reject_wrong_channel(ctx):
        return
    await ctx.reply(f"{round(bot.latency * 1000)} ms")


@bot.command(name="help")
async def help_command(ctx):
    if await reject_wrong_channel(ctx):
        return
    message = (
        "**RAG Bot 指令表**\n"
        "`!status` - 查看 RAG 索引、Ollama、模型與回答頻道狀態。\n"
        "`!ask 問題` - 詢問論文 RAG，例如 `!ask 用三句話介紹我的論文`。\n"
        "`!天氣 縣市` - 查中央氣象署一週天氣，例如 `!天氣 新竹`。\n"
        "`!吃啥` - 隨機推薦一項正餐；也可自訂選項，例如 `!吃啥 拉麵 火鍋 披薩`。\n"
        "`!吃啥消夜` / `!吃啥宵夜` - 隨機推薦宵夜或便利商店容易買到的食物。\n"
        "`!抽籤` / `!抽獎` - 隨機抽一張舊 bot 的籤圖。\n"
        "`!電腦檢測` / `!pc_status` / `!gpu_inf` - 查看 CPU、RAM 與 NVIDIA GPU 狀態。\n"
        # "`!色圖` - 回覆不可以色色。\n"
        "`!ping` - 測試 bot 延遲。\n"
        "`!shutdown` - 讓 bot 下線，限 bot owner 使用。\n\n"
        "範例：\n"
        "`!ask 這篇論文的研究方法是什麼?`\n"
        "`!ask 這篇論文模型的組成`"
    )
    await ctx.reply(message)


@bot.command(name="helpme")
async def helpme(ctx):
    await help_command(ctx)


@bot.command(name="地城")
async def dungeon_intro(ctx):
    if await reject_wrong_channel(ctx):
        return
    message = (
        "**Discord 地城冒險測試中**\n"
        "目前地城還處於生成與測試階段，可以先玩玩看、幫忙抓流程問題。\n\n"
        "**目前開放**\n"
        "第 1～5 層、普通怪、精英怪、第 3 層中 Boss、第 5 層 Boss、寶箱、商人、道具與逃跑。\n\n"
        "**重要提醒**\n"
        "現在是大家操作同一隻冒險者，也就是同一個伺服器共用同一份進度。\n"
        "請不要使用 `/開始 重置:True`，那會重開目前測試進度。\n\n"
        "**基本操作**\n"
        "現在主要可以直接按 bot 訊息下方的按鈕或選單操作；下面 slash 指令保留當備用。\n"
        "`/開始` - 建立共享冒險者，已有進度時不用再按。\n"
        "`/狀態` - 查看 HP、Gold、裝備與目前樓層。\n"
        "`/探索` - 查看目前可選的道路。\n"
        "`/選擇 編號:1` - 選擇第 1 個事件，可改 1～5。\n"
        "`/攻擊` - 戰鬥中攻擊。\n"
        "`/逃跑` - 戰鬥中嘗試逃跑。\n"
        "`/背包` - 查看道具與備用裝備。\n"
        "`/使用 編號:1` - 使用背包中的道具。\n"
        "`/裝備 編號:1` - 裝備背包中的備用裝備。\n"
        "`/開啟`、`/放棄` - 寶箱相關操作。\n"
        "`/商店`、`/購買 編號:1 2 4`、`/販售 編號:1`、`/離開商店` - 商人相關操作。"
        "\n`/旁白 開啟:True` / `/旁白 開啟:False` - 開關 AI GM 旁白。"
        "\n`/問 問題:我現在該逃跑嗎` - 詢問 AI GM 地城建議。"
    )
    await ctx.reply(message)


@bot.command(name="地城同步", aliases=["sync_dungeon", "syncslash"])
async def sync_dungeon_commands(ctx):
    if await reject_wrong_channel(ctx):
        return
    if not ctx.guild:
        await ctx.reply("這個指令只能在 Discord 伺服器內使用。")
        return
    guild = discord.Object(id=ctx.guild.id)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    names = "、".join(command.name for command in synced)
    await ctx.reply(f"已同步 {len(synced)} 個 slash commands 到此伺服器：{names}")


@bot.command(name="地城資料庫", aliases=["dungeon_db"])
async def dungeon_database_status(ctx):
    if await reject_wrong_channel(ctx):
        return
    info = dungeon_db_diagnostics()
    message = (
        "**地城資料庫狀態**\n"
        f"路徑：`{info['db_path']}`\n"
        f"環境變數：`{info['env_path'] or '未設定'}`\n"
        f"存在：{info['exists']}\n"
        f"大小：{info['size']} bytes\n"
        f"健康：{info.get('integrity', 'unknown')}\n"
        f"Journal：{info.get('journal_mode', 'unknown')}\n"
        f"玩家數：{info.get('players', 'unknown')}\n"
        f"錯誤：`{info['error'] or '無'}`"
    )
    await ctx.reply(message)


@bot.command(name="status")
async def status(ctx):
    if await reject_wrong_channel(ctx):
        return
    index_status = "OK" if CHUNKS_FILE.exists() else "找不到索引，請先跑 `python thesis_rag.py ingest rag_docs`"
    embedding_status = "OK" if EMBEDDINGS_FILE.exists() else "找不到向量索引，請重跑 `python thesis_rag.py ingest rag_docs`"
    ollama_status = "OK" if ollama_is_running() else "連不上 Ollama"
    channel_status = f"`{ALLOWED_CHANNEL_ID}`" if ALLOWED_CHANNEL_ID else "未限制"
    message = (
        "**RAG Bot 狀態**\n"
        f"索引：{index_status}\n"
        f"向量索引：{embedding_status}\n"
        f"Ollama：{ollama_status}\n"
        f"模型：`{DEFAULT_MODEL}`\n"
        f"地城GM模型：`{DUNGEON_GM_MODEL}`\n"
        f"回答頻道：{channel_status}\n"
        "指令：`!ask 你的問題`"
    )
    await ctx.reply(message)


async def send_random_file(ctx, key, missing_message):
    if await reject_wrong_channel(ctx):
        return
    image_path = random_existing_file(LEGACY_SETTINGS.get(key, []))
    if not image_path:
        await ctx.reply(missing_message)
        return
    await ctx.reply(file=discord.File(str(image_path)))


@bot.command(name="抽籤", aliases=["抽獎"])
async def draw_lottery(ctx):
    await send_random_file(ctx, "pic2", "找不到可用的抽籤圖片，請確認舊 bot 的圖片路徑還存在。")


@bot.command(name="隨機圖片")
async def random_image(ctx):
    await send_random_file(ctx, "pic", "找不到可用的隨機圖片，請確認舊 bot 的圖片路徑還存在。")


@bot.command(name="吃啥")
async def what_to_eat(ctx, *, options=None):
    if await reject_wrong_channel(ctx):
        return
    await ctx.reply(f"吃{choose_meal(options)}")


@bot.command(name="吃啥消夜", aliases=["吃啥宵夜"])
async def what_to_eat_late_night(ctx, *, options=None):
    if await reject_wrong_channel(ctx):
        return
    await ctx.reply(f"吃{choose_late_night_meal(options)}")


@bot.command(name="色圖")
async def no_color(ctx):
    if await reject_wrong_channel(ctx):
        return
    if not NO_COLOR_IMAGE_PATH.exists():
        await ctx.reply("不可以色色，但圖片檔案找不到。")
        return
    await ctx.reply("不可以色色", file=discord.File(str(NO_COLOR_IMAGE_PATH)))


def read_full_pc_status():
    return f"{read_cpu_memory_status()}\n\n{read_gpu_status()}"


@bot.command(name="電腦檢測", aliases=["pc_status", "cpu_use", "mem_use", "gpu_inf"])
async def pc_status_zh(ctx):
    if await reject_wrong_channel(ctx):
        return
    status_text = await asyncio.to_thread(read_full_pc_status)
    await ctx.reply(status_text)


@bot.command(name="天氣")
async def weather_zh(ctx, *, location=None):
    if await reject_wrong_channel(ctx):
        return
    if not location:
        await ctx.reply("請輸入臺灣縣市，例如 `!天氣 新竹`、`!天氣 台北`。")
        return

    async with ctx.typing():
        try:
            weather_text = await asyncio.to_thread(read_cwa_week_weather, location)
        except Exception as exc:
            await ctx.reply(f"天氣查詢失敗：{exc}")
            return

    for index, part in enumerate(split_message(weather_text)):
        if index == 0:
            await ctx.reply(part)
        else:
            await ctx.send(part)


@bot.command(name="ask")
async def ask_rag(ctx, *, question):
    if await reject_wrong_channel(ctx):
        return
    async with ctx.typing():
        try:
            answer = await asyncio.to_thread(run_rag, question, DEFAULT_MODEL)
        except Exception as exc:
            await ctx.reply(f"RAG 發生錯誤：{exc}")
            return

    if not answer:
        await ctx.reply("沒有產生回答，請確認 Ollama 是否啟動、模型是否下載完成。")
        return

    for index, part in enumerate(split_message(answer)):
        if index == 0:
            await ctx.reply(part)
        else:
            await ctx.send(part)


async def send_interaction_text(interaction, text, view=None):
    parts = split_message(text)
    if not interaction.response.is_done():
        if view is None:
            await interaction.response.send_message(parts[0])
        else:
            await interaction.response.send_message(parts[0], view=view)
    else:
        if view is None:
            await interaction.followup.send(parts[0])
        else:
            await interaction.followup.send(parts[0], view=view)
    for part in parts[1:]:
        await interaction.followup.send(part)


async def defer_interaction(interaction):
    if not interaction.response.is_done():
        await interaction.response.defer(thinking=True)


async def send_dungeon_result(interaction, state, text, narrate=False, narration_kind="事件"):
    if narrate and dungeon_gm_enabled(state):
        narration = await asyncio.to_thread(
            dungeon_ai.narrate_event,
            build_narration_context(state, text, narration_kind),
            DUNGEON_GM_MODEL,
        )
        if narration:
            text = f"**アロナ:**\n{narration}\n\n**系統結果**\n{text}"
    save_player(state)
    await send_interaction_text(interaction, text, view=create_dungeon_view(state))


def load_dungeon_or_message(interaction):
    state = load_player(dungeon_session_id(interaction))
    if not state:
        return None, "你還沒有建立冒險者。請先使用 `/開始`。"
    dungeon.normalize_state(state)
    return state, None


def dungeon_session_id(interaction):
    if interaction.guild_id:
        return f"guild:{interaction.guild_id}"
    return f"channel:{interaction.channel_id}"


def dungeon_session_name(interaction):
    if interaction.guild:
        return f"{interaction.guild.name} 冒險隊"
    return "共享冒險隊"


def set_dungeon_actor(state, interaction):
    state["last_actor"] = interaction.user.display_name


def dungeon_gm_enabled(state):
    return state.get("gm_narration_enabled", True)


def build_narration_context(state, result_text, kind):
    battle = state.get("battle") or {}
    encounter = state.get("encounter") or {}
    monster = battle.get("monster") or encounter.get("monster")
    monster_text = ""
    if monster:
        current_hp = battle.get("enemy_hp", monster.get("hp"))
        max_hp = battle.get("enemy_max_hp", monster.get("hp"))
        monster_text = f"敵人：{monster.get('name')}（{monster.get('type')}），HP {current_hp}/{max_hp}"
    return (
        f"事件類型：{kind}\n"
        f"提議者：{state.get('last_actor') or '未知'}\n"
        "這是多人共用冒險，請把玩家稱作冒險團，不要把提議者寫成唯一主角。\n"
        f"樓層：第 {state.get('floor')} 層，第 {min(state.get('step', 0) + 1, 5)} 步\n"
        f"玩家狀態：{dungeon.compact_status_line(state)}\n"
        f"{monster_text}\n"
        "已確定的系統結果如下，必須遵守，不可改寫數值或選項：\n"
        f"{result_text[:1200]}"
    )


def build_gm_chat_context(state):
    battle = state.get("battle") or {}
    encounter = state.get("encounter") or {}
    monster = battle.get("monster") or encounter.get("monster")
    monster_text = "無"
    if monster:
        current_hp = battle.get("enemy_hp", monster.get("hp"))
        max_hp = battle.get("enemy_max_hp", monster.get("hp"))
        monster_text = f"{monster.get('name')}（{monster.get('type')}）HP {current_hp}/{max_hp}"
    inventory = ", ".join(f"{name}x{qty}" for name, qty in dungeon.inventory_lines(state)) or "無"
    equipment_bag = ", ".join(dungeon.format_equipment(item) for item in state.get("equipment_bag", [])) or "無"
    return (
        f"模式：{state.get('mode')}\n"
        f"樓層：第 {state.get('floor')} 層，第 {min(state.get('step', 0) + 1, 5)} 步\n"
        f"玩家狀態：{dungeon.compact_status_line(state)}\n"
        f"目前敵人：{monster_text}\n"
        f"背包道具：{inventory}\n"
        f"備用裝備：{equipment_bag}\n"
        "請只根據以上狀態給地城內建議，不可替玩家操作。"
    )


def use_items_from_selection(state, values_text):
    numbers = parse_inventory_selection_values(values_text)
    if not numbers:
        return "請選擇要使用的道具。"
    messages = []
    for number in numbers:
        messages.append(dungeon.use_item(state, number))
        if state.get("mode") in {"dead", "cleared"}:
            break
    return "\n\n".join(messages)


def parse_inventory_selection_values(values_text):
    numbers = []
    for token in str(values_text).split():
        base = token.split(":", 1)[0]
        if base.isdigit():
            numbers.append(int(base))
    return numbers


def equip_items_from_selection(state, values_text):
    equipment_indices = []
    for token in str(values_text).split():
        if token.startswith("eq:") and token[3:].isdigit():
            equipment_indices.append(int(token[3:]))
        elif token.isdigit():
            inventory_count = len(dungeon.inventory_lines(state))
            equipment_indices.append(int(token) - inventory_count - 1)
    if not equipment_indices:
        return "請選擇要換上的裝備。"
    messages = []
    inventory_count = len(dungeon.inventory_lines(state))
    selected = []
    for equipment_index in equipment_indices:
        if 0 <= equipment_index < len(state.get("equipment_bag", [])):
            selected.append(state["equipment_bag"][equipment_index])
    if not selected:
        return "找不到選擇的裝備。"
    for item in selected:
        for current_index, current_item in enumerate(state.get("equipment_bag", [])):
            if current_item is item:
                messages.append(dungeon.equip_item(state, inventory_count + current_index + 1))
                break
    return "\n\n".join(messages)


async def run_dungeon_button_action(interaction, action, value=None):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)

    narrate = False
    narration_kind = "事件"
    if action == "choose":
        text = dungeon.choose_event(state, int(value))
        narrate = True
        narration_kind = "探索選擇"
    elif action == "attack":
        text = dungeon.attack(state)
        narrate = True
        narration_kind = "戰鬥行動"
    elif action == "run":
        text = dungeon.run_away(state)
        narrate = True
        narration_kind = "逃跑行動"
    elif action == "use":
        mode_before = state.get("mode")
        text = use_items_from_selection(state, str(value))
        if mode_before in {"battle", "encounter"}:
            narrate = True
            narration_kind = "戰鬥道具"
    elif action == "open":
        text = dungeon.open_chest(state)
    elif action == "abandon":
        text = dungeon.abandon_chest(state)
    elif action == "buy":
        text = dungeon.buy_items(state, str(value))
    elif action == "sell":
        text = dungeon.sell_items(state, str(value))
    elif action == "equip":
        text = equip_items_from_selection(state, str(value))
    elif action == "bag":
        state["_ui_mode"] = "bag"
        text = dungeon.bag_text(state)
    elif action == "refresh":
        state.pop("_ui_mode", None)
        text = dungeon.current_prompt(state)
    elif action == "leave_shop":
        text = dungeon.leave_shop(state)
    else:
        text = "未知的地城操作。"
    if action not in {"bag"}:
        state.pop("_ui_mode", None)
    await send_dungeon_result(interaction, state, text, narrate=narrate, narration_kind=narration_kind)


class DungeonButton(discord.ui.Button):
    def __init__(self, label, action, value=None, style=discord.ButtonStyle.secondary):
        super().__init__(label=label[:80], style=style)
        self.action = action
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        await run_dungeon_button_action(interaction, self.action, self.value)


class DungeonSelect(discord.ui.Select):
    def __init__(self, placeholder, options, action, row=None, max_values=1):
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=max(1, min(max_values, len(options))),
            options=options,
            row=row,
        )
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        await run_dungeon_button_action(interaction, self.action, " ".join(self.values))


class DungeonView(discord.ui.View):
    def __init__(self, state):
        super().__init__(timeout=None)
        self.state = state
        self.build()

    def build(self):
        if self.state.get("_ui_mode") == "bag":
            self.add_bag_controls()
            self.add_item(DungeonButton("返回", "refresh", style=discord.ButtonStyle.secondary))
            return
        mode = self.state.get("mode")
        if mode == "explore":
            self.add_explore_buttons()
            self.add_item_select_if_available(row=2)
        elif mode == "encounter":
            self.add_combat_buttons(include_smoke=True)
        elif mode == "battle":
            self.add_combat_buttons(include_smoke=False)
        elif mode == "chest":
            self.add_item(DungeonButton("開啟寶箱", "open", style=discord.ButtonStyle.primary))
            self.add_item(DungeonButton("放棄", "abandon", style=discord.ButtonStyle.secondary))
            self.add_item_select_if_available(row=1)
        elif mode == "shop":
            self.add_shop_controls()

    def add_explore_buttons(self):
        if self.state.get("step", 0) >= 5:
            return
        options = self.state["floor_events"][self.state["step"]]
        reveal_count = dungeon.reveal_count_for_state(self.state)
        torch = self.state.get("torch_reveal_next", False)
        for index, event in enumerate(options, 1):
            if self.state.get("map_revealed") or torch or event["type"] == "商人" or index <= reveal_count:
                label = event["type"]
            else:
                label = dungeon.EVENT_HINTS.get(event["type"], "???")
            button = DungeonButton(f"{index}. {label}", "choose", index, discord.ButtonStyle.primary)
            button.row = 0 if index <= 3 else 1
            self.add_item(button)
        bag_button = DungeonButton("背包", "bag", style=discord.ButtonStyle.success)
        bag_button.row = 1
        self.add_item(bag_button)

    def add_combat_buttons(self, include_smoke):
        attack_label = "戰鬥" if include_smoke else "攻擊"
        self.add_item(DungeonButton(attack_label, "attack", style=discord.ButtonStyle.danger))
        self.add_item(DungeonButton("逃跑", "run", style=discord.ButtonStyle.secondary))
        self.add_item(DungeonButton("背包", "bag", style=discord.ButtonStyle.success))
        item_options = inventory_select_options(self.state)
        if item_options:
            self.add_item(DungeonSelect("勾選要使用的道具", item_options, "use", row=2, max_values=len(item_options)))
        if include_smoke:
            smoke_index = inventory_item_index(self.state, "煙霧彈")
            if smoke_index:
                self.add_item(DungeonButton("煙霧彈", "use", smoke_index, discord.ButtonStyle.success))

    def add_shop_controls(self):
        buy_options = []
        for index, good in enumerate(self.state.get("shop") or [], 1):
            if good.get("sold"):
                continue
            label = shop_option_label(index, good)
            buy_options.append(discord.SelectOption(label=label[:100], value=str(index)))
        if buy_options:
            buy_options = buy_options[:25]
            self.add_item(DungeonSelect("勾選要購買的商品", buy_options, "buy", row=0, max_values=len(buy_options)))

        sell_options = sell_select_options(self.state)
        if sell_options:
            sell_options = sell_options[:25]
            self.add_item(DungeonSelect("勾選要販售的物品", sell_options, "sell", row=1, max_values=len(sell_options)))
        self.add_item_select_if_available(row=2)
        leave = DungeonButton("離開商店", "leave_shop", style=discord.ButtonStyle.secondary)
        leave.row = 3
        self.add_item(leave)

    def add_bag_controls(self):
        item_options = inventory_select_options(self.state)
        if item_options:
            self.add_item(DungeonSelect("勾選要使用的道具", item_options, "use", row=0, max_values=len(item_options)))

        equip_options = equipment_select_options(self.state)
        if equip_options:
            self.add_item(DungeonSelect("勾選要換上的裝備", equip_options, "equip", row=1, max_values=len(equip_options)))

    def add_item_select_if_available(self, row=None):
        item_options = inventory_select_options(self.state)
        if item_options:
            self.add_item(DungeonSelect("勾選要使用的道具", item_options, "use", row=row, max_values=len(item_options)))


def create_dungeon_view(state):
    view = DungeonView(state)
    return view if view.children else None


def inventory_item_index(state, name):
    for index, (item_name, _) in enumerate(dungeon.inventory_lines(state), 1):
        if item_name == name:
            return index
    return None


def inventory_select_options(state):
    options = []
    expanded_index = 1
    usable_items = {"回復藥", "高級回復藥", "解毒藥", "止血繃帶", "萬靈藥", "煙霧彈", "火把", "地圖"}
    for index, (name, qty) in enumerate(dungeon.inventory_lines(state), 1):
        if name not in usable_items:
            continue
        for copy_index in range(1, qty + 1):
            suffix = f" #{copy_index}" if qty > 1 else ""
            options.append(
                discord.SelectOption(
                    label=f"{expanded_index}. {name}{suffix}"[:100],
                    description=dungeon.format_item_description(name)[:100],
                    value=f"{index}:{copy_index}",
                )
            )
            expanded_index += 1
    return options[:25]


def sell_select_options(state):
    options = []
    inventory = dungeon.inventory_lines(state)
    for index, (name, qty) in enumerate(inventory, 1):
        price = int(dungeon.ITEMS.get(name, {"price": 0})["price"] * 0.5)
        options.append(
            discord.SelectOption(
                label=f"{index}. {name} x{qty}（賣{price}G/個）"[:100],
                description=dungeon.format_item_description(name)[:100],
                value=str(index),
            )
        )
    start = len(inventory) + 1
    for index, item in enumerate(state.get("equipment_bag", []), start):
        price = int(item.get("price", dungeon.estimated_equipment_price(item)) * 0.5)
        options.append(
            discord.SelectOption(
                label=f"{index}. {item['name']}（賣{price}G）"[:100],
                description=dungeon.format_equipment(item)[:100],
                value=str(index),
            )
        )
    return options[:25]


def equipment_select_options(state):
    options = []
    start = len(dungeon.inventory_lines(state)) + 1
    for bag_index, item in enumerate(state.get("equipment_bag", [])):
        display_index = start + bag_index
        options.append(
            discord.SelectOption(
                label=f"{display_index}. {item['name']}"[:100],
                description=dungeon.format_equipment(item)[:100],
                value=f"eq:{bag_index}",
            )
        )
    return options[:25]


def shop_option_label(index, good):
    if good["kind"] == "item":
        qty = f"x{good.get('qty', 1)} " if good.get("qty", 1) > 1 else ""
        return f"{index}. {good['name']} {qty}{good['price']}G"
    if good["kind"] == "backpack":
        return f"{index}. {good['name']} {good['price']}G"
    return f"{index}. {good['name']} {good['price']}G"


class HomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="進入地城", style=discord.ButtonStyle.success, custom_id="home_enter_dungeon")
    async def enter_dungeon(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await reject_wrong_interaction(interaction):
            return
        await defer_interaction(interaction)
        state, message = load_dungeon_or_message(interaction)
        if message:
            await send_interaction_text(
                interaction,
                message + "\n\n如果是第一次測試，請先使用 `/開始` 建立共享冒險者。",
            )
            return
        set_dungeon_actor(state, interaction)
        await send_dungeon_result(interaction, state, dungeon.status_text(state))


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    traceback.print_exception(type(error), error, error.__traceback__)
    message = f"地城指令發生錯誤：{error}"
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="測試", description="測試 slash command 是否正常回應")
async def dungeon_ping(interaction: discord.Interaction):
    print(">> /測試 callback entered <<")
    await interaction.response.send_message("地城 slash command OK")


@bot.tree.command(name="開始", description="建立新的地城冒險者")
@app_commands.describe(reset="已有存檔時是否重新開始")
@app_commands.rename(reset="重置")
async def dungeon_start(interaction: discord.Interaction, reset: bool = False):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    session_id = dungeon_session_id(interaction)
    existing = load_player(session_id)
    if existing and not reset:
        await send_interaction_text(
            interaction,
            "你已經有冒險進度。\n"
            "查看狀態：`/狀態`\n"
            "繼續探索：`/探索`\n"
            "若要重來，請使用 `/開始 重置:True`。",
        )
        return
    if reset:
        delete_player(session_id)
    state = dungeon.new_player(session_id, dungeon_session_name(interaction))
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.reset_message(state))


@bot.tree.command(name="狀態", description="查看目前的冒險者狀態")
async def dungeon_status(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    await send_interaction_text(interaction, dungeon.status_text(state), view=create_dungeon_view(state))


@bot.tree.command(name="旁白", description="開啟或關閉 AI GM 旁白")
@app_commands.describe(enabled="是否開啟 AI 旁白")
@app_commands.rename(enabled="開啟")
async def dungeon_narration_toggle(interaction: discord.Interaction, enabled: bool):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    state["gm_narration_enabled"] = bool(enabled)
    save_player(state)
    status = "開啟" if enabled else "關閉"
    await send_interaction_text(
        interaction,
        f"AI GM 旁白已{status}。\n模型：`{DUNGEON_GM_MODEL}`\n如果 Ollama 沒回應，遊戲會自動使用原本文字。",
        view=create_dungeon_view(state),
    )


@bot.tree.command(name="問", description="詢問 AI GM 目前地城狀況")
@app_commands.describe(question="想問 GM 的地城問題")
@app_commands.rename(question="問題")
async def dungeon_ask_gm(interaction: discord.Interaction, question: str):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    answer = await asyncio.to_thread(
        dungeon_ai.answer_gm_question,
        build_gm_chat_context(state),
        question,
        DUNGEON_GM_MODEL,
    )
    if not answer:
        answer = "GM暫時沉默了。請確認 Ollama 是否啟動，或稍後再問。"
    await send_interaction_text(
        interaction,
        f"**問題：**{question}\n\n**アロナ:**\n{answer}",
        view=create_dungeon_view(state),
    )


@bot.tree.command(name="探索", description="查看目前可選擇的探索事件")
async def dungeon_explore(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.explore_text(state))


@bot.tree.command(name="選擇", description="選擇目前步數中的事件")
@app_commands.describe(number="事件編號 1 到 5")
@app_commands.rename(number="編號")
async def dungeon_choose(interaction: discord.Interaction, number: app_commands.Range[int, 1, 5]):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(
        interaction,
        state,
        dungeon.choose_event(state, int(number)),
        narrate=True,
        narration_kind="探索選擇",
    )


@bot.tree.command(name="攻擊", description="在戰鬥中攻擊敵人")
async def dungeon_attack(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.attack(state), narrate=True, narration_kind="戰鬥行動")


@bot.tree.command(name="逃跑", description="在戰鬥中嘗試逃跑")
async def dungeon_run(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.run_away(state), narrate=True, narration_kind="逃跑行動")


@bot.tree.command(name="背包", description="查看背包、道具與備用裝備")
async def dungeon_bag(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    state["_ui_mode"] = "bag"
    await send_dungeon_result(interaction, state, dungeon.bag_text(state))


@bot.tree.command(name="使用", description="使用背包中的道具")
@app_commands.describe(number="道具編號")
@app_commands.rename(number="編號")
async def dungeon_use(interaction: discord.Interaction, number: app_commands.Range[int, 1, 99]):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    mode_before = state.get("mode")
    await send_dungeon_result(
        interaction,
        state,
        dungeon.use_item(state, int(number)),
        narrate=mode_before in {"battle", "encounter"},
        narration_kind="戰鬥道具",
    )


@bot.tree.command(name="裝備", description="裝備背包中的備用武器、防具或飾品")
@app_commands.describe(number="備用裝備編號")
@app_commands.rename(number="編號")
async def dungeon_equip(interaction: discord.Interaction, number: app_commands.Range[int, 1, 99]):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.equip_item(state, int(number)))


@bot.tree.command(name="商店", description="查看目前商人販售的商品")
async def dungeon_shop(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    await send_interaction_text(interaction, dungeon.shop_text(state), view=create_dungeon_view(state))


@bot.tree.command(name="購買", description="購買商店中的商品，可輸入多個編號")
@app_commands.describe(number="商品編號，例如 1 或 1 2 4")
@app_commands.rename(number="編號")
async def dungeon_buy(interaction: discord.Interaction, number: str):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.buy_items(state, number))


@bot.tree.command(name="販售", description="販售背包中的道具或備用裝備，可輸入多個編號")
@app_commands.describe(number="背包編號，例如 1 或 1 3")
@app_commands.rename(number="編號")
async def dungeon_sell(interaction: discord.Interaction, number: str):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.sell_items(state, number))


@bot.tree.command(name="開啟", description="使用寶箱鑰匙開啟目前的寶箱")
async def dungeon_open(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.open_chest(state))


@bot.tree.command(name="放棄", description="放棄目前的寶箱")
async def dungeon_abandon(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.abandon_chest(state))


@bot.tree.command(name="離開商店", description="離開目前的商店")
async def dungeon_leave_shop(interaction: discord.Interaction):
    if await reject_wrong_interaction(interaction):
        return
    await defer_interaction(interaction)
    state, message = load_dungeon_or_message(interaction)
    if message:
        await send_interaction_text(interaction, message)
        return
    set_dungeon_actor(state, interaction)
    await send_dungeon_result(interaction, state, dungeon.leave_shop(state))


@bot.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx):
    if await reject_wrong_channel(ctx):
        return
    await ctx.reply("收到，アロナ 下線。 BYE~")
    await bot.close()


@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.reply("這個指令只允許 bot owner 使用。")
    else:
        await ctx.reply(f"關閉指令發生錯誤：{error}")


def main():
    token = os.getenv(TOKEN_ENV)
    if not token:
        raise RuntimeError(f"Missing {TOKEN_ENV}. Set it before running this bot.")
    bot.run(token)


if __name__ == "__main__":
    main()
