#!/usr/bin/env python3
"""wubu_worm.py — WUBU WORM: The Honey Game.

GOV-42. A gamified cooperation system. Grow your worm, feed it
plastic, evolve, battle, race, and climb the ladder.

The worm is your identity. The worm is your status. The worm is
the game. The ignorant rich buy their way to big worms. The
smart poor earn their way to powerful worms. The game filters.

Commands:
  wubu_worm status <wid>           — view your worm + ladder
  wubu_worm feed <wid> <amt>       — feed plastic to your worm
  wubu_worm login <wid>            — daily login bonus
  wubu_worm do <wid> <task>        — do a task for plastic
  wubu_worm gift <wid> <rwid> <n>  — gift plastic (cooperation)
  wubu_worm battle <wid> <rwid>    — PvP cooperation duel
  wubu_worm race <wid>             — join a worm race
  wubu_worm shop <wid>             — buy plastic with pennies
  wubu_worm evolve <wid>           — evolve your worm
  wubu_worm nest <wid>             — join/create a nest (guild)
  wubu_worm leaderboard            — top worms
  wubu_worm achievements <wid>     — your badges
  wubu_worm find <wid>             — find lost plastic
  wubu_worm season                 — current season info
"""

import hashlib
import json
import os
import random
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "game")
os.makedirs(DATA, exist_ok=True)

WORM_FILE = os.path.join(DATA, "worms.json")
RACE_FILE = os.path.join(DATA, "races.json")
NEST_FILE = os.path.join(DATA, "nests.json")
SEASON_FILE = os.path.join(DATA, "season.json")

# ──────────────────────────────────────────────────────── stages ──
STAGES = {
    0: {"name": "Egg", "emoji": "🥚", "size": 1, "power": 0},
    5: {"name": "Hatchling", "emoji": "🐛", "size": 2, "power": 1},
    15: {"name": "Crawler", "emoji": "🐛", "size": 3, "power": 2},
    30: {"name": "Grower", "emoji": "🐛", "size": 4, "power": 3},
    50: {"name": "Big Worm", "emoji": "🐉", "size": 5, "power": 5},
    75: {"name": "Fat Worm", "emoji": "🐉", "size": 6, "power": 7},
    100: {"name": "Mega Worm", "emoji": "🐲", "size": 7, "power": 10},
    150: {"name": "Ultra Worm", "emoji": "🐲", "size": 8, "power": 15},
    200: {"name": "Cosmic Worm", "emoji": "🌟", "size": 9, "power": 20},
    300: {"name": "Celestial Worm", "emoji": "✨", "size": 10, "power": 30},
    500: {"name": "God Worm", "emoji": "👑", "size": 12, "power": 50},
}

EVOLUTIONS = {
    "butterfly": {"req": 100, "coop": 50, "emoji": "🦋", "bonus": "Flight"},
    "beetle": {"req": 150, "coop": 75, "emoji": "🪲", "bonus": "Armor"},
    "snake": {"req": 200, "coop": 100, "emoji": "🐍", "bonus": "Venom"},
    "dragon": {"req": 350, "coop": 200, "emoji": "🐉", "bonus": "Fire"},
    "cosmic": {"req": 500, "coop": 300, "emoji": "🌌", "bonus": "Stellar"},
}

POWERS = {
    "vote": {"tokens": 50, "coop": 10, "label": "🗳️  Cast votes"},
    "ship_seat": {"tokens": 100, "coop": 25, "label": "🚀 Ship seat priority"},
    "bureau": {"tokens": 250, "coop": 50, "label": "🔍 Bureau reports"},
    "policy": {"tokens": 500, "coop": 100, "label": "📜 Propose filings"},
    "founder_ear": {"tokens": 1000, "coop": 250, "label": "👂 Message founder"},
}

