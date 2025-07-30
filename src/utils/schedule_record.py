import requests
import json

BASE_URL = "https://qdjhgxyiymyqoimpdhda.supabase.co/functions/v1"
HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your-token"  # 如需鉴权，请取消注释
}


def call_edge_function(name: str, method="GET", payload: dict = None):
    url = f"{BASE_URL}/{name}"

    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, data=json.dumps(payload or {}))
        else:
            raise ValueError(f"不支持的方法: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except json.JSONDecodeError:
        print("❌ 返回内容不是合法的 JSON")
    return None


def get_latest_row():
    result = call_edge_function("get_latest_row", method="GET")
    if result and "data" in result:
        print("✅ 最新记录:", result["data"])
        return result["data"]
    else:
        print("⚠️ 没有获取到数据")
        return None


def add_row(start=100, end=200, count=101, remark="insert from python", runner="python-script"):
    payload = {
        "start_num": start,
        "end_num": end,
        "count": count,
        "remark": remark,
        "runner": runner,
    }
    result = call_edge_function("add_row", method="POST", payload=payload)
    if result and "data" in result:
        print("✅ 插入成功:", result["data"])
        return result["data"]
    else:
        print("⚠️ 插入失败")
        return None


def unzip():
    import zipfile
    import os

    # 路径配置
    zip_path = 'drive.zip'
    extract_to = './drive'  # 解压到 drive 文件夹（可改成你想要的位置）

    # 创建目标目录（如果不存在）
    os.makedirs(extract_to, exist_ok=True)

    # 解压
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    print(f"✅ 解压完成，文件已提取到：{extract_to}")
