import requests
import base64
import json

# ✅ 替换为你的 Google Gemini API Key
API_KEY = "AIzaSyDI8arF1kprfqkniJYDAd0c4bFy01Rpab8"
# ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={API_KEY}"


ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={API_KEY}"

# ✅ 读取 captcha.png 并编码为 base64
with open("hard_captcha_GFOYH.png", "rb") as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")

# ✅ 构建请求体：上传图像并让 Gemini 识别验证码
payload = {
    "contents": [
        {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/png",  # 如果是 jpg 改成 image/jpeg
                        "data": image_base64
                    }
                },
                {
                    "text": "请识别图中的验证码文字，只回答验证码内容，不要附加任何说明。"
                }
            ]
        }
    ]
}

# ✅ 请求头
headers = {
    "Content-Type": "application/json"
}

# ✅ 发送请求
response = requests.post(ENDPOINT, headers=headers, data=json.dumps(payload))

# ✅ 处理返回
if response.ok:
    try:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        print("✅ 识别结果：", text.strip())
    except Exception as e:
        print("⚠️ 无法解析返回结果：", result)
else:
    print("❌ 请求失败：", response.status_code)
    print(response.text)
