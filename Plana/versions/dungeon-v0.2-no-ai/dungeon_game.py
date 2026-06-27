import random
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


MID_BOSS_FLOORS = {3, 7, 13, 17, 23}
BOSS_FLOORS = {5, 10, 15, 20}
MERCHANT_FLOORS = {3, 5, 7, 10, 13, 15, 17, 20, 23}
MAX_FLOOR = 25
TAIWAN_TZ = timezone(timedelta(hours=8))

ITEMS = {
    "回復藥": {"price": 20, "heal": 20},
    "高級回復藥": {"price": 60, "heal": 50},
    "解毒藥": {"price": 20},
    "止血繃帶": {"price": 50, "heal": 10},
    "萬靈藥": {"price": 120, "heal": 30},
    "火把": {"price": 25},
    "地圖": {"price": 100},
    "寶箱鑰匙": {"price": 30},
    "煙霧彈": {"price": 40},
    "鳳凰羽毛": {"price": 0},
}

WEAPONS = {
    "木劍": {"kind": "weapon", "name": "木劍", "min": 3, "max": 5, "price": 40},
    "木棒": {"kind": "weapon", "name": "木棒", "min": 1, "max": 6, "price": 45},
    "短刀": {"kind": "weapon", "name": "短刀", "min": 2, "max": 6, "price": 55},
    "銅劍": {"kind": "weapon", "name": "銅劍", "min": 2, "max": 7, "price": 80},
}

ARMORS = {
    "布衣": {"kind": "armor", "name": "布衣", "defense": 1, "price": 30},
    "皮甲": {"kind": "armor", "name": "皮甲", "defense": 2, "price": 70},
    "厚布衣": {"kind": "armor", "name": "厚布衣", "defense": 3, "price": 90},
}

ACCESSORIES = {
    "力量戒指": {"kind": "accessory", "name": "力量戒指", "attack_bonus": 1, "price": 150},
    "守護戒指": {"kind": "accessory", "name": "守護戒指", "defense_bonus": 1, "price": 150},
    "生命護符": {"kind": "accessory", "name": "生命護符", "max_hp_bonus": 20, "price": 180},
    "抗毒護符": {"kind": "accessory", "name": "抗毒護符", "immunities": ["中毒"], "price": 160},
    "抗火護符": {"kind": "accessory", "name": "抗火護符", "immunities": ["燒傷"], "price": 160},
    "抗麻護符": {"kind": "accessory", "name": "抗麻護符", "immunities": ["麻痺"], "price": 180},
    "黃金戒指": {"kind": "accessory", "name": "黃金戒指", "gold_bonus": 0.2, "price": 220},
    "商人之戒": {"kind": "accessory", "name": "商人之戒", "sell_bonus": 0.2, "price": 220},
    "吸血護符": {"kind": "accessory", "name": "吸血護符", "kill_heal": 3, "price": 220},
    "冒險者指南針": {"kind": "accessory", "name": "冒險者指南針", "extra_reveal": 1, "price": 250},
    "幸運硬幣": {"kind": "accessory", "name": "幸運硬幣", "mimic_reduction": 0.05, "price": 250},
    "尋寶護符": {"kind": "accessory", "name": "尋寶護符", "money_bonus": 0.5, "price": 220},
}

MID_BOSS_DROPS = [
    {"kind": "weapon", "name": "哥布林巨棒", "min": 2, "max": 10, "price": 180, "boss": True},
    {"kind": "armor", "name": "哥布林掠奪皮裝", "defense": 6, "price": 180, "boss": True},
    {
        "kind": "accessory",
        "name": "哥布林酋長頭飾",
        "attack_bonus": 2,
        "defense_bonus": 1,
        "price": 250,
        "boss": True,
    },
]

BOSS_DROPS = [
    {"kind": "weapon", "name": "哥布林王巨劍", "min": 2, "max": 13, "price": 280, "boss": True},
    {"kind": "armor", "name": "哥布林王新衣", "defense": 8, "price": 280, "boss": True},
    {
        "kind": "accessory",
        "name": "人骨手環",
        "attack_bonus": 1,
        "defense_bonus": 1,
        "max_hp_bonus": 20,
        "price": 320,
        "boss": True,
    },
]

NORMAL_MONSTERS = [
    {
        "name": "史萊姆",
        "type": "普通怪",
        "weight": 20,
        "hp": 8,
        "attack": [1, 3],
        "gold": [3, 5],
        "drops": [],
    },
    {
        "name": "哥布林",
        "type": "普通怪",
        "weight": 18,
        "hp": 12,
        "attack": [2, 4],
        "gold": [5, 8],
        "drops": [{"chance": 0.05, "type": "weapon"}, {"chance": 0.05, "type": "armor"}],
    },
    {
        "name": "骷髏兵",
        "type": "普通怪",
        "weight": 15,
        "hp": 11,
        "attack": [3, 5],
        "gold": [6, 10],
        "drops": [{"chance": 0.05, "type": "weapon"}],
    },
    {
        "name": "殭屍",
        "type": "普通怪",
        "weight": 15,
        "hp": 12,
        "attack": [2, 4],
        "gold": [5, 8],
        "status": {"name": "麻痺", "chance": 0.10},
        "drops": [{"chance": 0.05, "type": "armor"}],
    },
    {
        "name": "鬼火",
        "type": "普通怪",
        "weight": 12,
        "hp": 10,
        "attack": [2, 4],
        "gold": [5, 8],
        "status": {"name": "燒傷", "chance": 0.10},
        "drops": [{"chance": 0.05, "type": "item", "name": "火把"}],
    },
    {
        "name": "毒蜘蛛",
        "type": "普通怪",
        "weight": 12,
        "hp": 10,
        "attack": [2, 4],
        "gold": [5, 8],
        "status": {"name": "中毒", "chance": 0.10},
        "drops": [{"chance": 0.05, "type": "item", "name": "解毒藥"}],
    },
    {
        "name": "盜賊",
        "type": "普通怪",
        "weight": 8,
        "hp": 11,
        "attack": [3, 5],
        "gold": [8, 15],
        "preemptive": True,
        "drops": [{"chance": 0.10, "type": "gold_bag"}],
    },
]

ELITE_MONSTERS = [
    {
        "name": "哥布林隊長",
        "type": "精英怪",
        "weight": 30,
        "hp": 25,
        "attack": [4, 7],
        "gold": [20, 30],
        "drops": [
            {"chance": 0.20, "type": "weapon"},
            {"chance": 0.20, "type": "armor"},
            {"chance": 0.05, "type": "accessory"},
        ],
    },
    {
        "name": "巨型蜘蛛",
        "type": "精英怪",
        "weight": 25,
        "hp": 22,
        "attack": [4, 7],
        "gold": [20, 30],
        "status": {"name": "中毒", "chance": 0.30},
        "drops": [
            {"chance": 0.20, "type": "weapon"},
            {"chance": 0.20, "type": "armor"},
            {"chance": 0.05, "type": "accessory"},
            {"chance": 0.10, "type": "item", "name": "解毒藥"},
        ],
    },
    {
        "name": "大鬼火",
        "type": "精英怪",
        "weight": 25,
        "hp": 22,
        "attack": [4, 7],
        "gold": [20, 30],
        "status": {"name": "燒傷", "chance": 0.30},
        "drops": [
            {"chance": 0.20, "type": "weapon"},
            {"chance": 0.20, "type": "armor"},
            {"chance": 0.05, "type": "accessory"},
            {"chance": 0.10, "type": "item", "name": "火把"},
        ],
    },
    {
        "name": "屍群",
        "type": "精英怪",
        "weight": 20,
        "hp": 28,
        "attack": [4, 7],
        "gold": [20, 30],
        "status": {"name": "麻痺", "chance": 0.15},
        "drops": [
            {"chance": 0.20, "type": "weapon"},
            {"chance": 0.20, "type": "armor"},
            {"chance": 0.05, "type": "accessory"},
        ],
    },
]