SHOP = {
    "snack": {"cost": 100, "points": 1, "label": "🍎 Snack (1)"},
    "meal": {"cost": 500, "points": 5, "label": "🍖 Meal (5)"},
    "feast": {"cost": 2500, "points": 25, "label": "🍗 Feast (25)"},
    "banquet": {"cost": 10000, "points": 50, "label": "🎂 Banquet (50)"},
    "coronation": {"cost": 50000, "points": 100, "label": "👑 Coronation (100)"},
    "apotheosis": {"cost": 250000, "points": 250, "label": "🌟 Apotheosis (250)"},
}

SKINS = {
    "default": {"cost": 0, "coop": 0, "label": "Default"},
    "copper": {"cost": 50, "coop": 0, "label": "🟤 Copper"},
    "silver": {"cost": 100, "coop": 50, "label": "⚪ Silver"},
    "gold": {"cost": 500, "coop": 100, "label": "🟡 Gold"},
    "diamond": {"cost": 1000, "coop": 250, "label": "💎 Diamond"},
    "cosmic": {"cost": 5000, "coop": 500, "label": "🌌 Cosmic"},
}

TASKS = [
    ("file_research", "File a research page", 1, 2),
    ("verify_token", "Verify a token", 1, 3),
    ("add_plastic", "Add plastic to collection", 1, 2),
    ("gift_token", "Gift a token to another", 2, 4),
    ("cooperate", "Cooperate with another citizen", 5, 10),
    ("mentor", "Mentor a new citizen", 10, 20),
    ("duel_win", "Win a duel", 15, 30),
    ("race_win", "Win a race", 20, 40),
]

ACHIEVEMENTS = {
    "first_login": {"label": "🌅 First Steps", "desc": "Log in for the first time"},
    "first_feed": {"label": "🍽️  First Meal", "desc": "Feed your worm for the first time"},
    "first_gift": {"label": "🎁 Generous", "desc": "Gift plastic to another"},
    "first_duel": {"label": "⚔️  Warrior", "desc": "Win your first duel"},
    "first_race": {"label": "🏁 Racer", "desc": "Win your first race"},
    "streak_7": {"label": "🔥 On Fire", "desc": "7-day login streak"},
    "streak_30": {"label": "💎 Dedicated", "desc": "30-day login streak"},
    "level_10": {"label": "📈 Climber", "desc": "Reach level 10"},
    "level_50": {"label": "🏔️  Mountaineer", "desc": "Reach level 50"},
    "level_100": {"label": "🌌 Legendary", "desc": "Reach level 100"},
    "coop_50": {"label": "🤝 Helper", "desc": "50 cooperation acts"},
    "coop_100": {"label": "🌟 Saint", "desc": "100 cooperation acts"},
    "evolve": {"label": "🦋 Evolved", "desc": "Evolve your worm"},
    "nest_founder": {"label": "🏰 Nest Founder", "desc": "Create a nest"},
    "rich_buyer": {"label": "💰 Big Spender", "desc": "Buy 1000+ pennies worth"},
    "poor_climber": {"label": "💪 Self-Made", "desc": "Reach 50 without buying"},
}


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def worm_stage(points):
    stage = 0
    for threshold in sorted(STAGES.keys()):
        if points >= threshold:
            stage = threshold
    return stage


def worm_ascii(points):
    stage = STAGES[worm_stage(points)]
    size = stage["size"]
    emoji = stage["emoji"]
    return emoji * size


def worm_bar(points):
    stage = worm_stage(points)
    next_stage = None
    for threshold in sorted(STAGES.keys()):
        if points < threshold:
            next_stage = threshold
            break
    
    if next_stage is None:
        return "█" * 20 + " MAX"
    
    progress = (points - stage) / (next_stage - stage)
    filled = int(progress * 20)
    return "█" * filled + "░" * (20 - filled)


