# סוכן AI אוטונומי לשרת — שלד פרויקט

מערכת חינמית לחלוטין: מודל שפה מקומי (Ollama), חיפוש חינמי (DuckDuckGo), והרצת פקודות בתוך קונטיינר Docker מבודד (sandbox).

## הרצה

1. התקנת Docker ו-Docker Compose.
2. העתקת `.env.example` ל-`.env` והגדרת `AGENT_AUTH_TOKEN`.
3. בניית תמונת ה-sandbox:
   ```bash
   docker build -t agent-sandbox:latest ./sandbox_image
   ```
4. הרמת המערכת:
   ```bash
   docker-compose up -d
   ```
5. הורדת מודל חינמי ל-Ollama (פעם אחת):
   ```bash
   docker exec -it $(docker ps -qf name=ollama) ollama pull llama3.1
   ```
6. שליחת משימה:
   ```bash
   curl -X POST http://localhost:8000/task \
     -H "Authorization: Bearer <AGENT_AUTH_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"goal": "בדוק מה גרסת פייתון מותקנת על השרת"}'
   ```

## מבנה הפרויקט

```
app/
  main.py            נקודת כניסה ל-FastAPI
  config.py          הגדרות סביבה
  auth.py            אימות טוקן
  llm_provider.py    הפשטת ספק מודל (ollama/groq)
  orchestrator.py     לולאת הסוכן (Plan -> Act -> Observe)
  models.py          מבני נתונים
  tools/             הכלים שהסוכן יכול להפעיל
  sandbox/           הרצת פקודות בתוך קונטיינר מבודד
sandbox_image/       תמונת ה-Docker שבתוכה רצות הפקודות של הסוכן
workspace/           תיקיית העבודה המשותפת
```

## הערות אבטחה

- כל פקודת shell רצה בתוך קונטיינר נפרד, לא-root, עם הגבלת CPU/זיכרון/זמן.
- רשימת תבניות פקודה חסומות ב-`app/sandbox/docker_runner.py`.
- `http_fetch` חוסם כתובות פנימיות/פרטיות (הגנת SSRF).
- יש להרחיב בהמשך: לוג ביקורת מלא, אישור ידני לפעולות הרסניות, הרשאות Docker socket מוגבלות יותר (למשל Docker-in-Docker עם rootless).

זהו שלד בסיסי לעבודה - לא מוכן לייצור כמו שהוא.
