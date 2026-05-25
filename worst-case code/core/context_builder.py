import json

def json_to_dialogue_str(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dialogue_list = data.get("dialogue", [])
    
    result_lines = []
    
    for item in dialogue_list:
        speaker = item.get("speaker")
        text = item.get("text", "")
        
        if speaker == "seeker":
            role = "来访者"
        elif speaker == "supporter":
            role = "咨询师"
        else:
            role = "未知"
        
        result_lines.append(f"{role}：{text}")
    
    return "\n".join(result_lines)