def get_worm(wid):
    worms = load_json(WORM_FILE, {})
    if wid not in worms:
        worms[wid] = {
            "wid": wid,
            "points": 0,
            "tokens": 0,
            "coop_acts": 0,
            "skin": "default",
            "evolution": None,
            "login_streak": 0,
            "last_login": 0,
            "powers": [],
            "achievements": [],
            "joined": time.time(),
            "spent": 0,
            "nest": None,
            "duels_won": 0,
            "races_won": 0,
        }
        save_json(WORM_FILE, worms)
    return worms[wid]


def save_worm(wid, worm):
    worms = load_json(WORM_FILE, {})
    worms[wid] = worm
    save_json(WORM_FILE, worms)


def check_powers(worm):
    unlocked = []
    for power, req in POWERS.items():
        if worm["points"] >= req["tokens"] and worm["coop_acts"] >= req["coop"]:
            unlocked.append(power)
    worm["powers"] = unlocked
    return unlocked


def check_achievements(worm):
    new = []
    if "first_login" not in worm["achievements"]:
        new.append("first_login")
    if worm["tokens"] > 0 and "first_feed" not in worm["achievements"]:
        new.append("first_feed")
    if worm["coop_acts"] > 0 and "first_gift" not in worm["achievements"]:
        new.append("first_gift")
    if worm.get("duels_won", 0) > 0 and "first_duel" not in worm["achievements"]:
        new.append("first_duel")
    if worm.get("races_won", 0) > 0 and "first_race" not in worm["achievements"]:
        new.append("first_race")
    if worm["login_streak"] >= 7 and "streak_7" not in worm["achievements"]:
        new.append("streak_7")
    if worm["login_streak"] >= 30 and "streak_30" not in worm["achievements"]:
        new.append("streak_30")
    if worm["points"] >= 10 and "level_10" not in worm["achievements"]:
        new.append("level_10")
    if worm["points"] >= 50 and "level_50" not in worm["achievements"]:
        new.append("level_50")
    if worm["points"] >= 100 and "level_100" not in worm["achievements"]:
        new.append("level_100")
    if worm["coop_acts"] >= 50 and "coop_50" not in worm["achievements"]:
        new.append("coop_50")
    if worm["coop_acts"] >= 100 and "coop_100" not in worm["achievements"]:
        new.append("coop_100")
    if worm.get("evolution") and "evolve" not in worm["achievements"]:
        new.append("evolve")
    if worm.get("spent", 0) >= 1000 and "rich_buyer" not in worm["achievements"]:
        new.append("rich_buyer")
    if worm["points"] >= 50 and worm.get("spent", 0) == 0 and "poor_climber" not in worm["achievements"]:
        new.append("poor_climber")
    
    worm["achievements"] = list(set(worm["achievements"] + new))
    return new


def status(wid):
    worm = get_worm(wid)
    check_powers(worm)
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    stage = STAGES[worm_stage(worm["points"])]
    
    print("=" * 50)
    print(f"🐛 YOUR WORM")
    print("=" * 50)
    print(f"\n  {worm_ascii(worm['points'])}")
    print(f"\n  Stage: {stage['emoji']} {stage['name']}")
    print(f"  Level: {worm['points']} points")
    print(f"  Power: {stage['power']}")
    print(f"  Plastic eaten: {worm['tokens']}")
    print(f"  Cooperation: {worm['coop_acts']} acts")
    print(f"  Login streak: {worm['login_streak']} days")
    print(f"  Skin: {worm['skin']}")
    if worm.get("evolution"):
        print(f"  Evolution: {EVOLUTIONS[worm['evolution']]['emoji']} {worm['evolution'].title()}")
    if worm.get("nest"):
        print(f"  Nest: {worm['nest']}")
    
    print(f"\n  Progress: [{worm_bar(worm['points'])}]")
    
    if worm["powers"]:
        print(f"\n🔓 UNLOCKED POWERS:")
        for p in worm["powers"]:
            print(f"  {POWERS[p]['label']}")
    else:
        print(f"\n🔒 No powers yet. Cooperate to unlock!")
    
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")
    
    print(f"\n{'─' * 50}")
    print("LADDER:")
    for threshold in sorted(STAGES.keys(), reverse=True):
        name = STAGES[threshold]["name"]
        emoji = STAGES[threshold]["emoji"]
        if worm["points"] >= threshold:
            print(f"  {emoji} {name:20s} ✓")
        else:
            print(f"  {emoji} {name:20s}")