MID_BOSSES = [
    {"name": "大哥布林戰士", "type": "中Boss", "hp": 35, "attack": [5, 9], "gold": [40, 60]},
    {"name": "大哥布林勇士", "type": "中Boss", "hp": 45, "attack": [4, 7], "gold": [40, 60], "double_chance": 0.20},
    {
        "name": "哥布林部落酋長",
        "type": "中Boss",
        "hp": 40,
        "attack": [4, 7],
        "gold": [40, 60],
        "status": {"name": "麻痺", "chance": 0.25},
    },
]

GOBLIN_KING = {
    "name": "哥布林王",
    "type": "大Boss",
    "hp": 50,
    "attack": [6, 10],
    "gold": [80, 120],
    "boss": "goblin_king",
}

MIMIC = {
    "name": "銅寶箱怪",
    "type": "寶箱怪",
    "hp": 25,
    "attack": [4, 8],
    "gold": [15, 25],
    "preemptive": True,
    "mimic": True,
    "status_pool": [{"name": "麻痺", "chance": 0.20}, {"name": "流血", "chance": 0.20}],
}

EVENT_HINTS = {
    "普通怪": "似乎有影子在晃動",
    "精英怪": "似乎有影子在晃動",
    "銀色稀有怪": "似乎有影子在晃動",
    "金色稀有怪": "似乎有影子在晃動",
    "商人": "似乎有影子在晃動",
    "金錢": "似乎有什麼閃閃發光",
    "寶箱": "似乎有什麼閃閃發光",
    "道具": "似乎是安全的地方",
    "空地": "似乎是安全的地方",
    "陷阱": "似乎是安全的地方",
}


def new_player(user_id, name):
    state = {
        "user_id": str(user_id),
        "name": name,
        "mode": "explore",
        "floor": 1,
        "step": 0,
        "hp": 100,
        "base_max_hp": 100,
        "max_hp": 100,
        "gold": 0,
        "weapon": deepcopy(WEAPONS["木劍"]),
        "armor": deepcopy(ARMORS["布衣"]),
        "accessory": None,
        "bag_capacity": 15,
        "inventory": {"回復藥": 2, "寶箱鑰匙": 1},
        "equipment_bag": [],
        "statuses": {},
        "stats": {
            "normal_kills": 0,
            "elite_kills": 0,
            "boss_kills": 0,
            "items_used": {},
            "gold_earned": 0,
        },
        "has_hero_proof": False,
        "floor_events": generate_floor_events(1),
        "torch_reveal_next": False,
        "map_revealed": False,
        "battle": None,
        "encounter": None,
        "pending_chest": False,
        "shop": None,
        "last_actor": "",
        "last_message": "",
    }
    return state


def status_text(state):
    recalc_max_hp(state)
    accessory = state["accessory"]["name"] if state.get("accessory") else "無"
    statuses = "、".join(state.get("statuses", {}).keys()) or "無"
    mode = {"explore": "探索", "encounter": "遭遇", "chest": "寶箱", "battle": "戰鬥", "shop": "商店", "dead": "死亡", "cleared": "通關"}.get(
        state["mode"], state["mode"]
    )
    return (
        f"**{state['name']} 的冒險者狀態**\n"
        f"目前：第 {state['floor']} 層 / 第 {min(state['step'] + 1, 5)} 步 / {mode}\n"
        f"HP：{state['hp']} / {state['max_hp']}\n"
        f"Gold：{state['gold']}\n"
        f"武器：{format_equipment(state['weapon'])}\n"
        f"防具：{format_equipment(state['armor'])}\n"
        f"飾品：{accessory}\n"
        f"狀態：{statuses}\n"
        f"背包：{bag_used(state)} / {state['bag_capacity']}"
    )


def compact_status_line(state):
    recalc_max_hp(state)
    statuses = "、".join(format_status(name, value) for name, value in state.get("statuses", {}).items()) or "無異常"
    weapon = state["weapon"]["name"]
    armor = state["armor"]["name"]
    accessory = state["accessory"]["name"] if state.get("accessory") else "無飾品"
    return f"HP:{state['hp']}/{state['max_hp']} {statuses} G{state['gold']} {weapon} {armor} {accessory}"


def format_status(name, value):
    if name == "流血":
        if isinstance(value, dict):
            return f"流血{value.get('stacks', 1)}層{value.get('turns', 3)}回合"
        return f"流血{value}層"
    if value and value > 0:
        return f"{name}{value}回合"
    return name


def explore_text(state):
    if state["mode"] == "battle":
        return battle_prompt(state)
    if state["mode"] == "encounter":
        return encounter_prompt(state)
    if state["mode"] == "chest":
        return chest_prompt(state)
    if state["mode"] == "shop":
        return shop_text(state)
    if state["mode"] in {"dead", "cleared"}:
        return "這次冒險已經結束。可以使用 `/開始` 重新開始。"
    if state["step"] >= 5:
        return maybe_start_floor_end(state)
    return event_options_text(state)


def choose_event(state, number):
    if state["mode"] != "explore":
        return "現在不能選擇探索事件。\n\n" + current_prompt(state)
    if state["step"] >= 5:
        return maybe_start_floor_end(state)
    if number < 1 or number > 5:
        return "請選擇 1 到 5 之間的事件編號。"

    options = state["floor_events"][state["step"]]
    event = options[number - 1]
    was_torch_revealed = state.get("torch_reveal_next", False)
    reveal_count = reveal_count_for_state(state)
    state["step"] += 1
    state["torch_reveal_next"] = False

    chosen_label = event["type"] if state.get("map_revealed") or was_torch_revealed or event["type"] == "商人" or number <= reveal_count else EVENT_HINTS.get(event["type"], "???")
    actor = state.get("last_actor") or "有人"
    header = f"{actor} 選了 {number}. {chosen_label}\n"
    text = handle_event(state, event)
    if state["mode"] == "explore":
        text = text + "\n\n" + maybe_start_floor_end(state)
    return header + text


def attack(state):
    if state["mode"] == "encounter":
        monster = state["encounter"]["monster"]
        floor_end = state["encounter"].get("floor_end", False)
        state["encounter"] = None
        return start_battle(state, monster, floor_end=floor_end, started=True)
    if state["mode"] != "battle":
        return "現在沒有正在進行的戰鬥。"
    messages = []
    if apply_turn_status_damage(state, messages):
        return "\n".join(messages)

    battle = state["battle"]
    battle["started"] = True
    if state.get("statuses", {}).get("麻痺", 0):
        messages.append("你因為麻痺而無法攻擊。")
        remove_status(state, "麻痺")
    else:
        damage = player_damage(state)
        battle["enemy_hp"] = max(0, battle["enemy_hp"] - damage)
        messages.append(f"你攻擊 {battle['monster']['name']}，造成 {damage} 點傷害。")
        apply_weapon_affix(state, battle, messages)

    if battle["enemy_hp"] <= 0:
        messages.append(win_battle(state))
        return "\n".join(messages)

    monster_action(state, messages)
    if state["mode"] == "dead":
        return "\n".join(messages)
    messages.append(battle_prompt(state))
    return "\n".join(messages)


