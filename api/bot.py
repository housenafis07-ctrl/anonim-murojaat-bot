import json
from http.server import BaseHTTPRequestHandler
import requests

BOT_TOKEN = "8817219207:AAEYnonur5Zy0Sg3wCxjpKqYVDrA_nO1qqQ"
GROUP_ID = -1004498687655

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                
                group_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                
                if text == "/start":
                    # Foydalanuvchiga salom yo'llash
                    requests.post(group_url, json={
                        "chat_id": chat_id,
                        "text": "Assalomu alaykum! Murojaatingizni yuboring. U to'liq anonim tarzda guruhga yetkaziladi (hech qanday ma'lumotingiz saqlanmaydi):"
                    })
                else:
                    # Guruhga yuborish (Kim yuborgani umuman ko'rinmaydi)
                    requests.post(group_url, json={
                        "chat_id": GROUP_ID,
                        "text": f"📩 **Yangi anonim murojaat:**\n\n{text}"
                    })
                    
                    # Foydalanuvchiga muvaffaqiyatli ketganini aytish
                    requests.post(group_url, json={
                        "chat_id": chat_id,
                        "text": "✅ Murojaatingiz guruhga anonim tarzda yuborildi!"
                    })

        except Exception as e:
            print(f"Xatolik: {e}")

        self.send_response(200)
        self.end_headers()
        return
