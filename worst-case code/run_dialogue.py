import os
import json

from agents.emo_agent import predict_first_emotion, predict_next_emotion
from agents.seeker_agent import seeker_agent
from agents.supporter_agent import supporter_agent


def emotion_result_to_text(emotion_result: dict) -> str:
    lines = []

    if emotion_result.get("emotion_label"):
        lines.append(f'emotion_label：{emotion_result["emotion_label"]}')

    if emotion_result.get("emotion_transition_reason"):
        lines.append(
            f'emotion_transition_reason：{emotion_result["emotion_transition_reason"]}'
        )

    if emotion_result.get("emotion_description"):
        lines.append(f'emotion_description：{emotion_result["emotion_description"]}')

    return "\n".join(lines)


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


def append_seeker_turn(dialogue_path: str, seeker_text: str, emotion_result: dict) -> None:
    dialogue_data = load_dialogue(dialogue_path)

    item = {
        "speaker": "seeker",
        "text": seeker_text,
        "emotion_label": emotion_result.get("emotion_label", ""),
        "emotion_description": emotion_result.get("emotion_description", "")
    }

    if "emotion_transition_reason" in emotion_result:
        item["emotion_transition_reason"] = emotion_result.get(
            "emotion_transition_reason", ""
        )

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
    print("生成完整对话实验")
    dialogue_path = init_dialogue_file(profile_path, output_dir)
    prev_emotion = None
    end_after_supporter = False  # seeker 说结束词后，让 supporter 再回复一轮再结束

    END_PHRASES = [
        "再见",
        "就这样吧"
    ]

    for turn_idx in range(max_turns):
        # 1. 情绪预测
        if turn_idx == 0:
            emotion_result = predict_first_emotion(profile_path)
        else:
            emotion_result = predict_next_emotion(
                profile_path=profile_path,
                dialogue_path=dialogue_path,
                prev_emotion=prev_emotion
            )

        emotion_text = emotion_result_to_text(emotion_result)
        prev_emotion = emotion_result.get("emotion_label", "中性")

        # 2. seeker 发言
        if turn_idx == 0:
            seeker_text = seeker_agent(
                profile_path=profile_path,
                emotion_text=emotion_text
            )
        else:
            seeker_text = seeker_agent(
                profile_path=profile_path,
                emotion_text=emotion_text,
                dialogue_path=dialogue_path
            )

        # 结束判断：原有逻辑保持不变
        if "<END>" in seeker_text:
            print("对话结束")
            break

        # 新增逻辑：如果 seeker 说了“就这样吧”，让 supporter 再回复一轮后结束
        if any(phrase in seeker_text for phrase in END_PHRASES):
            end_after_supporter = True

        append_seeker_turn(dialogue_path, seeker_text, emotion_result)

        # 3. supporter 回复
        supporter_text = supporter_agent(dialogue_path)
        append_supporter_turn(dialogue_path, supporter_text)

        # ✅ 精简打印（只保留你要的）
        print(f"\n=== 第 {turn_idx + 1} 轮 ===")
        print("[emotion]")
        print(json.dumps(emotion_result, ensure_ascii=False))
        print("[seeker]")
        print(seeker_text)
        print("[supporter]")
        print(supporter_text)

        # seeker 说“就这样吧”后，supporter 已完成最后一轮回复，结束对话
        if end_after_supporter:
            print("检测到“就这样吧”，supporter 已完成最后一轮回复，对话结束")
            break

    # 更新 turn
    dialogue_data = load_dialogue(dialogue_path)
    dialogue_data["turn"] = len(dialogue_data.get("dialogue", []))
    save_dialogue(dialogue_path, dialogue_data)

    return dialogue_path