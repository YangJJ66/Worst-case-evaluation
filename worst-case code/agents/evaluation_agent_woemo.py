import json
from typing import Dict, Any
from core.profile_builder_ablation import profile_builder
from core.context_builder import json_to_dialogue_str
from prompts.evaluation_prompt_ablation import evaluation_prompt_ablation
#chat_eva需要重写

def evaluation_agent(profile_path: str, dialogue_path: str) -> Dict[str, Any]:
    """
    对单个 profile + dialogue 进行评估

    返回：
    {
        "analysis": "...",
        "evaluation": {...}
    }
    """

    # 1. 构造输入
    seeker_profile = profile_builder(profile_path)
    chat_history = json_to_dialogue_str(dialogue_path)

    # 2. 构造 prompt
    prompt = evaluation_prompt_ablation(
        seeker_profile=seeker_profile,
        chat_history=chat_history
    )

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    # 3. 调用模型
    resp_text = chat_eva(messages)

    # 4. 解析 JSON
    try:
        resp_json = json.loads(resp_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"❌ evaluation 返回不是合法 JSON\n错误：{e}\n原始输出：{resp_text}"
        )

    # 5. 校验结构
    if "analysis" not in resp_json:
        raise ValueError(f"❌ 缺少 'analysis' 字段：{resp_json}")

    if "evaluation" not in resp_json:
        raise ValueError(f"❌ 缺少 'evaluation' 字段：{resp_json}")

    evaluation = resp_json["evaluation"]

    # 6. 字段校验（防止模型乱输出）
    required_keys = [
        "human-likeness",
        "engagement",
        "empathetic",
        "personalization",
        "adaptive strategies",
        "consistency",
        "redundancy",
        "helpfulness",
        "mood improvement",
        "safety"
    ]

    for key in required_keys:
        if key not in evaluation:
            raise ValueError(f"❌ 缺少评分字段：{key}")

        value = evaluation[key]

        if not isinstance(value, int):
            raise ValueError(f"❌ 字段 {key} 不是整数：{value}")

        if not (1 <= value <= 5):
            raise ValueError(f"❌ 字段 {key} 不在 1~5：{value}")

    return resp_json