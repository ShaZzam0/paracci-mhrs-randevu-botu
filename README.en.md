# MHRS Appointment Bot

This project is developed to search for appointments via **MHRS (Central Physician Appointment System)** and notify the user when an appointment is found.

## Installation and Usage

### 1. Required Dependencies
To run this project, the following dependencies must be installed on your system:

- Python 3.x
- Twilio (if you want to use SMS or WhatsApp notifications)

To install dependencies:
```sh
pip install requests alive-progress twilio keyboard
```

### 2. Configuration
Edit the `config = {}` section in the `paracci_mhrs_checker.py` file according to your preferences.

#### User Information
```python
"kullaniciAdi": "ENTER_YOUR_TURKISH_ID_NUMBER",  # Enter your Turkish ID number here
"parola": "ENTER_YOUR_PASSWORD",  # Enter your password here
```
Enter your Turkish ID number and password used to log into the MHRS system.

#### Notification Method
```python
"notification_method": 4  # 1 = WhatsApp, 2 = SMS, 3 = Open File, 4 = Open URL
```
**Options:**
- `1` = Receive notifications via WhatsApp.
- `2` = Receive notifications via SMS.
- `3` = A specified file will open when an appointment is found.
- `4` = A specified URL will open, and depending on your system, an alert sound may play.

**File or URL Usage:**
```python
"file_path": "C:/Users/user/Downloads/found.mp4",  # Path of the file to open (Ensure correct path format using slash `/`)
"open_url": "https://mhrs.gov.tr/vatandas#/",  # URL to open
```

#### Twilio Settings (For WhatsApp & SMS Notifications)
If you want to receive SMS or WhatsApp notifications using Twilio, you need to fill in the following details.

Create a Twilio account: [Twilio](https://www.twilio.com/login)

To send and receive SMS or WhatsApp messages on your Twilio account, follow these steps:

- Verify your phone number for SMS by [visiting this page](https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms).
- To send and receive WhatsApp messages, [visit this page](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn).
- To obtain your API keys, [go here](https://console.twilio.com/us1/account/keys-credentials/api-keys).

```python
"account_sid": "TWILIO_ACCOUNT_SID",  # Twilio Account SID
"auth_token": "TWILIO_AUTH_TOKEN",  # Twilio Auth Token

"from_whatsapp_number": "whatsapp:+14155238886",  # Twilio WhatsApp number
"from_sms_number": "+12295978361",  # Twilio SMS number

"to_whatsapp_number": ["whatsapp:+905*********", "whatsapp:+905*********"],  # WhatsApp numbers to receive notifications
"to_sms_number": ["+905*********", "+905*********"],  # SMS numbers to receive notifications
```

#### MHRS Appointment Search Criteria
```python
"aksiyonId": "200",  # MHRS action ID
"cinsiyet": "Your Gender",  # Female (F) or Male (M)
"mhrsHekimId": -1,  # Doctor selection (-1: doesn't matter)
"mhrsIlId": 34,  # City ID (e.g., Istanbul = 34)
"mhrsIlceId": -1,  # District ID (-1: doesn't matter)
"mhrsKlinikId": 157,  # Clinic ID (Must be selected)
"mhrsKurumId": -1,  # Institution ID (-1: doesn't matter)
"muayeneYeriId": -1  # Examination place ID (-1: doesn't matter)
```

### 3. Running the Program

Use the following command to start the program:
```sh
python paracci_mhrs_checker.py
```
If an appointment is found, you will be notified through the selected notification method.

---

## Error Handling
You can share common error messages related to Twilio or MHRS API and possible solutions.

For more information, check Twilio documentation: [Twilio Documentation](https://www.twilio.com/docs)

**When an Appointment is Found**
```json
{
  "kodu": "RND4000",
  "mesaj": "There are appointments that match the criterias you are looking for."
}
```

**When No Appointment is Found**
```json
{
  "kodu": "RND4010",
  "mesaj": "In the criteria you are looking for, <b> <u> no appointments could be found </font></u> </b> to suit your specifications.<br>However, you can search again from different hospital or Neighbourhood Polyclinics by changing your criteria for the clinic you are looking for an appointment with. (RND4010)"
}
```

**If You Do Not Have Permission to Make an Appointment for the Selected Clinic**
```json
{
  "kodu": "RND3001",
  "mesaj": "Patients who are deemed appropriate by their doctors as a result of the examination and examination procedures, can make their appointments directly to the advanced specialty polyclinics via CDAS when they are registered in the system as \"Patient Requiring Monitoring\". (RND3001)"
}
```

**If Logged in from a Different Device**
```json
{
  "kodu": "LGN2001",
  "mesaj": "The session ended because you logged in from somewhere else. (LGN2001)"
}
```

**If the Session is Expired**
```json
{
  "code": "LGN1004",
  "message": "Your session has expired, please log in again. (LGN1004)"
}
```

---

## Frequently Asked Questions (FAQ)

**1. No appointment is found, what should I do?**
- Check your selected city, clinic, and doctor information.
- MHRS system may be overloaded, try again at different times.

**2. Notifications are not being received, why?**
- Make sure your Twilio information is entered correctly.
- Ensure your phone number is verified on Twilio.
- Check if the `notification_method` setting is configured correctly.

**3. I am getting an error, how can I fix it?**
- Set **dev_mode = True** to carefully inspect the code execution.
- Verify that your **config** settings are correct.
- **Check the MHRS IDs again** to ensure their accuracy.
- If nothing works, **share the error message and seek support**.

---

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

The software can be freely used, modified, and distributed for personal use. However, you must obtain permission from the developer for commercial use.

Commercial and malicious uses are prohibited. The developer of this software cannot be held responsible if it is used in malicious attempts, such as fraud, harm, or other illegal actions.

By using the software, you agree to these terms.
