# Amar ka WhatsApp AI agent - phone se setup (sab free)

Tera bot: tu WhatsApp pe message kare -> Meta webhook -> Render pe bot -> Gemini jawab -> WhatsApp pe reply.
Commands: /add, /list, /done 2, /clear, /help. Baaki kuch bhi pooch.

Phone mein Chrome kholke "Desktop site" ON kar (3-dot menu) - Meta aur Render pe zaroori hai.

## Step 1 - Gemini key (2 min)
1. aistudio.google.com/apikey kholo, Google login (amarjithkumar2007@gmail.com).
2. "Create API key" -> copy karke Notes mein rakh. Ye GEMINI_API_KEY hai.

## Step 2 - GitHub pe code (3 min)
1. github.com pe naya repo bana: naam `amar-wa-agent`, Public.
2. "Add file > Upload files" se app.py, requirements.txt, .gitignore upload kar (zip se files nikaal ke) ya Instinct ne repo bana diya ho to skip.

## Step 3 - Meta app (10 min)
1. developers.facebook.com pe Facebook se login, "Get started" -> developer account verify (phone OTP).
2. My Apps > Create App > use case "Other" > type "Business" > naam "Amar Agent".
3. App dashboard mein "WhatsApp" product ke neeche "Set up" dabao. (Business portfolio maange to test wala bana le.)
4. WhatsApp > API Setup page pe ye milega:
   - Test number (From) ke neeche **Phone number ID** -> PHONE_NUMBER_ID
   - **Temporary access token** (24 ghante chalta hai) -> WHATSAPP_TOKEN
5. "To" box mein "Manage phone number list" -> apna number +91 6203941988 add kar, OTP WhatsApp pe aayega, verify kar.
6. "Send message" dabake test kar - hello_world message aana chahiye.

## Step 4 - Render deploy (5 min)
1. render.com pe GitHub se sign up.
2. New + > Web Service > apna repo `amar-wa-agent` chun.
3. Settings:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --workers 1 --threads 4 --timeout 60`
   - Instance type: Free
4. Environment variables daal:
   - VERIFY_TOKEN = koi bhi secret word (jaise `amar123xyz`)
   - WHATSAPP_TOKEN = Step 3.4 wala
   - PHONE_NUMBER_ID = Step 3.4 wala
   - GEMINI_API_KEY = Step 1 wala
   - ALLOWED_NUMBERS = 916203941988
5. Deploy. URL milega jaise https://amar-wa-agent.onrender.com - kholke "ok" dikhna chahiye.

## Step 5 - Webhook jodna (3 min)
1. Meta dashboard > WhatsApp > Configuration > Webhook > Edit.
2. Callback URL = https://<tera-render-url>/webhook
3. Verify token = wahi VERIFY_TOKEN. "Verify and save".
4. Neeche Webhook fields mein "messages" ko **Subscribe** kar.
5. Ab WhatsApp pe test number ko "hi" bhej. Reply aana chahiye.

## Dhyan rakhne wali baatein
- Temporary token 24 ghante mein expire hota hai. Permanent token: Business Settings > Users > System users > Add (admin) > Generate token, permissions `whatsapp_business_messaging` + `whatsapp_business_management`, app select kar. Phir Render mein WHATSAPP_TOKEN badal de.
- Meta test number sirf tune jo numbers add kiye unhi ko message bhej sakta hai. Tu apna number add kar chuka hai, theek hai.
- Tune pehle test number ko message bheja ho (ya hello_world mila ho) tabhi 24 ghante ke andar free-form reply jaata hai.
- Render free service 15 min idle ke baad so jaati hai; pehla reply 30-60 sec late aa sakta hai. Tasks/list restart pe reset ho jaati hai (free disk).
- Gemini free tier ki limit hai; "AI busy" aaye to thodi der baad try kar.
- Tokens/keys kisi ko share mat kar, WhatsApp pe mujhe bhi nahi. Sirf Render ke environment mein daal.