def run_away(state):
    if state["mode"] == "encounter":
        monster = state["encounter"]["monster"]
        if monster["type"] in {"大Boss", "魔王", "寶箱怪"}:
            return f"{monster['type']} 無法逃跑，只能正面迎戰。"
        if state.get("statuses", {}).get("麻痺", 0):
            return "你目前處於麻痺狀態，無法逃跑。"
        if monster["type"] == "中Boss":
            if item_count(state, "寶箱鑰匙") <= 0:
                return "中 Boss 逃跑需要寶箱鑰匙 ×1。你沒有鑰匙，只能戰鬥。"
            chance = 0.20
        elif monster["type"] == "普通怪":
            chance = 0.80
        else:
            chance = 0.50
        if random.random() < chance:
            if monster["type"] == "中Boss":
                remove_item(state, "寶箱鑰匙", 1)
            state["encounter"] = None
            state["mode"] = "explore"
            text = f"{state.get('last_actor') or '有人'} 逃離了 {monster['name']}。"
            if monster["type"] == "中Boss":
                return text + "\n\n" + advance_floor(state)
            return text + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
        state["encounter"] = None
        text = f"逃跑失敗，{monster['name']} 先攻一次！\n"
        return text + start_battle(state, monster, floor_end=False, started=True, preemptive_override=True)
    if state["mode"] != "battle":
        return "現在沒有需要逃跑的戰鬥。"
    battle = state["battle"]
    monster_type = battle["monster"]["type"]
    if state.get("statuses", {}).get("麻痺", 0):
        return "你目前處於麻痺狀態，無法逃跑。"
    if monster_type in {"大Boss", "魔王", "寶箱怪"}:
        return f"{monster_type} 無法逃跑，只能正面迎戰。"

    if monster_type == "中Boss":
        if item_count(state, "寶箱鑰匙") <= 0:
            return "中 Boss 逃跑需要寶箱鑰匙 ×1。你沒有鑰匙，只能戰鬥。"
        chance = 0.20 if not battle.get("started") else 0.10
    elif monster_type == "普通怪":
        chance = 0.80 if not battle.get("started") else 0.50
    elif monster_type == "精英怪":
        chance = 0.50 if not battle.get("started") else 0.25
    else:
        chance = 0.50

    if random.random() < chance:
        if monster_type == "中Boss":
            remove_item(state, "寶箱鑰匙", 1)
        state["battle"] = None
        state["mode"] = "explore"
        text = "逃跑成功，本次事件消失。"
        if monster_type == "中Boss":
            return text + "\n\n" + advance_floor(state)
        if state["step"] >= 5:
            return text + "\n\n" + maybe_start_floor_end(state)
        return text + "\n\n" + event_options_text(state)

    messages = ["逃跑失敗，怪物立刻攻擊！"]
    battle["started"] = True
    monster_action(state, messages)
    if state["mode"] == "dead":
        return "\n".join(messages)
    messages.append(battle_prompt(state))
    return "\n".join(messages)


def use_item(state, number):
    usable = inventory_lines(state)
    if number < 1 or number > len(usable):
        return "找不到這個道具編號。請先使用 `/背包` 查看。"
    name = usable[number - 1][0]
    in_battle = state["mode"] == "battle"
    if state["mode"] not in {"explore", "battle", "encounter"}:
        return "現在不能使用道具。"

    messages = []
    consumed = True
    if name in {"回復藥", "高級回復藥"}:
        healed = heal(state, ITEMS[name]["heal"])
        messages.append(f"你使用 {name}，恢復 {healed} HP。")
    elif name == "解毒藥":
        cleared = clear_statuses(state, {"中毒", "劇毒", "疾病"})
        messages.append(f"你使用解毒藥，解除：{cleared or '沒有可解除的狀態'}。")
    elif name == "止血繃帶":
        healed = heal(state, 10)
        cleared = clear_statuses(state, {"流血"})
        messages.append(f"你使用止血繃帶，恢復 {healed} HP，解除：{cleared or '沒有流血'}。")
    elif name == "萬靈藥":
        healed = heal(state, 30)
        state["statuses"] = {}
        messages.append(f"你使用萬靈藥，解除所有異常並恢復 {healed} HP。")
    elif name == "火把":
        if state["mode"] != "explore":
            return "火把只能在探索中使用。"
        state["torch_reveal_next"] = True
        messages.append("你點燃火把，下一步的 5 個事件將全部公開。")
    elif name == "地圖":
        if state["mode"] != "explore":
            return "地圖只能在探索中使用。"
        state["map_revealed"] = True
        messages.append("你攤開地圖，看清了本層剩餘的事件。")
        messages.append(map_text(state))
    elif name == "煙霧彈":
        if state["mode"] not in {"battle", "encounter"}:
            return "煙霧彈只能在遭遇或戰鬥中使用。"
        monster = state["battle"]["monster"] if state["mode"] == "battle" else state["encounter"]["monster"]
        monster_type = monster["type"]
        if monster_type not in {"普通怪", "精英怪"}:
            return "煙霧彈只能對普通怪與精英怪使用。"
        remove_item(state, name, 1)
        add_item_use_stat(state, name)
        state["battle"] = None
        state["encounter"] = None
        state["mode"] = "explore"
        text = "煙霧散開，你成功脫離戰鬥。"
        if state["step"] >= 5:
            return text + "\n\n" + maybe_start_floor_end(state)
        return text + "\n\n" + event_options_text(state)
    else:
        consumed = False
        messages.append("這個道具目前不能主動使用。")

    if consumed:
        remove_item(state, name, 1)
        add_item_use_stat(state, name)

    if in_battle and state["mode"] == "battle":
        monster_action(state, messages)
        if state["mode"] != "dead":
            messages.append(battle_prompt(state))
    elif state["mode"] == "explore":
        messages.append(event_options_text(state) if state["step"] < 5 else maybe_start_floor_end(state))
    elif state["mode"] == "encounter":
        messages.append(encounter_prompt(state))
    return "\n".join(messages)


def bag_text(state):
    lines = [
        f"**背包：{bag_used(state)} / {state['bag_capacity']}**",
        "道具：",
    ]
    inv = inventory_lines(state)
    if inv:
        lines.extend([f"{index}. {name} × {qty} - {format_item_description(name)}" for index, (name, qty) in enumerate(inv, 1)])
    else:
        lines.append("無")

    lines.append("\n備用裝備：")
    if state["equipment_bag"]:
        start = len(inv) + 1
        for index, item in enumerate(state["equipment_bag"], start):
            lines.append(f"{index}. {format_equipment(item)}")
    else:
        lines.append("無")
    lines.append("\n使用道具：`/使用 編號:1`")
    lines.append("裝備備用品：`/裝備 編號:1`")
    return "\n".join(lines)


