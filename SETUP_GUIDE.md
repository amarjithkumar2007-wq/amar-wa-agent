# Setup guide (Hinglish, phone se, sab free)

Flow: tu WhatsApp pe message kare -> Meta webhook -> `app.py` (Render pe) -> Gemini -> WhatsApp reply.

Purana n8n + Hugging Face route ab use nahi hota (`n8n-*` files sirf reference ke liye hain).
Secrets (keys/tokens) kisi ko chat mein mat bhej. Sirf host ke Environment/Secrets mein daal.

## Step 1 - Gemini key (2 min)
aistudio.google.com/apikey > Create API key > copy. Ye `GEMINI_API_KEY` hai.

## Step 2 - Meta WhatsApp test number (10 min)
1. developers.facebook.com > Facebook login > developer account verify.
2. Create App > Other > Business > naam "Amar Agent". WhatsApp product > Set up.
3. WhatsApp > API Setup: Phone number ID copy kar (`PHONE_NUMBER_ID`). Temporary token copy kar (`WHATSAPP_TOKEN`, 24 ghante).
4. "To" mein apna number +91 6203941988 add kar aur OTP se verify kar. "Send message" se hello_world test kar.

Agar Meta card ya business verification maange to ruk jaana aur batana.

## Step 3 - Deploy on Render (5 min, free plan)
1. render.com > Sign in with GitHub > New > Blueprint > repo `amar-wa-agent`. `render.yaml` apne aap settings bhar dega.
2. Environment mein `VERIFY_TOKEN` (koi secret word), `WHATSAPP_TOKEN`, `PHONE_NUMBER_ID`, `GEMINI_API_KEY` daal. `ALLOWED_NUMBERS` already set hai.
3. Deploy hone do. URL milega: `https://<naam>.onrender.com`. `/health` kholke "ok" dekh.

Agar Render card maange to ruk jaana. Alternative: Hugging Face Docker Space.

## Step 4 - Webhook jodna (3 min)
Meta > WhatsApp > Configuration > Webhook > Edit: Callback URL = `https://<naam>.onrender.com/webhook`, Verify token = `VERIFY_TOKEN`. Verify and save. Phir "messages" field Subscribe kar.
Test number ko WhatsApp pe "hi" bhej. Reply aana chahiye.

## Dhyan rakho
- Temp token 24 ghante mein expire hota hai. Business Settings > System users se permanent token bana (permissions `whatsapp_business_messaging`, `whatsapp_business_management`) aur `WHATSAPP_TOKEN` badal.
- Render free service idle pe sleep ho jaati hai. Pehla reply 1 min late ho sakta hai.
- Tasks aur chat memory restart pe chali jaati hain. Persistence agle PR mein aayegi.
