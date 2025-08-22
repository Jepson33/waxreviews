# Waxreviews

Automatiskt system för att samla gästrecensioner 24h efter utcheckning på Waxholms Hotell.  
Byggt för att öka antalet positiva recensioner på Google/Tripadvisor och samtidigt fånga upp intern feedback.

---

## 🚀 Funktioner
- Hämtar gäster som checkat ut från **Mews API**.
- Väntar 24h innan utskick för att kännas mer personligt.
- Skickar e-post med personlig hälsning och betygsfråga (1–5).
- Loggar alla utskick och feedback i CSV-filer.
- Gäst klickar på en stjärna → öppnar enkel webbsida:
  - **4–5 stjärnor** → tack-sida med länk till Google/Tripadvisor.
  - **1–3 stjärnor** → tack-sida, loggas internt för uppföljning.
- Notifiering vid negativa svar (ex via e-post till receptionen).
- Enkel mallmotor (Jinja2) för att personalisera mail.

---

## 📂 Struktur

waxreviews/
src/
main.py # CLI för att köra schemalagda flöden
mews_client.py # Hämtar data från Mews API (eller mock under test)
scheduler.py # Hanterar utskickskö och 24h-delay
emailer.py # Skickar e-post (återanvändbar modul)
storage.py # Loggning av utskick och feedback
feedback_server.py # Enkel webbtjänst (FastAPI) som tar emot klick
templates/
email_invite.html
thank_you_positive.html
thank_you_neutral.html
data/
sent.csv # Logg av skickade mail
feedback.csv # Gästfeedback (1–5)
pending.json # Kö för utskick
config.example.json
requirements.txt
README.md