def equip_item(state, number):
    inv_len = len(inventory_lines(state))
    equipment_number = number - inv_len
    if number <= inv_len:
        return "這個編號是道具，不是裝備。請用 `/使用` 使用道具。"
    if equipment_number < 1 or equipment_number > len(state["equipment_bag"]):
        return "找不到這個裝備編號。請先使用 `/背包` 查看。"
    item = state["equipment_bag"].pop(equipment_number - 1)
    slot = item["kind"]
    if slot == "weapon":
        old = state["weapon"]
        state["weapon"] = item
    elif slot == "armor":
        old = state["armor"]
        state["armor"] = item
    elif slot == "accessory":
        old = state.get("accessory")
        state["accessory"] = item
    else:
        state["equipment_bag"].append(item)
        return "這個物品不是可裝備物。"
    if old:
        state["equipment_bag"].append(old)
    recalc_max_hp(state)
    return f"已裝備 {format_equipment(item)}。\n\n" + status_text(state)


def shop_text(state):
    if state["mode"] != "shop":
        return "你目前不在商店。"
    lines = [
        compact_status_line(state),
        "",
        "**神秘商人**",
        f"Gold：{state['gold']}",
        f"背包：{bag_used(state)} / {state['bag_capacity']}",
        "",
    ]
    for index, good in enumerate(state["shop"], 1):
        sold = "（已售出）" if good.get("sold") else ""
        lines.append(f"{index}. {good_label(good)}{sold}")
    lines.append("\n購買：`/購買 編號:1`")
    lines.append("一次購買多項：`/購買 編號:1 2 4`")
    lines.append("販售背包物品：`/販售 編號:1`，編號請看 `/背包`")
    lines.append("離開：`/離開商店`")
    return "\n".join(lines)


def buy_item(state, number):
    return buy_items(state, str(number))


def buy_items(state, numbers_text):
    if state["mode"] != "shop":
        return "你目前不在商店。"
    numbers = parse_numbers(numbers_text)
    if not numbers:
        return "請輸入要購買的商品編號，例如 `/購買 編號:1 2 4`。"
    messages = []
    for number in numbers:
        if number < 1 or number > len(state["shop"]):
            messages.append(f"{number}. 找不到這個商品。")
            continue
        good = state["shop"][number - 1]
        if good.get("sold"):
            messages.append(f"{number}. {good['name']} 已售出。")
            continue
        if state["gold"] < good["price"]:
            messages.append(f"{number}. Gold 不足，無法購買 {good['name']}。")
            continue

        if good["kind"] == "backpack":
            if state["bag_capacity"] >= good["capacity"]:
                messages.append(f"{number}. 你已經擁有同級或更大的背包。")
                continue
            state["gold"] -= good["price"]
            state["bag_capacity"] = good["capacity"]
            good["sold"] = True
            messages.append(f"{number}. 購買 {good['name']}，背包容量提升為 {good['capacity']}。")
            continue

        qty = good.get("qty", 1)
        needed = qty if good["kind"] == "item" else 1
        if bag_used(state) + needed > state["bag_capacity"]:
            messages.append(f"{number}. 背包空間不足，無法購買 {good['name']}。")
            continue

        state["gold"] -= good["price"]
        good["sold"] = True
        if good["kind"] == "item":
            add_item(state, good["name"], qty)
            messages.append(f"{number}. 購買 {good['name']} × {qty}。")
            continue

        state["equipment_bag"].append(deepcopy(good["equipment"]))
        messages.append(f"{number}. 購買 {format_equipment(good['equipment'])}。可用 `/裝備` 換上。")
    messages.append(f"\n剩餘 Gold：{state['gold']}")
    return "\n".join(messages)


def leave_shop(state):
    if state["mode"] != "shop":
        return "你目前不在商店。"
    state["shop"] = None
    state["mode"] = "explore"
    text = "你離開了商人，身後的燈火很快消失在地城深處。"
    if state["step"] >= 5:
        return text + "\n\n" + maybe_start_floor_end(state)
    return text + "\n\n" + event_options_text(state)


def reset_message(state):
    return (
        "新的冒險已建立。\n\n"
        + status_text(state)
        + "\n\n"
        + event_options_text(state)
    )


def current_prompt(state):
    if state["mode"] == "battle":
        return battle_prompt(state)
    if state["mode"] == "encounter":
        return encounter_prompt(state)
    if state["mode"] == "chest":
        return chest_prompt(state)
    if state["mode"] == "shop":
        return shop_text(state)
    return event_options_text(state) if state["step"] < 5 else maybe_start_floor_end(state)


def handle_event(state, event):
    event_type = event["type"]
    if event_type == "普通怪":
        return start_encounter(state, choose_weighted(NORMAL_MONSTERS))
    if event_type == "精英怪":
        return start_encounter(state, choose_weighted(ELITE_MONSTERS))
    if event_type == "銀色稀有怪":
        monster = {"name": "銀色稀有怪", "type": "普通怪", "hp": 12, "attack": [1, 2], "gold": [50, 80]}
        return start_encounter(state, monster)
    if event_type == "金色稀有怪":
        monster = {"name": "金色稀有怪", "type": "普通怪", "hp": 18, "attack": [1, 3], "gold": [120, 200]}
        return start_encounter(state, monster)
    if event_type == "金錢":
        gold = money_event_gold(state)
        gain_gold(state, gold)
        return f"你在角落發現一個破舊錢袋，獲得 {gold} Gold。"
    if event_type == "道具":
        item = random.choice(["回復藥", "解毒藥", "火把", "寶箱鑰匙", "煙霧彈"])
        if not add_item_checked(state, item, 1):
            return f"你找到 {item}，但背包已滿，只能放棄。"
        return f"你在石縫旁找到 {item} ×1。"
    if event_type == "寶箱":
        state["mode"] = "chest"
        state["pending_chest"] = True
        return chest_prompt(state)
    if event_type == "陷阱":
        return trigger_trap(state)
    if event_type == "空地":
        healed = heal(state, 10)
        return f"你找到一處安靜空地，短暫休息後恢復 {healed} HP。"
    if event_type == "商人":
        state["mode"] = "shop"
        state["shop"] = generate_shop(state["floor"])
        return "你遇見一位披著斗篷的神秘商人。\n\n" + shop_text(state)
    return "這裡什麼也沒有。"


def start_encounter(state, monster, floor_end=False):
    state["mode"] = "encounter"
    state["encounter"] = {"monster": deepcopy(monster), "floor_end": floor_end}
    return encounter_prompt(state)


def encounter_prompt(state):
    encounter = state.get("encounter")
    if not encounter:
        state["mode"] = "explore"
        return current_prompt(state)
    monster = encounter["monster"]
    smoke = "\n3. 使用煙霧彈：`/使用 編號:煙霧彈的背包編號`" if item_count(state, "煙霧彈") > 0 and monster["type"] in {"普通怪", "精英怪"} else ""
    escape = "2. 逃跑：`/逃跑`" if monster["type"] not in {"大Boss", "魔王", "寶箱怪"} else "2. 逃跑：不可逃跑"
    return (
        f"{compact_status_line(state)}\n\n"
        f"遭遇 {monster['name']}（{monster['type']}）！\n"
        "1. 戰鬥：`/攻擊`\n"
        f"{escape}"
        f"{smoke}"
    )


