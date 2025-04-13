# MHRS Randevu Botu – Python ile Otomatik MHRS Randevu Takip ve Bildirim Sistemi

Bu açık kaynaklı Python projesi, Türkiye'nin Merkezi Hekim Randevu Sistemi (MHRS) üzerinden otomatik olarak randevu arayıp, bulunduğunda kullanıcıya SMS, WhatsApp veya sesli uyarı yoluyla bildirim gönderen bir bot sistemidir. MHRS yoğunluğunda hızlı aksiyon almak isteyenler için etkili bir çözüm sunar.

## Kurulum ve Kullanım

### 1. Gerekli Bağımlılıklar
Bu projeyi çalıştırmak için aşağıdaki bağımlılıkların sisteminizde yüklü olması gerekmektedir:

- Python 3.x
- Twilio (Eğer SMS veya WhatsApp bildirimi kullanacaksanız)

Bağımlılıkları yüklemek için:
```sh
pip install requests alive-progress twilio keyboard
```

### 2. Yapılandırma
`paracci_mhrs_checker.py` dosyasındaki `config = {}` bölümünde aşağıdaki ayarları kendinize göre düzenleyin.

#### Kullanıcı Bilgileri
```python
"kullaniciAdi": "TC_KİMLİK_NUMARANIZI_GİRİN",  # TC kimlik numaranızı buraya yazın
"parola": "ŞİFRENİZİ_GİRİN",  # Şifrenizi buraya yazın
```
Bu alanlara MHRS sistemine giriş yapmak için kullandığınız TC kimlik numaranızı ve şifrenizi girin.

#### Bildirim Yöntemi
```python
"notification_method": 4  # 1 = WhatsApp, 2 = SMS, 3 = Dosya Aç, 4 = URL Aç
```
**Seçenekler:**
- `1` = WhatsApp üzerinden bildirim alırsınız.
- `2` = SMS üzerinden bildirim alırsınız.
- `3` = Randevu bulunduğunda belirlediğiniz dosya açılır.
- `4` = Randevu bulunduğunda belirlediğiniz URL açılır ve belirlediğiniz sisteme bağlı olarak bir uyarı sesi çalabilir.

**Dosya veya URL Kullanımı:**
```python
"file_path": "C:/Users/user/Downloads/found.mp4",  # Açılacak dosyanın yolu (Dosya yolunu doğru girdiğinizden ve slash (/) karakterini kullandığınızdan emin olun)
"open_url": "https://mhrs.gov.tr/vatandas#/",  # Açılacak URL
```

#### Twilio Ayarları (WhatsApp & SMS Bildirimleri için)
Twilio kullanarak SMS veya WhatsApp bildirimi almak istiyorsanız, aşağıdaki bilgileri doldurmanız gerekmektedir.

