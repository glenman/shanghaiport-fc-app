# quick_test.py
import os
from siliconflow import SiliconFlow

def quick_translation_test(api_key):
    client = SiliconFlow(api_key=api_key)
    
    test_pairs = [
        ("你好，世界！", "Hello, world!"),
        ("人工智能", "Artificial Intelligence"),
        ("数据科学", "Data Science"),
        ("机器学习", "Machine Learning")
    ]
    
    print("开始翻译测试...\n")
    
    for chinese, expected_english in test_pairs:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-4B-Instruct",
            messages=[
                {"role": "user", "content": f"将以下中文翻译成英文：{chinese}"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        actual = response.choices[0].message.content.strip()
        status = "✓" if expected_english.lower() in actual.lower() else "✗"
        
        print(f"{status} 中文：{chinese}")
        print(f"   期望：{expected_english}")
        print(f"   实际：{actual}\n")
    
    print("测试完成！")

if __name__ == "__main__":
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if api_key:
        quick_translation_test(api_key)
    else:
        print("请先设置 SILICONFLOW_API_KEY 环境变量")