def chest_prompt(state):
    if item_count(state, "寶箱鑰匙") <= 0:
        state["pending_chest"] = False
        state["mode"] = "explore"
        return "你發現寶箱，但沒有寶箱鑰匙，只能放棄。\n\n" + (
            maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state)
        )
    return (
        f"{compact_status_line(state)}\n\n"
        "你發現一個上鎖的寶箱。\n"
        "1. 使用寶箱鑰匙：`/開啟`\n"
        "2. 放棄寶箱：`/放棄`"
    )


def abandon_chest(state):
    if state["mode"] != "chest":
        return "現在沒有可放棄的寶箱。"
    state["pending_chest"] = False
    state["mode"] = "explore"
    text = f"{state.get('last_actor') or '有人'} 放棄了寶箱。"
    return text + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))


def open_chest(state):
    if state["mode"] != "chest" or not state.get("pending_chest"):
        return "現在沒有可以開啟的寶箱。"
    if item_count(state, "寶箱鑰匙") <= 0:
        state["pending_chest"] = False
        state["mode"] = "explore"
        return "你沒有寶箱鑰匙，只能放棄寶箱。\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    remove_item(state, "寶箱鑰匙", 1)
    add_item_use_stat(state, "寶箱鑰匙")
    state["pending_chest"] = False
    state["mode"] = "explore"
    mimic_chance = max(0.01, 0.10 - accessory_value(state, "mimic_reduction", 0))
    if random.random() < mimic_chance:
        return "寶箱鑰匙喀一聲斷開，寶箱突然張開利齒！\n\n" + start_battle(state, MIMIC, started=True)

    reward_type = weighted_choice(
        [("道具", 25), ("金錢", 20), ("武器", 25), ("防具", 15), ("飾品", 10), ("特殊物品", 5)]
    )
    if reward_type == "道具":
        item = random.choice(["回復藥", "高級回復藥", "解毒藥", "火把", "地圖", "煙霧彈", "寶箱鑰匙"])
        return reward_item(state, item, 1, "寶箱裡放著") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    if reward_type == "金錢":
        gold = random.randint(30, 100)
        gain_gold(state, gold)
        return f"寶箱裡裝著 {gold} Gold。\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    if reward_type == "武器":
        item = make_chest_weapon()
        return reward_equipment(state, item, "寶箱裡躺著") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    if reward_type == "防具":
        item = make_chest_armor()
        return reward_equipment(state, item, "寶箱裡躺著") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    if reward_type == "飾品":
        item = deepcopy(random.choice(list(ACCESSORIES.values())))
        return reward_equipment(state, item, "寶箱裡躺著") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    if item_count(state, "鳳凰羽毛") >= 1:
        return reward_item(state, "高級回復藥", 1, "寶箱裡放著") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))
    return reward_item(state, "鳳凰羽毛", 1, "寶箱裡散發光芒的是") + "\n\n" + (maybe_start_floor_end(state) if state["step"] >= 5 else event_options_text(state))


def trigger_trap(state):
    if random.random() < 0.60:
        return "你察覺地板機關，敏捷地避開了陷阱。"
    trap_type = random.choice(["damage", "gold", "item"])
    if trap_type == "damage":
        damage = random.randint(5, 15)
        state["hp"] -= damage
        text = f"暗箭從牆縫射出，你受到 {damage} 點傷害。"
        if state["hp"] <= 0:
            return text + "\n\n" + handle_death(state)
        return text
    if trap_type == "gold" and state["gold"] > 0:
        lost = min(state["gold"], random.randint(5, 25))
        state["gold"] -= lost
        return f"地面崩落，你遺失了 {lost} Gold。"
    inv = inventory_lines(state)
    if inv:
        item = random.choice(inv)[0]
        remove_item(state, item, 1)
        return f"你被迫丟下了 {item} ×1 才逃出陷阱。"
    return "陷阱擦身而過，所幸你沒有損失。"


def maybe_start_floor_end(state):
    if state["mode"] != "explore":
        return current_prompt(state)
    floor = state["floor"]
    if state["step"] < 5:
        return event_options_text(state)
    if floor in MID_BOSS_FLOORS:
        boss = deepcopy(random.choice(MID_BOSSES))
        return "你抵達樓層盡頭，中 Boss 擋住了道路。\n\n" + start_encounter(state, boss, floor_end=True)
    if floor in BOSS_FLOORS:
        if floor == 5:
            return "你踏上王座前的石階，哥布林王正在等待挑戰者。\n\n" + start_battle(
                state, deepcopy(GOBLIN_KING), floor_end=True, started=True
            )
        return advance_floor(state)
    if floor == MAX_FLOOR:
        return "最終魔王尚未在第一版開放。"
    return advance_floor(state)


def advance_floor(state):
    if state["floor"] >= 5:
        state["mode"] = "cleared"
        state["has_hero_proof"] = False
        return first_area_clear_text(state)
    state["floor"] += 1
    state["step"] = 0
    state["floor_events"] = generate_floor_events(state["floor"])
    state["torch_reveal_next"] = False
    state["map_revealed"] = False
    state["battle"] = None
    state["shop"] = None
    state["mode"] = "explore"
    return f"你找到通往下一層的樓梯，抵達第 {state['floor']} 層。\n\n" + event_options_text(state)


def start_battle(state, monster, floor_end=False, started=False, preemptive_override=False):
    monster = deepcopy(monster)
    state["mode"] = "battle"
    state["battle"] = {
        "monster": monster,
        "enemy_hp": monster["hp"],
        "enemy_max_hp": monster["hp"],
        "started": started,
        "floor_end": floor_end,
        "goblin_king_enraged": False,
    }
    messages = [f"遭遇 {monster['name']}！"]
    if monster.get("preemptive") or preemptive_override:
        messages.append(f"{monster['name']} 先制攻擊！")
        monster_action(state, messages)
    if state["mode"] == "dead":
        return "\n".join(messages)
    messages.append(battle_prompt(state))
    return "\n".join(messages)


def battle_prompt(state):
    battle = state["battle"]
    if not battle:
        return current_prompt(state)
    monster = battle["monster"]
    return (
        f"{compact_status_line(state)}\n\n"
        f"**戰鬥中：{monster['name']}**\n"
        f"敵方 HP：{battle['enemy_hp']} / {battle['enemy_max_hp']}\n"
        f"你的 HP：{state['hp']} / {state['max_hp']}\n"
        "1. 攻擊：`/攻擊`\n"
        "2. 使用道具：`/使用 編號:1`\n"
        "3. 逃跑：`/逃跑`"
    )


