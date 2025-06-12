import os
import sys
import subprocess
import requests
import time
import keyboard
import threading
import webbrowser
from alive_progress import alive_bar
import random
from twilio.rest import Client
from datetime import datetime
import telegram
import asyncio

dev_mode = False

config = {                                          
    "kullaniciAdi": "TC_KİMLİK_NUMARANIZI_GİRİN",
    "parola": "ŞİFRENİZİ_GİRİN",
    "notification_method": 4,  # 1 = WhatsApp, 2 = SMS (SMS ile iletilen bilgiler geç gelebilir, bu yüzden kullanılması tavsiye edilmez), 3 = Open File, 4 = Open URL, 5 = Telegram
    "file_path": "C:/Users/user/Downloads/found.mp4",
    "open_url": "https://mhrs.gov.tr/vatandas#/",
    "account_sid": "TWILIO_ACCOUNT_SID",
    "auth_token": "TWILIO_AUTH_TOKEN",
    "telegram_bot_token": "YOUR_BOT_TOKEN",  # Telegram bot tokeni
    "telegram_chat_ids": ["YOUR_CHAT_ID"],  # Telegram chat ID'leri
    "from_whatsapp_number": "whatsapp:+14155238886",
    "from_sms_number": "+12295978361",
    "to_whatsapp_number": ["whatsapp:+905*********", "whatsapp:+905*********"],
    "to_sms_number": ["+905*********", "+905*********"],
    "login_cooldown": 120,    # Giriş başarısızsa bekleme süresi (saniye)
    "check_cooldown": 300,    # Randevu bulunamazsa bekleme süresi (saniye)
    "success_cooldown": 1200,  # Randevu bulunduğunda bekleme süresi (saniye)
    "aksiyonId": "200",
    "cinsiyet": "Cinsiyetiniz", # Kadın (F) veya Erkek (M)
    "mhrsHekimId": -1,
    "mhrsIlId": 34,
    "mhrsIlceId": -1,
    "mhrsKlinikId": 141,
    "mhrsKurumId": -1,
    "muayeneYeriId": -1
}

def dev_print(message):
    if dev_mode:
        print(f"DEV MODE: {message}")

def login_to_mhrs():
    login_url = "https://prd.mhrs.gov.tr/api/vatandas/login"
    login_payload = {
        "kullaniciAdi": config["kullaniciAdi"],
        "parola": config["parola"],
        "islemKanali": "VATANDAS_WEB",
        "girisTipi": "PAROLA",
        "captchaKey": None
    }
    login_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:     
        dev_print("Giriş işlemi başlatıldı.")
        login_response = requests.post(login_url, json=login_payload, headers=login_headers)
        login_response.raise_for_status()
        login_data = login_response.json()
        if not login_data.get("success"):
            dev_print(f"Giriş başarısız: {login_data.get('errors')}")
            print("Login Response JSON:", login_data)
            return None       
        jwt_token = login_data.get("data", {}).get("jwt")
        if not jwt_token:
            dev_print("JWT token alınamadı.")
            print("Login Response JSON:", login_data)
            return None
        dev_print(f"JWT Token başarıyla alındı: {jwt_token}")
        return jwt_token
    except requests.exceptions.RequestException as e:
        dev_print(f"HTTP isteği hatası: {e}")
        return None
    except ValueError:
        dev_print(f"JSON parse hatası. Sunucu yanıtı: {login_response.text}")
        return None

def find_nearest_appointment(appointments):
    nearest_appointment = None
    nearest_start_time = None
    for appointment in appointments:
        randevu_baslangic = appointment.get("randevuBaslangic")
        if randevu_baslangic:
            randevu_datetime = datetime.strptime(randevu_baslangic, "%Y-%m-%dT%H:%M:%S")
            if not nearest_start_time or randevu_datetime < nearest_start_time:
                nearest_start_time = randevu_datetime
                nearest_appointment = appointment
    return nearest_appointment