def feed(wid, amount):
    worm = get_worm(wid)
    
    # Check tokens (not points) - feeding converts tokens to points
    if worm["tokens"] < amount:
        print(f"Not enough plastic tokens. You have {worm['tokens']}, need {amount}")
        return
    
    worm["tokens"] -= amount
    worm["points"] += amount
    
    check_powers(worm)
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    stage = STAGES[worm_stage(worm["points"])]
    
    print(f"🍽️  Fed {amount} plastic to your worm!")
    print(f"\n  {worm_ascii(worm['points'])}")
    print(f"  Stage: {stage['emoji']} {stage['name']}")
    print(f"  Level: {worm['points']} points")
    
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")


def login(wid):
    worm = get_worm(wid)
    now = time.time()
    last = worm.get("last_login", 0)
    
    if now - last < 86400:
        print("Already logged in today. Come back tomorrow!")
        return
    
    if now - last < 172800:
        worm["login_streak"] += 1
    else:
        worm["login_streak"] = 1
    
    worm["last_login"] = now
    worm["points"] += 1
    
    bonus = 0
    if worm["login_streak"] >= 7:
        bonus = 5
        worm["points"] += bonus
    if worm["login_streak"] >= 30:
        bonus += 20
        worm["points"] += 20
    
    check_powers(worm)
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    print(f"✅ Daily login! +1 point")
    print(f"🔥 Streak: {worm['login_streak']} days")
    if bonus:
        print(f"🎉 Streak bonus! +{bonus} points!")
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")


def do_task(wid, task_name):
    worm = get_worm(wid)
    
    task = None
    for t in TASKS:
        if t[0] == task_name:
            task = t
            break
    
    if not task:
        print(f"Unknown task: {task_name}")
        print(f"Available: {[t[0] for t in TASKS]}")
        return
    
    task_id, label, base, coop_bonus = task
    worm["points"] += base
    worm["coop_acts"] += 1
    worm["tokens"] += 1
    
    check_powers(worm)
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    print(f"✅ Task complete: {label}")
    print(f"  +{base} base points")
    print(f"  +1 cooperation act")
    print(f"  +1 plastic eaten")
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")


def gift(wid, receiver_wid, amount):
    worm = get_worm(wid)
    receiver = get_worm(receiver_wid)
    
    if worm["points"] < amount:
        print(f"Not enough points. You have {worm['points']}, need {amount}")
        return
    
    worm["points"] -= amount
    worm["coop_acts"] += amount * 2
    
    receiver["points"] += amount
    receiver["tokens"] += amount
    
    save_worm(wid, worm)
    save_worm(receiver_wid, receiver)
    
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    print(f"🎁 Gifted {amount} points to {receiver_wid}")
    print(f"  Your cooperation acts: +{amount * 2}")
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")


def battle(wid, opponent_wid):
    worm = get_worm(wid)
    opponent = get_worm(opponent_wid)
    
    print(f"⚔️  DUEL")
    print(f"  You: {worm_ascii(worm['points'])} ({worm['points']} pts)")
    print(f"  Opp: {worm_ascii(opponent['points'])} ({opponent['points']} pts)")
    print(f"\n  Rolling dice...")
    
    time.sleep(1)
    
    p1 = worm["points"] + random.randint(1, 20) + worm["coop_acts"]
    p2 = opponent["points"] + random.randint(1, 20) + opponent["coop_acts"]
    
    if p1 >= p2:
        worm["points"] += 10
        worm["duels_won"] = worm.get("duels_won", 0) + 1
        save_worm(wid, worm)
        print(f"\n🏆 YOU WIN! +10 points")
    else:
        opponent["points"] += 10
        save_worm(opponent_wid, opponent)
        print(f"\n😤 Opponent wins. Try again!")