def win_battle(state):
    battle = state["battle"]
    monster = battle["monster"]
    gold = random.randint(*monster.get("gold", [0, 0]))
    if accessory_value(state, "gold_bonus", 0) and monster["type"] in {"普通怪", "精英怪", "中Boss", "大Boss"}:
        gold = int(gold * (1 + accessory_value(state, "gold_bonus", 0)))
    gain_gold(state, gold)
    messages = [f"你擊敗了 {monster['name']}，獲得 {gold} Gold。"]

    if monster["type"] == "普通怪":
        state["stats"]["normal_kills"] += 1
    elif monster["type"] == "精英怪":
        state["stats"]["elite_kills"] += 1
    else:
        state["stats"]["boss_kills"] += 1

    if accessory_value(state, "kill_heal", 0):
        healed = heal(state, accessory_value(state, "kill_heal", 0))
        messages.append(f"吸血護符恢復 {healed} HP。")

    messages.extend(resolve_drops(state, monster))
    state["battle"] = None
    state["mode"] = "explore"

    if monster["type"] in {"中Boss", "大Boss"} and battle.get("floor_end"):
        if monster["type"] == "大Boss" and state["floor"] == 5:
            state["mode"] = "cleared"
            messages.append(first_area_clear_text(state))
        else:
            messages.append(advance_floor(state))
    elif state["step"] >= 5:
        messages.append(maybe_start_floor_end(state))
    else:
        messages.append(event_options_text(state))
    return "\n".join(messages)


def resolve_drops(state, monster):
    messages = []
    if monster["type"] == "中Boss" and random.random() < 0.20:
        messages.append(reward_equipment(state, random.choice(MID_BOSS_DROPS), "中 Boss 掉落"))
    if monster["type"] == "大Boss" and monster.get("boss") == "goblin_king":
        messages.append(reward_equipment(state, random.choice(BOSS_DROPS), "Boss 掉落"))
    if monster["type"] == "寶箱怪":
        item = random.choice(["回復藥", "高級回復藥", "寶箱鑰匙", "煙霧彈"])
        messages.append(reward_item(state, item, 1, "寶箱怪掉落"))

    for drop in monster.get("drops", []):
        if random.random() >= drop["chance"]:
            continue
        if drop["type"] == "item":
            messages.append(reward_item(state, drop["name"], 1, "怪物掉落"))
        elif drop["type"] == "gold_bag":
            gold = random.randint(10, 20)
            gain_gold(state, gold)
            messages.append(f"怪物掉落 Gold袋，額外獲得 {gold} Gold。")
        elif drop["type"] == "weapon":
            messages.append(reward_equipment(state, random_area_weapon(), "怪物掉落"))
        elif drop["type"] == "armor":
            messages.append(reward_equipment(state, random_area_armor(), "怪物掉落"))
        elif drop["type"] == "accessory":
            messages.append(reward_equipment(state, random.choice(list(ACCESSORIES.values())), "怪物掉落"))
    return messages


def monster_action(state, messages):
    battle = state["battle"]
    monster = battle["monster"]
    if battle.pop("skip_next", False):
        messages.append(f"{monster['name']} 因麻痺而無法行動。")
        return
    attacks = 1
    double_chance = monster.get("double_chance", 0)
    if monster.get("name") == "大哥布林勇士" and battle["enemy_hp"] < 20:
        double_chance = 0.40
    if monster.get("boss") == "goblin_king":
        if battle["enemy_hp"] <= 10 and not battle.get("goblin_king_enraged"):
            attacks = 2
            battle["goblin_king_enraged"] = True
            messages.append("哥布林王進入狂暴狀態，發動二連擊！")
        elif battle["enemy_hp"] <= 25 and random.random() < 0.15:
            apply_status(state, "麻痺", messages)
    elif double_chance and random.random() < double_chance:
        attacks = 2
        messages.append(f"{monster['name']} 發動二連擊！")

    for _ in range(attacks):
        raw = random.randint(*monster["attack"])
        damage = max(1, raw - player_defense(state))
        state["hp"] -= damage
        messages.append(f"{monster['name']} 攻擊你，造成 {damage} 點傷害。")
        if state["hp"] <= 0:
            messages.append(handle_death(state))
            return

    status = monster.get("status")
    if monster.get("name") == "哥布林部落酋長" and battle["enemy_hp"] < 20:
        status = {"name": "麻痺", "chance": 0.45}
    if status and random.random() < status["chance"]:
        apply_status(state, status["name"], messages)
    for status in monster.get("status_pool", []):
        if random.random() < status["chance"]:
            apply_status(state, status["name"], messages)


def handle_death(state):
    if item_count(state, "鳳凰羽毛") > 0:
        remove_item(state, "鳳凰羽毛", 1)
        state["hp"] = 30
        return "鳳凰羽毛發出耀眼光芒！你從死亡邊緣被拉了回來，恢復 30 HP！"
    state["hp"] = 0
    state["mode"] = "dead"
    state["battle"] = None
    return death_summary(state)


def death_summary(state):
    date = taiwan_now().strftime("%Y/%m/%d %H:%M")
    total_kills = state["stats"]["normal_kills"] + state["stats"]["elite_kills"] + state["stats"]["boss_kills"]
    return (
        "**YOU DIED**\n"
        f"到達樓層：第 {state['floor']} 層\n"
        f"結束日期：{date}\n"
        f"擊敗怪物數：{total_kills}\n"
        f"獲得 Gold：{state['stats']['gold_earned']}\n"
        "最終裝備：\n"
        f"武器：{format_equipment(state['weapon'])}\n"
        f"防具：{format_equipment(state['armor'])}\n"
        f"飾品：{state['accessory']['name'] if state.get('accessory') else '無'}"
    )


def taiwan_now():
    try:
        return datetime.now(ZoneInfo("Asia/Taipei"))
    except Exception:
        return datetime.now(TAIWAN_TZ)


def first_area_clear_text(state):
    return (
        "**第一區通關！**\n"
        "你擊敗了哥布林王，穿越哥布林區。\n"
        "目前第一版先開放 1~5 層；第二階段可接續加入 6~25 層與 AI GM。\n\n"
        + status_text(state)
    )


def event_options_text(state):
    floor = state["floor"]
    step = state["step"]
    if step >= 5:
        return maybe_start_floor_end(state)
    options = state["floor_events"][step]
    reveal_count = reveal_count_for_state(state)
    lines = [compact_status_line(state), "", f"**第 {floor} 層 / 第 {step + 1} 步**", "你看見 5 條道路："]
    for index, event in enumerate(options, 1):
        if state.get("map_revealed") or state.get("torch_reveal_next") or index <= reveal_count or event["type"] == "商人":
            label = event["type"]
        else:
            label = EVENT_HINTS.get(event["type"], "???")
        lines.append(f"{index}. {label}")
    lines.append("\n選擇：`/選擇 編號:1`")
    return "\n".join(lines)


def reveal_count_for_state(state):
    if state.get("torch_reveal_next"):
        return 5
    return 1 + int(accessory_value(state, "extra_reveal", 0))


def map_text(state):
    lines = ["**本層地圖**"]
    for step_index, events in enumerate(state["floor_events"], 1):
        labels = " / ".join(event["type"] for event in events)
        lines.append(f"第 {step_index} 步：{labels}")
    return "\n".join(lines)


