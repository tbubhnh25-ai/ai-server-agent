# סוכן AI אוטונומי לשרת — שלד פרויקט

מערכת שרץ על שירות אחד (למשל Render), עם מודל שפה חינמי מרוחק (Groq או Gemini) וחיפוש חינמי (DuckDuckGo).

## הרצה מקומית

1. העתקת `.env.example` ל-`.env`, הגדרת `AGENT_AUTH_TOKEN` ו-`LLM_API_KEY` (מפתח חינמי מ-[console.groq.com/keys](https://console.groq.com/keys) או [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).
2. הרמת המערכת:
   ```bash
   docker-compose up -d --build
   ```
3. שליחת משימה:
   ```bash
   curl -X POST http://localhost:8000/task \
     -H "Authorization: Bearer <AGENT_AUTH_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"goal": "בדוק מה גרסת פייתון מותקנת על השרת"}'
   ```

## פריסה ל-Render

1. חיבור הריפו הזה לשירות Web Service חדש ב-Render (Render מזהה את ה-`Dockerfile` אוטומטית).
2. הגדרת משתני הסביבה מ-`.env.example` בלשונית Environment של השירות (`AGENT_AUTH_TOKEN`, `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`).
3. Deploy. Render מזריק את `PORT` בעצמו — אין צורך להגדיר אותו.

## גישה דרך Cloudflare Worker (פרוקסי)

אם הגישה הישירה לכתובת ה-Render חסומה (למשל ע"י סינון רשת/ISP), אפשר לגשת לסוכן דרך Worker של Cloudflare שמשמש פרוקסי הפוך:

1. כניסה ל-[dash.cloudflare.com](https://dash.cloudflare.com) -> Workers & Pages -> Create -> Create Worker.
2. עריכת הקוד (Edit code) והדבקת התוכן של `cloudflare-worker/worker.js` (עדכון `ORIGIN` לכתובת שירות ה-Render שלכם אם שונה).
3. Deploy. כעת אפשר לשלוח בקשות ל-`https://<worker-name>.<account>.workers.dev/task` במקום ישירות ל-Render - ה-Worker מעביר הלאה את כל ה-headers (כולל Authorization) וה-body.

## מבנה הפרויקט

```
app/
  main.py            נקודת כניסה ל-FastAPI
  config.py          הגדרות סביבה
  auth.py            אימות טוקן
  llm_provider.py    הפשטת ספק מודל (groq/gemini)
  orchestrator.py     לולאת הסוכן (Plan -> Act -> Observe)
  models.py          מבני נתונים
  tools/             הכלים שהסוכן יכול להפעיל
  sandbox/           הרצת פקודות shell מוגבלת-זמן/זיכרון
workspace/           תיקיית העבודה המשותפת
```

## הערות אבטחה

- `shell_exec` רץ כתהליך-בן מוגבל בזמן/זיכרון/מספר תהליכים, בתוך תיקיית ה-workspace בלבד — **בתוך הקונטיינר של השירות עצמו**, לא בקונטיינר sandbox נפרד. זה מספיק לפריסה על שירות יחיד כמו Render, אבל נותן בידוד חלש יותר מהרצה עם Docker-in-Docker.
- רשימת תבניות פקודה חסומות ב-`app/sandbox/subprocess_runner.py`.
- `http_fetch` חוסם כתובות פנימיות/פרטיות (הגנת SSRF).
- `package_install` מוגבל ל-`pip`/`npm` בלבד (לא `apt-get`, שדורש הרשאות root שאין לתהליך).
- לוג ביקורת מלא: כל משימה, מחשבה, פעולה ותוצאה מתועדים כ-JSON lines בקובץ שמוגדר ב-`AUDIT_LOG_PATH` (`app/audit.py`).
- יש להרחיב בהמשך: אישור ידני לפעולות הרסניות, ואם צריך בידוד חזק יותר — להעביר את `shell_exec` לבידוד קונטיינר נפרד בסביבה שמאפשרת זאת (לא Render).

זהו שלד בסיסי לעבודה - לא מוכן לייצור כמו שהוא.
