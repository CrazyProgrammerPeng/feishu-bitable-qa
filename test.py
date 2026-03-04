import requests
import json
import sys

BASE_URL = "http://localhost:80"


def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"健康检查: {response.status_code}")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {str(e)}")
        return False


def test_qa(message: str):
    """测试问答接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/test",
            json={"message": message},
            timeout=30
        )
        print(f"\n问题: {message}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"回答:\n{result['result']}")
        else:
            print(f"错误: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("飞书多维表格智能问答系统 - 测试脚本")
    print("=" * 60)
    
    print("\n1. 测试健康检查...")
    if not test_health():
        print("\n❌ 服务未启动，请先运行: python app.py")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("2. 测试问答功能")
    print("=" * 60)
    
    test_questions = [
        "帮助",
        "查询所有记录",
        "统计记录数量"
    ]
    
    for question in test_questions:
        print("\n" + "-" * 60)
        test_qa(question)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n💡 提示:")
    print("1. 确保已配置 ZHIPU_API_KEY 环境变量")
    print("2. 可以使用以下命令测试自定义问题:")
    print(f"   python test.py \"你的问题\"")
    
    if len(sys.argv) > 1:
        custom_question = sys.argv[1]
        print("\n" + "=" * 60)
        print(f"测试自定义问题: {custom_question}")
        print("=" * 60)
        test_qa(custom_question)


if __name__ == "__main__":
    main()