def generate_floor_events(floor):
    groups = [[{"type": "普通怪"}] for _ in range(5)]
    extra = [{"type": "普通怪"} for _ in range(2)]
    elite_count = 1 if floor in MID_BOSS_FLOORS else random.randint(1, 2)
    extra.extend({"type": "精英怪"} for _ in range(elite_count))
    extra.extend({"type": "金錢"} for _ in range(6))
    extra.extend({"type": "道具"} for _ in range(3))
    extra.extend({"type": "寶箱"} for _ in range(3))
    extra.extend({"type": "陷阱"} for _ in range(2))
    while sum(len(group) for group in groups) + len(extra) < 25:
        extra.append({"type": "空地"})

    if random.randint(1, 100) == 1:
        replace_one_empty(extra, "金色稀有怪")
    elif random.randint(1, 10) == 1:
        replace_one_empty(extra, "銀色稀有怪")
    if floor in MERCHANT_FLOORS:
        replace_one_empty(extra, "商人")

    random.shuffle(extra)
    for event in extra:
        target = min(groups, key=len)
        target.append(event)
    for group in groups:
        random.shuffle(group)
    return groups


def replace_one_empty(events, event_type):
    for event in events:
        if event["type"] == "空地":
            event["type"] = event_type
            return
    if events:
        events[-1]["type"] = event_type


def generate_shop(floor):
    goods = []
    goods.append({"kind": "backpack", "name": "中背包", "capacity": 20, "price": 500})
    if floor >= 10:
        goods.append({"kind": "backpack", "name": "大背包", "capacity": 30, "price": 2000})

    goods.extend(
        [
            make_shop_equipment(random_area_weapon()),
            make_shop_equipment(random_area_armor()),
            make_shop_item("回復藥", 1),
            make_shop_item("回復藥", 1),
            make_shop_item("回復藥", 1),
            make_shop_item("解毒藥", 1),
            make_shop_item("火把", 1),
            make_shop_item("寶箱鑰匙", 1),
        ]
    )
    weighted_goods = [
        ("回復藥", 25),
        ("解毒藥", 25),
        ("火把", 25),
        ("weapon", 25),
        ("armor", 25),
        ("accessory", 15),
        ("寶箱鑰匙", 20),
        ("煙霧彈", 20),
        ("高級回復藥", 10),
        ("地圖", 5),
    ]
    while len(goods) < 15:
        pick = weighted_choice(weighted_goods)
        if pick == "weapon":
            goods.append(make_shop_equipment(random_area_weapon()))
        elif pick == "armor":
            goods.append(make_shop_equipment(random_area_armor()))
        elif pick == "accessory":
            goods.append(make_shop_equipment(random.choice(list(ACCESSORIES.values()))))
        else:
            goods.append(make_shop_item(pick, 1))
    return goods[:15]


def make_shop_item(name, qty):
    return {"kind": "item", "name": name, "qty": qty, "price": ITEMS[name]["price"] * qty}


def make_shop_equipment(equipment):
    equipment = deepcopy(equipment)
    return {"kind": equipment["kind"], "equipment": equipment, "name": equipment["name"], "price": equipment.get("price", 100)}


def good_label(good):
    if good["kind"] == "item":
        qty = f" × {good['qty']}" if good["qty"] > 1 else ""
        return f"{good['name']}{qty}（{good['price']}G，{format_item_description(good['name'])}）"
    if good["kind"] == "backpack":
        return f"{good['name']}（{good['price']}G）"
    return f"{format_equipment(good['equipment'])}（{good['price']}G）"


def sell_items(state, numbers_text):
    if state["mode"] != "shop":
        return "你目前不在商店。"
    numbers = parse_numbers(numbers_text)
    if not numbers:
        return "請輸入要販售的背包編號，例如 `/販售 編號:1 3`。"
    messages = []
    for number in sorted(set(numbers), reverse=True):
        inv = inventory_lines(state)
        if 1 <= number <= len(inv):
            name, qty = inv[number - 1]
            price = int(ITEMS.get(name, {"price": 0})["price"] * 0.5)
            if price <= 0:
                messages.append(f"{number}. {name} 無法販售。")
                continue
            remove_item(state, name, 1)
            state["gold"] += price
            messages.append(f"{number}. 賣出 {name} ×1，獲得 {price} Gold。")
            continue

        equip_index = number - len(inv)
        if 1 <= equip_index <= len(state["equipment_bag"]):
            item = state["equipment_bag"].pop(equip_index - 1)
            price = int(item.get("price", estimated_equipment_price(item)) * 0.5)
            state["gold"] += price
            messages.append(f"{number}. 賣出 {format_equipment(item)}，獲得 {price} Gold。")
            continue
        messages.append(f"{number}. 找不到這個背包物品。")
    sold_lines = list(reversed(messages))
    sold_lines.append(f"\n目前 Gold：{state['gold']}")
    return "\n".join(sold_lines)


def estimated_equipment_price(item):
    if item["kind"] == "weapon":
        return max(40, (item["min"] + item["max"]) * 12)
    if item["kind"] == "armor":
        return max(30, item["defense"] * 35)
    if item["kind"] == "accessory":
        return 180
    return 0


def parse_numbers(text):
    if isinstance(text, int):
        return [text]
    normalized = str(text).replace(",", " ").replace("，", " ").replace(".", " ")
    numbers = []
    for part in normalized.split():
        if part.isdigit():
            numbers.append(int(part))
    return numbers


def make_chest_weapon():
    item = random_area_weapon()
    item["name"] = "閃亮的" + item["name"]
    item["min"] = min(item["max"], item["min"] + 2)
    item["affix"] = random.choice(["流血", "麻痺"])
    item["price"] = int(item.get("price", 80) * 1.5)
    return item


def make_chest_armor():
    item = random_area_armor()
    item["name"] = "堅固的" + item["name"]
    item["defense"] += random.randint(1, 3)
    item["affix"] = random.choice(["抗毒", "抗燒", "抗麻", "生命"])
    if item["affix"] == "生命":
        item["max_hp_bonus"] = item.get("max_hp_bonus", 0) + 20
    else:
        item["immunities"] = {"抗毒": ["中毒"], "抗燒": ["燒傷"], "抗麻": ["麻痺"]}[item["affix"]]
    item["price"] = int(item.get("price", 80) * 1.5)
    return item


def random_area_weapon():
    return deepcopy(random.choice([WEAPONS["木棒"], WEAPONS["短刀"], WEAPONS["銅劍"]]))


def random_area_armor():
    return deepcopy(random.choice([ARMORS["皮甲"], ARMORS["厚布衣"]]))


def reward_item(state, item, qty, prefix):
    if not add_item_checked(state, item, qty):
        return f"{prefix} {item} × {qty}，但背包已滿，只能放棄。"
    return f"{prefix} {item} × {qty}。"


def reward_equipment(state, equipment, prefix):
    equipment = deepcopy(equipment)
    if bag_used(state) + 1 > state["bag_capacity"]:
        return f"{prefix} {format_equipment(equipment)}，但背包已滿，只能放棄。"
    state["equipment_bag"].append(equipment)
    return f"{prefix} {format_equipment(equipment)}。可用 `/裝備` 換上。"


def money_event_gold(state):
    if random.random() < 0.05:
        gold = random.randint(100, 200)
    else:
        gold = random.randint(10, 50)
    bonus = accessory_value(state, "money_bonus", 0)
    return int(gold * (1 + bonus))


def gain_gold(state, amount):
    state["gold"] += amount
    state["stats"]["gold_earned"] += amount


def player_damage(state):
    weapon = state["weapon"]
    return random.randint(weapon["min"], weapon["max"]) + player_attack_bonus(state)


