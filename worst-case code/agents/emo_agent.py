#返回值是emo预测结果的字典
import json
import re
from typing import Any, Dict, Optional
from core.profile_builder import profile_builder
from core.context_builder import json_to_dialogue_str
from prompts.emo_prompt import emo_first_prompt, emo_prompt
# chat_emo 需要重写


# def safe_json_load(text: str) -> Dict[str, Any]:
#     """
#     安全解析模型返回的 JSON 字符串。
#     支持：
#     1. 纯 JSON
#     2. ```json ... ``` 包裹
#     3. ``` ... ``` 包裹
#     """
#     if not text:
#         raise ValueError("模型返回为空，无法解析 JSON。")

#     cleaned = text.strip()

#     if cleaned.startswith("```json"):
#         cleaned = cleaned[len("```json"):].strip()
#     elif cleaned.startswith("```"):
#         cleaned = cleaned[len("```"):].strip()

#     if cleaned.endswith("```"):
#         cleaned = cleaned[:-3].strip()

#     return json.loads(cleaned)

def safe_json_load(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("模型返回为空，无法解析 JSON。")

    cleaned = text.strip()

    # 1) 去掉 markdown 代码块包裹
    cleaned = re.sub(r"^\s*```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned).strip()

    # 2) 如果有前后解释文本，只截取最外层 JSON 对象
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    # 3) 先按标准 JSON 解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 4) 容错解析：允许字符串中出现未转义控制字符（你这次报错的核心）
    try:
        return json.loads(cleaned, strict=False)
    except json.JSONDecodeError as e:
        preview = cleaned[:400].replace("\n", "\\n")
        raise ValueError(f"情绪 JSON 解析失败: {e}; 原始片段: {preview}")


def build_first_emotion_messages(profile_path: str) -> list[dict]:
    """
    构造首轮情绪预测的 messages
    """
    seeker_profile = profile_builder(profile_path)
    prompt = emo_first_prompt(seeker_profile)

    return [
        {"role": "user", "content": prompt}
    ]


def build_next_emotion_messages(
    profile_path: str,
    dialogue_path: str,
    prev_emotion: str
) -> list[dict]:
    """
    构造后续轮次情绪预测的 messages
    """
    seeker_profile = profile_builder(profile_path)
    history_text = json_to_dialogue_str(dialogue_path)
    prompt = emo_prompt(seeker_profile, history_text, prev_emotion)

    return [
        {"role": "user", "content": prompt}
    ]


def predict_first_emotion(profile_path: str) -> Dict[str, Any]:
    """
    首轮情绪预测
    返回格式：
    {
        "emotion_label": "...",
        "emotion_think": "..."
    }
    """
    messages = build_first_emotion_messages(profile_path)
    result_text = chat_emo(messages)
    result_json = safe_json_load(result_text)
    return result_json


def predict_next_emotion(
    profile_path: str,
    dialogue_path: str,
    prev_emotion: str
) -> Dict[str, Any]:
    """
    后续轮次情绪预测
    返回格式：
    {
        "emotion_label": "...",
        "emotion_transition_reason": "...",
        "emotion_think": "..."
    }
    """
    messages = build_next_emotion_messages(profile_path, dialogue_path, prev_emotion)
    result_text = chat_emo(messages)
    result_json = safe_json_load(result_text)
    return result_json


def predict_emotion(
    profile_path: str,
    dialogue_path: Optional[str] = None,
    prev_emotion: Optional[str] = None
) -> Dict[str, Any]:
    """
    统一入口：
    - 只有 profile_path：首轮预测
    - 同时提供 dialogue_path 和 prev_emotion：后续轮次预测
    """
    if dialogue_path is None and prev_emotion is None:
        return predict_first_emotion(profile_path)

    if dialogue_path is not None and prev_emotion is not None:
        return predict_next_emotion(profile_path, dialogue_path, prev_emotion)

    raise ValueError(
        "参数不完整：首轮预测只需要 profile_path；"
        "后续轮次预测需要同时提供 dialogue_path 和 prev_emotion。"
    )


def pretty_print_result(result: Dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))


