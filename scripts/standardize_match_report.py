import json
from pathlib import Path

def standardize_match_report(file_path: Path) -> bool:
    """标准化赛事报告中的球员名称"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 球员名称标准化映射
        name_mapping = {
            "布朗宁": "蒋光太",
            "普林斯·奥本·安佩姆": "安佩姆",
            "吾米提江·玉素甫": "吾米提江"
        }

        modified_count = 0

        def replace_name(obj, key=None):
            nonlocal modified_count
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "name" and isinstance(v, str) and v in name_mapping:
                        original = v
                        obj[k] = name_mapping[v]
                        print(f"  球员名称修正: {original} → {name_mapping[v]}")
                        modified_count += 1
                    elif k in ["player", "player2", "playerIn", "playerOut", "substitutedFor"] and isinstance(v, str) and v in name_mapping:
                        original = v
                        obj[k] = name_mapping[v]
                        print(f"  球员名称修正: {original} → {name_mapping[v]}")
                        modified_count += 1
                    else:
                        replace_name(v, k)
            elif isinstance(obj, list):
                for item in obj:
                    replace_name(item)

        print("=" * 60)
        print("开始标准化处理...")
        print("=" * 60)

        replace_name(data)

        # 保存更新后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 标准化处理完成！共修正 {modified_count} 处球员名称")
        return True

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def main():
    file_path = Path("public/data/2026-05-02-中超-第9轮.json")
    print(f"处理文件: {file_path.name}")
    standardize_match_report(file_path)

if __name__ == "__main__":
    main()