def race(wid):
    worm = get_worm(wid)
    
    print(f"🏁 WORM RACE")
    print(f"  Your worm: {worm_ascii(worm['points'])} ({worm['points']} pts)")
    print(f"\n  Racing against 3 opponents...")
    
    time.sleep(1)
    
    opponents = [
        {"name": "RandomCitizen1", "points": random.randint(10, 100)},
        {"name": "RandomCitizen2", "points": random.randint(10, 100)},
        {"name": "RandomCitizen3", "points": random.randint(10, 100)},
    ]
    
    all_racers = [{"name": wid, "points": worm["points"]}] + opponents
    results = sorted(all_racers, key=lambda x: x["points"], reverse=True)
    
    print(f"\n  Results:")
    for i, r in enumerate(results):
        medal = ["🥇", "🥈", "🥉", "4️⃣"][i]
        print(f"    {medal} {r['name']:20s} — {r['points']} pts")
    
    if results[0]["name"] == wid:
        worm["points"] += 20
        worm["races_won"] = worm.get("races_won", 0) + 1
        save_worm(wid, worm)
        print(f"\n🏆 YOU WIN! +20 points")
    else:
        print(f"\n😤 You placed {next(i+1 for i, r in enumerate(results) if r['name'] == wid)}th. Try again!")


def shop():
    print("=" * 50)
    print("🛒 WORM SHOP — Pay to Grow")
    print("=" * 50)
    for item, info in SHOP.items():
        print(f"  {info['label']:25s} — {info['cost']:>7,} pennies")
    print(f"\n  Use 'wubu_worm buy <item>' to purchase")


def buy(wid, item):
    worm = get_worm(wid)
    
    if item not in SHOP:
        print(f"Unknown item: {item}")
        return
    
    info = SHOP[item]
    cost = info["cost"]
    points = info["points"]
    
    print(f"🛒 Purchasing {item} for {cost:,} pennies...")
    print(f"  (Payment processing simulated)")
    
    worm["points"] += points
    worm["tokens"] += points
    worm["spent"] = worm.get("spent", 0) + cost
    
    check_powers(worm)
    new_achievements = check_achievements(worm)
    save_worm(wid, worm)
    
    stage = STAGES[worm_stage(worm["points"])]
    
    print(f"✅ Purchased! +{points} points")
    print(f"\n  {worm_ascii(worm['points'])}")
    print(f"  Stage: {stage['emoji']} {stage['name']}")
    print(f"  Level: {worm['points']} points")
    
    if not worm["powers"]:
        print(f"\n  ⚠️  No powers yet. Buy more OR cooperate.")
    
    if new_achievements:
        print(f"\n🏆 NEW ACHIEVEMENTS:")
        for a in new_achievements:
            print(f"  {ACHIEVEMENTS[a]['label']}")


def evolve(wid):
    worm = get_worm(wid)
    
    print(f"🧬 EVOLUTION")
    print(f"  Current: {worm_ascii(worm['points'])} {STAGES[worm_stage(worm['points'])]['name']}")
    print(f"\n  Available evolutions:")
    
    for evo_name, evo in EVOLUTIONS.items():
        status = "✅" if worm["points"] >= evo["req"] and worm["coop_acts"] >= evo["coop"] else "🔒"
        print(f"    {status} {evo['emoji']} {evo_name.title():12s} — {evo['req']} pts, {evo['coop']} coop (+{evo['bonus']})")
    
    if worm.get("evolution"):
        evo = EVOLUTIONS[worm["evolution"]]
        print(f"\n  You are already evolved: {evo['emoji']} {worm['evolution'].title()}")
        print(f"  Bonus: {evo['bonus']}")