def check_appointment(token):
    url = "https://prd.mhrs.gov.tr/api/kurum-rss/randevu/slot-sorgulama/arama"
    payload = {
        "aksiyonId": config["aksiyonId"],
        "cinsiyet": config["cinsiyet"],
        "mhrsHekimId": config["mhrsHekimId"],
        "mhrsIlId": config["mhrsIlId"],
        "mhrsIlceId": config["mhrsIlceId"],
        "mhrsKlinikId": config["mhrsKlinikId"],
        "mhrsKurumId": config["mhrsKurumId"],
        "muayeneYeriId": config["muayeneYeriId"],
        "tumRandevular": False,
        "ekRandevu": True,
        "randevuZamaniList": []
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://mhrs.gov.tr/",
        "Authorization": f"Bearer {token}"
    }

    try:
        dev_print("Randevu kontrolü başlatıldı.")
        response = requests.post(url, json=payload, headers=headers)
        dev_print(f"HTTP Durum Kodu: {response.status_code}")

        try:
            data = response.json()
        except ValueError:
            dev_print(f"JSON parse hatası. Sunucu yanıtı: {response.text}")
            return None

        dev_print(f"API Yanıtı: {response.status_code}, {data}")

        if not data.get("success") and data.get("errors"):
            for error in data["errors"]:
                if error.get("kodu") in ["LGN1004", "LGN2001"]:
                    dev_print(f"Oturum sonlandı ({error.get('kodu')}). Program yeniden başlatılıyor...")
                    global connection_error
                    connection_error = True  
                    return None  
        
        if data.get("success") and any(info.get("kodu") == "RND4000" for info in data.get("infos", [])):
            hastane_list = data["data"].get("hastane", [])
            for hastane in hastane_list:
                hekim = hastane.get("hekim", {})
                muayene_yeri = hastane.get("muayeneYeri", {})
                klinik = hastane.get("klinik", {})
                kurum = hastane.get("kurum", {})
                baslangic_zamani = hastane.get("baslangicZamaniStr", {})
                return {
                    "hekimAdi": hekim.get("ad", "Bilinmiyor"),
                    "hekimSoyadi": hekim.get("soyad", "Bilinmiyor"),
                    "hastaneAdi": kurum.get("kurumAdi", "Bilinmiyor"),
                    "klinikAdi": klinik.get("mhrsKlinikAdi", "Bilinmiyor"),
                    "muayeneYeriAdi": muayene_yeri.get("adi", "Bilinmiyor"),
                    "randevuZamani": baslangic_zamani.get("zaman", "Bilinmiyor")
                }

        elif any(error.get("kodu") in ["RND4010", "RND4030"] for error in data.get("errors", [])):
            dev_print("Aradığınız kriterlerde uygun randevu bulunamadı.")
            return None
        
    except requests.exceptions.RequestException as e:
        dev_print(f"HTTP isteği hatası: {e}")
        return None

async def send_telegram_message(message):
    bot = telegram.Bot(token=config["telegram_bot_token"])
    for chat_id in config["telegram_chat_ids"]:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            dev_print(f"Telegram mesajı başarıyla gönderildi: {chat_id}")
        except Exception as e:
            dev_print(f"Telegram mesajı gönderilirken hata oluştu: {e}")
            
def send_message(message):
    client = Client(config["account_sid"], config["auth_token"])
    try:
        if config["notification_method"] == 1:
            dev_print("WhatsApp mesajı gönderiliyor.")
            for number in config["to_whatsapp_number"]:
                client.messages.create(
                    body=message,
                    from_=config["from_whatsapp_number"],
                    to=number
                )
                dev_print(f"WhatsApp mesajı başarıyla gönderildi: {number}")
            play_notification_sound()

        elif config["notification_method"] == 2:
            dev_print("SMS mesajı gönderiliyor.")
            for number in config["to_sms_number"]:
                client.messages.create(
                    body=message,
                    from_=config["from_sms_number"],
                    to=number
                )
                dev_print(f"SMS başarıyla gönderildi: {number}")
            play_notification_sound()

        elif config["notification_method"] == 3:
            dev_print(f"Belirtilen dosya açılıyor: {config['file_path']}")
            try:
                if os.path.exists(config["file_path"]):
                    os.startfile(config["file_path"])
                    dev_print("Dosya başarıyla açıldı.")
                else:
                    dev_print("HATA: Dosya bulunamadı!")
            except PermissionError:
                dev_print("HATA: Yetki sorunu! Dosyayı açmak için izin gerekli.")
            except FileNotFoundError:
                dev_print("HATA: Dosya yolu bulunamadı!")
            except Exception as e:
                dev_print(f"Dosya açma hatası: {e}")
            finally:
                play_notification_sound()

        elif config["notification_method"] == 4:
            dev_print(f"Belirtilen URL açılıyor: {config['open_url']}")
            webbrowser.open(config["open_url"])
            play_notification_sound()

        elif config["notification_method"] == 5:
            dev_print("Telegram mesajı gönderiliyor.")
            asyncio.run(send_telegram_message(message))
            play_notification_sound()
            
    except Exception as e:
        dev_print(f"Mesaj gönderme hatası: {e}")
        play_notification_sound()

