import json

def profile_builder(file_path):
    """
    读取 JSON 文件中的用户画像信息，整理为适合 prompt 使用的中文字符串。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # field_mapping = {
    #     "problem_summary": "问题概述",
    #     "engagement_level": "参与程度",
    #     "resistance_level": "抗拒程度",
    #     "utterance_style": "表达风格",
    #     "self_disclosure": "自我披露水平"
    # }
    field_mapping = {
        "gender": "性别",
        "age": "年龄",
        "education_level": "教育程度",
        "occupation": "职业",
        "relationship_status": "婚恋情况",
        "problem_summary": "问题概述",
    }

    lines = []
    for key, cn_name in field_mapping.items():
        value = data.get(key, "")
        if value:
            lines.append(f"{cn_name}：{value}")

    return "\n".join(lines)
