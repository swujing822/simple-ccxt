import google.generativeai as genai

# 配置你的 API 密钥
# genai.configure(api_key="AIzaSyDI8arF1kprfqkniJYDAd0c4bFy01Rpab8")

import requests
import json

# ✅ 替换为你的 Gemini API Key
API_KEY = "AIzaSyDI8arF1kprfqkniJYDAd0c4bFy01Rpab8"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# ✅ 提问内容
payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "你好，请告诉我如何生成图片验证码"
                }
            ]
        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

# ✅ 发起请求
response = requests.post(URL, headers=headers, json=payload)

# ✅ 处理响应
if response.ok:
    result = response.json()
    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        print("✅ Gemini 回答：", text.strip())
    except Exception as e:
        print("⚠️ 返回结构可能有变化：", result)
else:
    print("❌ 请求失败：", response.status_code)
    print(response.text)
