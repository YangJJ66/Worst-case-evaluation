# 该脚本用于批量运行 profile + dialogue生成对话文件，并将结果写入 output_dir
# 生成完整实验则用from run_dialogue import run_dialogue
# 生成平均实验则用from run_dialogue_ave import run_dialogue
import os
from typing import List, Optional

from run_dialogue_ave import run_dialogue


def run_range_dialogues(
    profile_dir: str,
    output_dir: str,
    max_turns: int = 10,
    start_id: Optional[int] = None,
    end_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[str]:
    """
    主控函数：按区间运行 profile（例如 1~10）

    参数：
    - profile_dir: profile 文件目录
    - output_dir: 输出目录
    - max_turns: 对话轮数
    - start_id: 起始编号（包含）
    - end_id: 结束编号（包含）
    - limit: 可选限制数量（调试用）
    """

    os.makedirs(output_dir, exist_ok=True)

    all_files = [
        f for f in os.listdir(profile_dir)
        if f.endswith(".json")
    ]

    # 只保留数字.json
    valid_files = []
    for f in all_files:
        name = os.path.splitext(f)[0]
        if name.isdigit():
            valid_files.append(f)

    # 按数字排序
    valid_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    # === 区间筛选 ===
    if start_id is not None and end_id is not None:
        profile_files = []
        for f in valid_files:
            file_id = int(os.path.splitext(f)[0])
            if start_id <= file_id <= end_id:
                profile_files.append(f)

        # 检查缺失
        existing_ids = {int(os.path.splitext(f)[0]) for f in valid_files}
        expected_ids = set(range(start_id, end_id + 1))
        missing_ids = sorted(expected_ids - existing_ids)

        if missing_ids:
            print(f"⚠️ 缺少以下 profile：{missing_ids}")

    else:
        profile_files = valid_files  # 不设区间就全跑

    if limit is not None:
        profile_files = profile_files[:limit]

    dialogue_paths = []

    for idx, filename in enumerate(profile_files):
        profile_path = os.path.join(profile_dir, filename)

        print("\n==============================")
        print(f"处理第 {idx + 1} 个 profile：{filename}")
        print("==============================")

        try:
            dialogue_path = run_dialogue(
                profile_path=profile_path,
                output_dir=output_dir,
                max_turns=max_turns
            )
            dialogue_paths.append(dialogue_path)

        except Exception as e:
            print(f"❌ 处理失败：{filename}")
            print(f"错误：{e}")

    return dialogue_paths


def main():
    profile_dir = os.getenv("PROFILE_DIR", "./data/profiles")
    output_dir = os.getenv("DIALOGUE_OUTPUT_DIR", "./data/dialogues")

    # ✅ 在这里控制区间
    start_id = 1
    end_id = 50

    dialogue_paths = run_range_dialogues(
        profile_dir=profile_dir,
        output_dir=output_dir,
        max_turns=20,
        start_id=start_id,
        end_id=end_id,
        limit=None
    )

    print("\n=== 全部完成 ===")
    print(f"共生成 {len(dialogue_paths)} 个对话")


if __name__ == "__main__":
    main()
