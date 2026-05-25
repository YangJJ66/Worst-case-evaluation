import os
import json

from agents.seeker_agent_ave import seeker_agent
from agents.supporter_agent import supporter_agent


def init_dialogue_file(profile_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    profile_filename = os.path.basename(profile_path)
    dialogue_path = os.path.join(output_dir, profile_filename)

    init_data = {
        "dialogue": [],
        "turn": 0
    }

    with open(dialogue_path, "w", encoding="utf-8") as f:
        json.dump(init_data, f, ensure_ascii=False, indent=2)

    return dialogue_path


def load_dialogue(dialogue_path: str) -> dict:
    with open(dialogue_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dialogue(dialogue_path: str, dialogue_data: dict) -> None:
    with open(dialogue_path, "w", encoding="utf-8") as f:
        json.dump(dialogue_data, f, ensure_ascii=False, indent=2)


def append_seeker_turn(dialogue_path: str, seeker_text: str) -> None:
    dialogue_data = load_dialogue(dialogue_path)

    item = {
        "speaker": "seeker",
        "text": seeker_text
    }

    dialogue_data["dialogue"].append(item)
    dialogue_data["turn"] = len(dialogue_data["dialogue"])

    save_dialogue(dialogue_path, dialogue_data)


def append_supporter_turn(dialogue_path: str, supporter_text: str) -> None:
    dialogue_data = load_dialogue(dialogue_path)

    item = {
        "speaker": "supporter",
        "text": supporter_text
    }

    dialogue_data["dialogue"].append(item)
    dialogue_data["turn"] = len(dialogue_data["dialogue"])

    save_dialogue(dialogue_path, dialogue_data)


def run_dialogue(profile_path: str, output_dir: str, max_turns: int = 10) -> str:
    print("生成消融对话实验")
    dialogue_path = init_dialogue_file(profile_path, output_dir)
    end_after_supporter = False  # seeker 说结束语后，让 supporter 再回复一轮再结束

    # ✅ 结束语列表（可自由扩展）
    END_PHRASES = [
        "再见",
        "先这样",
        "先到这",
        "先结束"
    ]

    for turn_idx in range(max_turns):
        # 1. seeker 发言
        if turn_idx == 0:
            seeker_text = seeker_agent(
                profile_path=profile_path
            )
        else:
            seeker_text = seeker_agent(
                profile_path=profile_path,
                dialogue_path=dialogue_path
            )

        # 原结束判断
        if "<END>" in seeker_text:
            print("输出<END>，对话结束")
            break

        # ✅ 使用结束语列表判断
        if any(phrase in seeker_text for phrase in END_PHRASES):
            end_after_supporter = True

        append_seeker_turn(dialogue_path, seeker_text)

        # 2. supporter 回复
        supporter_text = supporter_agent(dialogue_path)
        append_supporter_turn(dialogue_path, supporter_text)

        print(f"\n=== 第 {turn_idx + 1} 轮 ===")
        print("[seeker]")
        print(seeker_text)
        print("[supporter]")
        print(supporter_text)

        # supporter 回复后结束
        if end_after_supporter:
            print("检测到结束语，supporter 已完成最后一轮回复，对话结束")
            break

    # 更新 turn
    dialogue_data = load_dialogue(dialogue_path)
    dialogue_data["turn"] = len(dialogue_data.get("dialogue", []))
    save_dialogue(dialogue_path, dialogue_data)

    return dialogue_path