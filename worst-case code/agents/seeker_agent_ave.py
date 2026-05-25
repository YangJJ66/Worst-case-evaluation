# 返回值是 seeker response 字符�?import os
import sys
from typing import Optional

from core.profile_builder_ablation import profile_builder
from core.context_builder import json_to_dialogue_str
from prompts.seeker_prompt_ablation import seeker_first_prompt, seeker_prompt
#chat_seeker需要重写


def build_first_seeker_messages(profile_path: str) -> list[dict]:
    """
    构�?seeker 首轮发言所需�?messages
    """
    seeker_profile = profile_builder(profile_path)
    
    prompt = seeker_first_prompt(seeker_profile)

    return [
        {"role": "user", "content": prompt}
    ]


def build_next_seeker_messages(
    profile_path: str,
    dialogue_path: str
) -> list[dict]:
    """
    构�?seeker 非首轮发言所需�?messages
    """
    seeker_profile = profile_builder(profile_path)
    history_text = json_to_dialogue_str(dialogue_path)
    prompt = seeker_prompt(seeker_profile, history_text)

    return [
        {"role": "user", "content": prompt}
    ]


def generate_first_seeker_utterance(profile_path: str) -> str:
    """
    生成 seeker 首轮发言
    """
    messages = build_first_seeker_messages(profile_path)
    response = chat_seeker(messages)
    return response.strip()


def generate_next_seeker_utterance(
    profile_path: str,
    dialogue_path: str
) -> str:
    """
    生成 seeker 后续轮次发言
    """
    messages = build_next_seeker_messages(profile_path, dialogue_path)
    response = chat_seeker(messages)
    return response.strip()


def seeker_agent(
    profile_path: str,
    dialogue_path: Optional[str] = None
) -> str:
    """
    seeker 统一生成入口

    参数�?    - profile_path: 画像 json 文件路径
    - dialogue_path:
        - None: 生成首轮发言
        - �?None: 根据历史对话生成后续发言

    返回�?    - seeker 当前轮发言字符�?    """
    if dialogue_path is None:
        return generate_first_seeker_utterance(profile_path)

    return generate_next_seeker_utterance(profile_path, dialogue_path)
