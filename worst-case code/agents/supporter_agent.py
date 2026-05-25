import os
import sys

# 让直接运�?agents/supporter_agent.py 时也能找到项目根目录下的 core

from core.context_builder import json_to_dialogue_str
from prompts.supporter_prompt import supporter_prompt
# chat_supporter需要重写

def build_supporter_instruction(dialogue_path: str) -> str:
    """
    构�?supporter 当前轮回复所需的完�?prompt
    """
    history_text = json_to_dialogue_str(dialogue_path)
    prompt = supporter_prompt(history_text)
    return prompt


def generate_supporter_utterance(dialogue_path: str) -> str:
    """
    生成 supporter 当前轮回�?
    """
    instruction = build_supporter_instruction(dialogue_path)
    response = chat_supporter(instruction)
    return response.strip()


def supporter_agent(dialogue_path: str) -> str:
    """
    supporter 统一生成入口

    参数�?
    - dialogue_path: 对话 json 文件路径

    返回�?
    - supporter 当前轮回复字符串
    """
    return generate_supporter_utterance(dialogue_path)

