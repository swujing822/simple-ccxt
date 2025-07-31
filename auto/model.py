import google.generativeai as genai

# 配置你的 API 密钥
genai.configure(api_key="AIzaSyDI8arF1kprfqkniJYDAd0c4bFy01Rpab8")

# 获取所有可用的模型
models = genai.list_models()

# 输出模型列表
for model in models:
    print(f"模型名: {model.name}")
