/**
 * פרוקסי הפוך (reverse proxy) ל-Worker Cloudflare.
 * מעביר כל בקשה ל-worker.dev ל-שירות הסוכן ב-Render, כולל headers (כגון Authorization) וה-body,
 * ומחזיר את התגובה כמו שהיא. האימות עם AGENT_AUTH_TOKEN עדיין נאכף בצד השרת עצמו.
 *
 * שימוש: עדכנו את ORIGIN לכתובת שירות ה-Render שלכם, והדביקו את הקובץ כולו
 * בעורך ה-Worker ב-Cloudflare (Workers & Pages -> Create -> Edit code).
 */

const ORIGIN = "https://autonomous-agent-server.onrender.com";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = ORIGIN + url.pathname + url.search;

    const init = {
      method: request.method,
      headers: request.headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
    };

    const response = await fetch(targetUrl, init);
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  },
};