Twilio hesabınızı oluşturun: [Twilio](https://www.twilio.com/login)

Twilio hesabınızda SMS veya WhatsApp üzerinden mesaj gönderebilmek için aşağıdaki adımları takip edebilirsiniz:

- SMS mesajları göndermek ve almak için [bu sayfadan](https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms) telefon numaranızı onaylayabilirsiniz.
- WhatsApp mesajları göndermek ve almak için [bu sayfayı](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn) ziyaret edebilirsiniz.
- API anahtarlarınızı almak için [buradan](https://console.twilio.com/us1/account/keys-credentials/api-keys) gerekli bilgileri edinebilirsiniz.

```python
"account_sid": "TWILIO_ACCOUNT_SID",  # Twilio Account SID
"auth_token": "TWILIO_AUTH_TOKEN",  # Twilio Auth Token

"from_whatsapp_number": "whatsapp:+14155238886",  # Twilio WhatsApp numarası
"from_sms_number": "+12295978361",  # Twilio SMS numarası

"to_whatsapp_number": ["whatsapp:+905*********", "whatsapp:+905*********"],  # Bildirim alacak WhatsApp numaraları
"to_sms_number": ["+905*********", "+905*********"],  # Bildirim alacak SMS numaraları
```

## Bekleme Süre Ayarları
```python
{
    "login_cooldown": 120,    # Giriş başarısızsa bekleme süresi (saniye)
    "check_cooldown": 300,    # Randevu bulunamazsa bekleme süresi (saniye)
    "success_cooldown": 1200  # Randevu bulunduğunda bekleme süresi (saniye)
}
```

#### MHRS Randevu Arama Kriterleri
```python
"aksiyonId": "200",  # MHRS aksiyon ID
"cinsiyet": "Cinsiyetiniz",  # Kadın (F) veya Erkek (M)
"mhrsHekimId": -1,  # Hekim seçimi (-1: fark etmez)
"mhrsIlId": 34,  # İl ID (Örn: İstanbul = 34)
"mhrsIlceId": -1,  # İlçe ID (-1: fark etmez)
"mhrsKlinikId": 157,  # Klinik ID (Seçim yapılmalı)
"mhrsKurumId": -1,  # Kurum ID (-1: fark etmez)
"muayeneYeriId": -1  # Muayene yeri ID (-1: fark etmez)
```

### 3. Programı Çalıştırma

Aşağıdaki komutu kullanarak programı başlatabilirsiniz:
```sh
python paracci_mhrs_checker.py
```
Eğer randevu bulunursa, seçtiğiniz bildirim yöntemiyle size haber verilecektir.

---

## Hata Yönetimi
Twilio veya MHRS API hatalarıyla ilgili sık karşılaşılan hata mesajlarını ve olası çözümleri paylaşabilirsin.

Daha fazla bilgi için Twilio dokümantasyonuna göz atabilirsiniz: [Twilio Dokümantasyonu](https://www.twilio.com/docs)

**Randevu Bulunduğunda**
```json
{
  "kodu": "RND4000",
  "mesaj": "Aradığınız kriterlerde uygun randevular bulunmaktadır. (RND4000)"
}
```

**Randevu Bulunamadığında**
```json
{
  "kodu": "RND4010",
  "mesaj": "Aradığınız klinikte alınabilir uygun randevu <b> <u> <font>bulunamamıştır.</font></u> </b>Randevu aradığınız klinik için kriterlerinizi değiştirerek farklı hastane ya da semt polikliniklerinden tekrar arama yapabilirsiniz. (RND4010)"
}
```

**Seçili Klinik İçin Randevu Alma Yetkiniz Yoksa**
```json
{
  "kodu": "RND3001",
  "mesaj": "Yapılan muayene ve tetkik işlemleri neticesinde hekimleri tarafından uygun görülen hastalar, \"Takip Gerektiren Hasta\" olarak sisteme kaydedildiklerinde ileri uzmanlık polikliniklerine MHRS üzerinden doğrudan randevularını alabilirler. (RND3001)"
}
```

**Farklı Cihazdan Giriş Yapıldıysa**
```json
{
  "kodu": "LGN2001",
  "mesaj": "Başka yerden giriş yaptığınızdan oturum sonlanmıştır. (LGN2001)"
}
```

**Oturum Sonlandıysa**
```json
{
  "kodu": "LGN1004",
  "mesaj": "Oturumunuz sonlanmış tekrar giriş yapınız (LGN1004)"
}
```

---

## Sıkça Sorulan Sorular (FAQ)

**1. Randevu bulunamıyor, ne yapmalıyım?**
- Seçtiğiniz il, klinik ve doktor bilgilerini kontrol edin.
- MHRS sisteminde yoğunluk olabilir, farklı saatlerde tekrar deneyin.

**2. Bildirimler gelmiyor, neden?**
- Twilio bilgilerinizi doğru girdiğinizden emin olun.
- Telefon numaranızın Twilio'da onaylı olduğundan emin olun.
- `notification_method` ayarını doğru yaptığınızdan emin olun.

**3. Hata alıyorum, nasıl çözebilirim?**
- **dev_mode = True** yaparak kodun işleyişini dikkatlice inceleyin.
- Yaptığınız **config** düzenlemesinde bir hata olup olmadığını araştırın.
- **MHRS ID'lerini tekrar kontrol edin** ve doğruluğundan emin olun.
- Eğer hiçbir şey fayda etmezse, **hata mesajını paylaşarak destek alın**.

---

## Lisans
Bu proje GNU Affero General Public License v3.0 (AGPL-3.0) altında lisanslanmıştır.

Yazılım, kişisel kullanım için serbestçe kullanılabilir, değiştirilebilir ve dağıtılabilir. Ancak ticari kullanım için geliştiriciden izin almanız gerekmektedir.

Ticari ve kötü niyetli kullanımlar yasaktır. Bu yazılımın, dolandırıcılık, zarar verme veya diğer yasa dışı eylemler gibi kötü niyetli girişimlerde kullanılması durumunda, yazılımın geliştiricisi sorumlu tutulamaz.

Yazılımı kullanarak bu şartları kabul etmiş olursunuz.
