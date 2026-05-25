# 该脚本用于批量评估 profile + dialogue，并将结果写入 output_dir
import os
import json
from typing import List, Optional

from agents.evaluation_agent_new import evaluation_agent


def run_range_evaluations(
    profile_dir: str,
    dialogue_dir: str,
    output_dir: str,
    start_id: Optional[int] = None,
    end_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[str]:
    """
    主控函数：批量评估 profile + dialogue，并写入结果文件

    功能：
    - 按编号匹配 profile 和 dialogue（如 1.json 对应 1.json）
    - 调用 evaluation_agent(profile_path, dialogue_path)
    - 将结果写入 output_dir
    - 返回所有生成的 evaluation 文件路径列表

    参数：
    - profile_dir: profile 文件夹路径
    - dialogue_dir: dialogue 文件夹路径
    - output_dir: evaluation 输出文件夹路径
    - start_id: 起始编号（包含）
    - end_id: 结束编号（包含）
    - limit: 可选，限制处理数量（调试用）

    返回：
    - 所有成功写入的 evaluation 文件路径列表
    """

    os.makedirs(output_dir, exist_ok=True)

    # 读取 profile_dir 下所有数字命名的 json 文件
    all_profile_files = [
        f for f in os.listdir(profile_dir)
        if f.endswith(".json") and os.path.splitext(f)[0].isdigit()
    ]

    # 按数字排序，避免 1, 10, 2 的字符串排序问题
    all_profile_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    # 区间筛选
    if start_id is not None and end_id is not None:
        profile_files = [
            f for f in all_profile_files
            if start_id <= int(os.path.splitext(f)[0]) <= end_id
        ]

        existing_ids = {
            int(os.path.splitext(f)[0]) for f in all_profile_files
        }
        expected_ids = set(range(start_id, end_id + 1))
        missing_profile_ids = sorted(expected_ids - existing_ids)

        if missing_profile_ids:
            print(f"⚠️ profile 文件夹缺少以下文件：{missing_profile_ids}")
    else:
        profile_files = all_profile_files

    if limit is not None:
        profile_files = profile_files[:limit]

    output_paths = []

    for idx, filename in enumerate(profile_files):
        profile_path = os.path.join(profile_dir, filename)
        dialogue_path = os.path.join(dialogue_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print("\n==============================")
        print(f"处理第 {idx + 1} 个文件：{filename}")
        print("==============================")

        # 检查 dialogue 文件是否存在
        if not os.path.exists(dialogue_path):
            print(f"❌ 缺少对应 dialogue 文件：{filename}")
            continue

        try:
            result = evaluation_agent(
                profile_path=profile_path,
                dialogue_path=dialogue_path
            )

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            output_paths.append(output_path)
            print(f"✅ 已写入：{output_path}")

        except Exception as e:
            print(f"❌ 处理失败：{filename}")
            print(f"错误：{e}")

            # 如需失败也落盘，保留错误信息，可以保留下面这段
            error_result = {
                "analysis": "ERROR",
                "evaluation": {},
                "error": str(e)
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)

            output_paths.append(output_path)
            print(f"⚠️ 已写入错误结果：{output_path}")

    return output_paths


def main():
    profile_dir = os.getenv("PROFILE_DIR", "./data/profiles")
    dialogue_dir = os.getenv("DIALOGUE_DIR", "./data/dialogues")
    output_dir = os.getenv("EVAL_OUTPUT_DIR", "./data/evaluations")

    # 区间控制
    start_id = 1
    end_id = 50

    output_paths = run_range_evaluations(
        profile_dir=profile_dir,
        dialogue_dir=dialogue_dir,
        output_dir=output_dir,
        start_id=start_id,
        end_id=end_id,
        limit=None
    )

    print("\n=== 全部完成 ===")
    print(f"共生成 {len(output_paths)} 个 evaluation 文件")


if __name__ == "__main__":
    main()
