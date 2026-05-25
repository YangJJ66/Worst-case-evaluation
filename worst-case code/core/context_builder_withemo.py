import json

def json_to_dialogue_str_with_emotion(file_path):
    """
    将对话 json 转换为带情绪信息的字符串（用于 evaluation prompt）
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dialogue_list = data.get("dialogue", [])

    result_lines = []

    for idx, item in enumerate(dialogue_list):
        speaker = item.get("speaker")
        text = item.get("text", "")

        emotion_label = item.get("emotion_label")
        emotion_description = item.get("emotion_description")
        emotion_transition_reason = item.get("emotion_transition_reason")

        # 角色映射
        if speaker == "seeker":
            role = "来访者"
        elif speaker == "supporter":
            role = "咨询师"
        else:
            role = "未知"

        # === 基础对话 ===
        result_lines.append(f"{role}：{text}")

        # === 只对 seeker 加情绪信息 ===
        if speaker == "seeker":
            if emotion_label:
                result_lines.append(f"  [情绪]：{emotion_label}")

            if emotion_description:
                result_lines.append(f"  [情绪描述]：{emotion_description}")

            if emotion_transition_reason:
                result_lines.append(f"  [情绪变化原因]：{emotion_transition_reason}")

        # 加空行更清晰
        result_lines.append("")

    return "\n".join(result_lines)