def player_attack_bonus(state):
    return int(accessory_value(state, "attack_bonus", 0))


def player_defense(state):
    return state["armor"]["defense"] + int(accessory_value(state, "defense_bonus", 0))


def recalc_max_hp(state):
    old_max = state.get("max_hp", 100)
    max_hp = state.get("base_max_hp", 100)
    max_hp += state.get("armor", {}).get("max_hp_bonus", 0)
    if state.get("accessory"):
        max_hp += state["accessory"].get("max_hp_bonus", 0)
    state["max_hp"] = max_hp
    if state["hp"] > max_hp:
        state["hp"] = max_hp
    if max_hp > old_max and state["hp"] <= 0:
        state["hp"] = 1


def heal(state, amount):
    recalc_max_hp(state)
    before = state["hp"]
    state["hp"] = min(state["max_hp"], state["hp"] + amount)
    return state["hp"] - before


def apply_weapon_affix(state, battle, messages):
    affix = state["weapon"].get("affix")
    if not affix or random.random() >= 0.10:
        return
    if affix in {"流血", "麻痺"}:
        messages.append(f"{state['weapon']['name']} 觸發{affix}效果。")
        if affix == "流血":
            battle["enemy_hp"] = max(0, battle["enemy_hp"] - 2)
            messages.append("敵人額外受到 2 點流血傷害。")
        elif affix == "麻痺":
            battle["skip_next"] = True


def apply_status(state, status, messages):
    if status in immunities(state):
        messages.append(f"你免疫了{status}。")
        return
    durations = {"燒傷": 3, "麻痺": 1, "疾病": 5, "魅惑": 3}
    if status == "流血":
        current = state["statuses"].get(status, {"stacks": 0, "turns": 0})
        if isinstance(current, int):
            current = {"stacks": current, "turns": 3}
        state["statuses"][status] = {"stacks": min(3, current.get("stacks", 0) + 1), "turns": 3}
    else:
        state["statuses"][status] = durations.get(status, -1)
    messages.append(f"你陷入{status}狀態。")


def remove_status(state, status):
    state.get("statuses", {}).pop(status, None)


def clear_statuses(state, names):
    cleared = [name for name in names if name in state.get("statuses", {})]
    for name in cleared:
        remove_status(state, name)
    return "、".join(cleared)


def apply_turn_status_damage(state, messages):
    statuses = state.get("statuses", {})
    damage = 0
    parts = []
    if "中毒" in statuses:
        damage += 3
        parts.append("中毒3")
    if "劇毒" in statuses:
        damage += 5
        parts.append("劇毒5")
    if "燒傷" in statuses:
        damage += 3
        parts.append("燒傷3")
        tick_status(state, "燒傷")
    if "流血" in statuses:
        bleed = statuses["流血"]
        stacks = bleed.get("stacks", 1) if isinstance(bleed, dict) else bleed
        bleed_damage = 2 * stacks
        damage += bleed_damage
        parts.append(f"流血{bleed_damage}")
    if damage:
        state["hp"] -= damage
        messages.append(f"異常狀態造成 {damage} 點傷害（{'、'.join(parts)}）。")
        if state["hp"] <= 0:
            messages.append(handle_death(state))
            return True
    tick_status(state, "疾病")
    tick_status(state, "魅惑")
    tick_status(state, "流血")
    return False


def tick_status(state, status):
    if status == "流血" and status in state.get("statuses", {}):
        value = state["statuses"][status]
        if isinstance(value, dict):
            value["turns"] -= 1
            if value["turns"] <= 0:
                remove_status(state, status)
            return
    if status in state.get("statuses", {}) and isinstance(state["statuses"][status], int) and state["statuses"][status] > 0:
        state["statuses"][status] -= 1
        if state["statuses"][status] <= 0:
            remove_status(state, status)


def immunities(state):
    values = set()
    for gear in [state.get("armor"), state.get("accessory")]:
        if gear:
            values.update(gear.get("immunities", []))
    return values


def accessory_value(state, key, default):
    accessory = state.get("accessory")
    if not accessory:
        return default
    return accessory.get(key, default)


def bag_used(state):
    return sum(state.get("inventory", {}).values()) + len(state.get("equipment_bag", []))


def item_count(state, name):
    return state.get("inventory", {}).get(name, 0)


def add_item(state, name, qty):
    state.setdefault("inventory", {})
    if name == "鳳凰羽毛":
        state["inventory"][name] = min(1, state["inventory"].get(name, 0) + qty)
    else:
        state["inventory"][name] = state["inventory"].get(name, 0) + qty


def add_item_checked(state, name, qty):
    if bag_used(state) + qty > state["bag_capacity"]:
        return False
    add_item(state, name, qty)
    return True


def remove_item(state, name, qty):
    if item_count(state, name) <= qty:
        state.get("inventory", {}).pop(name, None)
    else:
        state["inventory"][name] -= qty


def add_item_use_stat(state, name):
    used = state["stats"].setdefault("items_used", {})
    used[name] = used.get(name, 0) + 1


def inventory_lines(state):
    return [(name, qty) for name, qty in state.get("inventory", {}).items() if qty > 0]


def format_equipment(item):
    if not item:
        return "無"
    if item["kind"] == "weapon":
        suffix = f"（{item['affix']}）" if item.get("affix") else ""
        return f"{item['name']}{suffix}（{item['min']}~{item['max']}）"
    if item["kind"] == "armor":
        suffix = f"（{item['affix']}）" if item.get("affix") else ""
        return f"{item['name']}{suffix}（防禦+{item['defense']}）"
    effects = []
    for key, label in [
        ("attack_bonus", "攻擊+{}"),
        ("defense_bonus", "防禦+{}"),
        ("max_hp_bonus", "最大HP+{}"),
    ]:
        if item.get(key):
            effects.append(label.format(item[key]))
    if item.get("immunities"):
        effects.append("免疫" + "/".join(item["immunities"]))
    if item.get("gold_bonus"):
        effects.append("擊敗Gold+20%")
    if item.get("money_bonus"):
        effects.append("金錢事件+50%")
    if item.get("kill_heal"):
        effects.append(f"擊敗恢復{item['kill_heal']}HP")
    return f"{item['name']}（{'、'.join(effects) or '特殊效果'}）"


def format_item_description(name):
    descriptions = {
        "回復藥": "恢復20HP",
        "高級回復藥": "恢復50HP",
        "解毒藥": "解除中毒/劇毒/疾病",
        "止血繃帶": "解除流血並恢復10HP",
        "萬靈藥": "解除所有異常並恢復30HP",
        "火把": "公開下一步全部事件",
        "地圖": "公開本層全部事件",
        "寶箱鑰匙": "開啟寶箱或中Boss逃跑",
        "煙霧彈": "普通怪/精英怪必定逃跑",
        "鳳凰羽毛": "死亡時自動復活30HP",
    }
    return descriptions.get(name, "特殊道具")


def choose_weighted(monsters):
    return deepcopy(weighted_choice([(monster, monster["weight"]) for monster in monsters]))


def weighted_choice(weighted):
    total = sum(weight for _, weight in weighted)
    roll = random.uniform(0, total)
    current = 0
    for item, weight in weighted:
        current += weight
        if roll <= current:
            return item
    return weighted[-1][0]
