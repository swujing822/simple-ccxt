import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_PATH = 'token.json'

NEW_TOKEN_PATH = 'token2.json'

CREDENTIALS_PATH = 'credentials.json'

def get_credentials():
    creds = None

    # 如果已有 token.json，尝试加载
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 如果 token 无效或过期，尝试刷新或重新授权
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Token 已刷新")
            except Exception as e:
                print("⚠️ 刷新失败，需要重新授权:", e)
                creds = authorize()
        else:
            creds = authorize()

        # 保存新的 token
        with open(NEW_TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            print("✅ 新的 token 已保存")

    return creds

def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

    # 手动生成授权链接
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("🔗 请在浏览器中打开以下链接进行授权：\n", auth_url)
    code = input("📥 授权完成后，请粘贴授权码：\n")

    flow.fetch_token(code=code)
    return flow.credentials


if __name__ == '__main__':
    creds = get_credentials()
    print("🎉 授权成功，凭证已准备好")