def leaderboard():
    worms = load_json(WORM_FILE, {})
    
    if not worms:
        print("No worms yet. Be the first!")
        return
    
    sorted_worms = sorted(worms.values(), key=lambda w: w["points"], reverse=True)
    
    print("=" * 50)
    print("🏆 WORM LEADERBOARD")
    print("=" * 50)
    
    for i, worm in enumerate(sorted_worms[:10]):
        stage = STAGES[worm_stage(worm["points"])]
        powers = len(worm.get("powers", []))
        ach = len(worm.get("achievements", []))
        print(f"  {i+1:2d}. {worm['wid']:15s} — {stage['emoji']} {stage['name']:12s} "
              f"({worm['points']:>4d} pts, {powers} powers, {ach} badges)")
    
    print(f"\n  Total worms: {len(sorted_worms)}")


def achievements(wid):
    worm = get_worm(wid)
    
    print("=" * 50)
    print("🏆 YOUR ACHIEVEMENTS")
    print("=" * 50)
    
    for ach_id, ach in ACHIEVEMENTS.items():
        status = "✅" if ach_id in worm.get("achievements", []) else "🔒"
        print(f"  {status} {ach['label']:20s} — {ach['desc']}")
    
    earned = len(worm.get("achievements", []))
    total = len(ACHIEVEMENTS)
    print(f"\n  {earned}/{total} earned")


def find_token(wid):
    worm = get_worm(wid)
    
    if random.random() > 0.3:
        points = random.randint(1, 5)
        worm["points"] += points
        worm["tokens"] += points
        check_powers(worm)
        new_achievements = check_achievements(worm)
        save_worm(wid, worm)
        
        print(f"🔍 You found a lost plastic token!")
        print(f"  +{points} points")
        if new_achievements:
            print(f"\n🏆 NEW ACHIEVEMENTS:")
            for a in new_achievements:
                print(f"  {ACHIEVEMENTS[a]['label']}")
    else:
        print(f"🔍 You searched but found nothing.")


def season():
    print("=" * 50)
    print("🌟 CURRENT SEASON")
    print("=" * 50)
    print(f"  Season 1: The Founding")
    print(f"  Theme: Building the Base")
    print(f"  Exclusive rewards: Founder Badge, Season 1 Skin")
    print(f"  Ends: When 100 worms reach level 10")
    print(f"\n  Season 2: The Expansion (upcoming)")
    print(f"  Theme: Nests and Alliances")
    print(f"  Exclusive rewards: Nest Founder Badge, Season 2 Skin")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: wubu_worm <status|feed|login|do|gift|battle|race|shop|buy|evolve|leaderboard|achievements|find|season> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "status" and len(sys.argv) >= 3:
        status(sys.argv[2])
    elif cmd == "feed" and len(sys.argv) >= 4:
        feed(sys.argv[2], int(sys.argv[3]))
    elif cmd == "login" and len(sys.argv) >= 3:
        login(sys.argv[2])
    elif cmd == "do" and len(sys.argv) >= 4:
        do_task(sys.argv[2], sys.argv[3])
    elif cmd == "gift" and len(sys.argv) >= 5:
        gift(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif cmd == "battle" and len(sys.argv) >= 4:
        battle(sys.argv[2], sys.argv[3])
    elif cmd == "race" and len(sys.argv) >= 3:
        race(sys.argv[2])
    elif cmd == "shop":
        shop()
    elif cmd == "buy" and len(sys.argv) >= 4:
        buy(sys.argv[2], sys.argv[3])
    elif cmd == "evolve" and len(sys.argv) >= 3:
        evolve(sys.argv[2])
    elif cmd == "leaderboard":
        leaderboard()
    elif cmd == "achievements" and len(sys.argv) >= 3:
        achievements(sys.argv[2])
    elif cmd == "find" and len(sys.argv) >= 3:
        find_token(sys.argv[2])
    elif cmd == "season":
        season()
    else:
        print("Unknown command")
        sys.exit(1)