def clear_previous_lines(n=1):
    for _ in range(n):
        print('\033[F\033[K', end='')

esc_permission = False

def esc():
    global esc_permission
    while True:
        keyboard.wait("esc")
        if esc_permission:
            print("ESC tuşuna basıldı, program zorla kapatılıyor...")
            os._exit(0)
        else:
            print("Şu anda çıkış izni yok. Randevu bulunduğunda çıkış mümkün olacak.")

def main():
    global connection_error, esc_permission
    
    threading.Thread(target=esc, daemon=True).start()
    
    while True:
        connection_error = False
        
        token = login_to_mhrs()
        if not token:
            dev_print(f"Giriş yapılamadı. {config['login_cooldown'] // 60} dakika sonra tekrar denenecek.")
            print(f"Giriş yapılamadı. {config['login_cooldown'] // 60} dakika sonra tekrar denenecek.")
            print("Config bilgilerini doğru şekilde ayarlamadığınızı düşünüyorsanız, programı kapatın ve yönergeyi tekrar gözden geçirin.")
            wait_with_progress(config["login_cooldown"], f"{config['login_cooldown'] // 60} dakika bekleniyor...", clear_lines=3)
            continue
        
        while not connection_error:
            appointment_status = check_appointment(token)
            
            if connection_error:
                break  
            
            if appointment_status:
                esc_permission = True
                message = (f"Randevu bulundu!\n\n"
                           f"Hekim: {appointment_status['hekimAdi']} {appointment_status['hekimSoyadi']}\n"
                           f"Hastane: {appointment_status['hastaneAdi']}\n"
                           f"Klinik: {appointment_status['klinikAdi']}\n"
                           f"Muayene Yeri: {appointment_status['muayeneYeriAdi']}\n"
                           f"En yakın randevu zamanı: {appointment_status['randevuZamani']}\n"
                           f"Hemen kontrol et: https://mhrs.gov.tr/vatandas#/")

                send_message(message)
                print(f"Randevu bulundu ve mesaj gönderildi. Eğer fark etmediyseniz, {config['success_cooldown'] // 60} dakika sonra tekrar kontrol edilecek ve bilgilendirileceksiniz.")
                print("Tekrar kontrol edilmesini istemiyorsanız, ESC tuşuna basarak programı durdurabilirsiniz.")
                wait_with_progress(config["success_cooldown"], f"{config['success_cooldown'] // 60} dakika bekleniyor...", clear_lines=3)
            else:
                dev_print(f"Randevu bulunamadı. {config['check_cooldown'] // 60} dakika sonra tekrar denenecek.")
                print(f"Randevu bulunamadı. {config['check_cooldown'] // 60} dakika sonra tekrar denenecek.")
                wait_with_progress(config["check_cooldown"], f"{config['check_cooldown'] // 60} dakika bekleniyor...", clear_lines=2)
        
        dev_print("Oturum hatası tespit edildi, program yeniden başlatılıyor...")

def wait_with_progress(seconds, message, clear_lines=1):
    with alive_bar(seconds, title=message, bar='smooth', spinner='flowers') as bar:
        for _ in range(seconds):
            time.sleep(1)
            bar()
    clear_previous_lines(clear_lines)

def alive_intro():
    print("\n🚀 PARACCI MHRS RANDEVU CHECKER BAŞLATILIYOR 🚀\n")
    random_range = random.randint(100, 200)
    with alive_bar(random_range, bar='halloween', spinner='it') as bar:
        for _ in range(random_range):
            time.sleep(random.uniform(0.01, 0.03))
            bar()
    print("\n✅ Başarılı! Sistem hazır.\n")

def play_notification_sound():
    try:
        if sys.platform.startswith("win"):  
            import winsound
            winsound.MessageBeep()
        elif sys.platform == "darwin":  
            subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"], check=True)
        else:  
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"], check=True)
    except Exception as e:
        print(f"Uyarı sesi çalınamadı: {e}")

if __name__ == "__main__":
    alive_intro()
    main()
