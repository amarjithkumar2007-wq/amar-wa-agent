# Amar ka WhatsApp AI agent (n8n + Gemini) - phone se setup, sab free

Flow: tu WhatsApp pe message kare -> Meta webhook -> n8n (Hugging Face Space pe) -> Gemini AI Agent -> WhatsApp reply.
Baad mein n8n mein aur workflows (internship digest, reminders) add kar sakte hain.

Phone mein Chrome > 3-dot menu > "Desktop site" ON kar. Sab accounts Gmail amarjithkumar2007@gmail.com se bana.
Secrets (keys/tokens) kisi ko mat bhej, sirf Space ke Secrets mein daal.

## Step 1 - Gemini key (2 min)
aistudio.google.com/apikey > Create API key > copy. (GEMINI_KEY)

## Step 2 - Supabase database (5 min, n8n ka data yahan save hoga)
1. supabase.com > Sign in with GitHub > New project (naam n8n, password yaad rakh ya Notes mein save).
2. Project ban jaaye to upar "Connect" > "Session pooler" tab > host, port, user, database dikhega.
   Note kar: DB_HOST (aws-...pooler.supabase.com), DB_PORT (5432), DB_USER (postgres.xxxx), DB_PASSWORD.

## Step 3 - Hugging Face Space pe n8n (8 min)
1. huggingface.co > Sign up. Profile > New Space: naam `n8n`, SDK **Docker** > Blank, Free (CPU basic), **Public**.
2. Files tab > Add file > Create new file `Dockerfile`, andar github.com/amarjithkumar2007-wq/amar-wa-agent/blob/main/n8n-Dockerfile ka content paste kar. Commit.
3. Space Settings > "Variables and secrets" mein ye add kar:
   Secrets: DB_POSTGRESDB_PASSWORD (=DB_PASSWORD), N8N_ENCRYPTION_KEY (koi lamba random text, 32+ chars, Notes mein save), WHATSAPP_TOKEN (Step 4 se), VERIFY_TOKEN (koi secret word), GEMINI_KEY nahi chahiye (n8n credential mein jaayega).
   Variables: DB_POSTGRESDB_HOST, DB_POSTGRESDB_PORT=5432, DB_POSTGRESDB_USER, DB_POSTGRESDB_DATABASE=postgres, PHONE_NUMBER_ID (Step 4 se), ALLOWED_NUMBER=916203941988,
   WEBHOOK_URL = https://<tera-username>-n8n.hf.space/  (Space ka "Embed this Space" > Direct URL dekh ke sahi URL daal, end mein /),
   N8N_HOST = <tera-username>-n8n.hf.space, N8N_BLOCK_ENV_ACCESS_IN_NODE=false
4. Space build hone do (3-5 min). Phir Direct URL kholke n8n owner account bana (email + password).

## Step 4 - Meta WhatsApp test number (10 min)
1. developers.facebook.com > Facebook login > developer account verify.
2. Create App > Other > Business > naam "Amar Agent". WhatsApp product > Set up.
3. WhatsApp > API Setup: Phone number ID copy kar (PHONE_NUMBER_ID). Temporary token copy kar (WHATSAPP_TOKEN, 24 ghante).
4. "To" mein apna number +91 6203941988 add + OTP verify. "Send message" se hello_world test.
   Variables/Secrets Space mein update kar (Settings > ... ) - Space restart ho jaayega.

## Step 5 - Workflow import (3 min)
1. n8n > Workflows > Add workflow > top-right 3-dot > Import from URL:
   https://raw.githubusercontent.com/amarjithkumar2007-wq/amar-wa-agent/main/n8n-whatsapp-agent.workflow.json
2. "Gemini Chat Model" node kholo > Credential > Create new > Gemini API key paste (GEMINI_KEY).
3. Workflow ko **Active** kar (top-right toggle). Production URL hoga: https://<space-url>/webhook/whatsapp

## Step 6 - Webhook jodna (3 min)
Meta > WhatsApp > Configuration > Webhook > Edit: Callback URL = https://<space-url>/webhook/whatsapp, Verify token = VERIFY_TOKEN. Verify and save. Phir "messages" field Subscribe kar.
Test number ko WhatsApp pe "hi" bhej. Reply aana chahiye.

## Dhyan rakho
- Temp token 24 ghante mein expire: Business Settings > System users se permanent token bana (permissions whatsapp_business_messaging, whatsapp_business_management), Space secret WHATSAPP_TOKEN badal.
- HF free Space ~48 ghante idle rehne pe sleep ho jaata hai; message aane pe wake hota hai par pehla reply 1-2 min late ho sakta hai. Rokne ke liye cron-job.org (free) pe har 10 min Space URL ping karwa sakte hain.
- Supabase free project 1 hafta bina use ke pause ho sakta hai - dashboard se resume.
- Agar n8n wala setup atak jaaye: repo ke root mein simple Python bot (app.py) fallback hai, Render pe chalta hai.
