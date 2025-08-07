# Gemini Telegram Bot

Bot de Telegram con integración a Google Gemini (IA) y comandos personalizados para salud, entrenamiento y recordatorios.

## 🚀 Funciones incluidas

- **/start** — Muestra menú y comandos disponibles.
- **/planalimentos** — Plan de alimentación base.
- **/planentrenamiento** — Rutina semanal sugerida.
- **/seguimientopeso** `<peso>` — Guarda tu peso y muestra la variación desde la última vez.
- **/recordatorios** `<HH:MM>` `<texto>` — Programa un recordatorio diario (zona horaria AR).
- **Texto libre** — Respuesta con Gemini (modelo liviano `gemini-1.5-flash`).

## 📂 Estructura

```
.
├── bot_gemini.py        # Código principal del bot
├── gemini_client.py     # Cliente para la API de Google Gemini
├── requirements.txt     # Dependencias
├── .env.example         # Ejemplo de variables de entorno (NO subir .env real)
└── .gitignore           # Exclusión de archivos sensibles
```

## 🔑 Variables de entorno

En Render (o en `.env` local):

```env
TELEGRAM_TOKEN=tu_token_de_telegram
GEMINI_API_KEY=tu_api_key_de_gemini
GEMINI_MODEL=gemini-1.5-flash
```

⚠️ **Nunca subas `.env` a GitHub**.

## 🛠 Instalación local

```bash
git clone https://github.com/tu_usuario/tu_repo.git
cd tu_repo
pip install -r requirements.txt
cp .env.example .env  # Editar con tus claves reales
python bot_gemini.py
```

## ☁️ Deploy en Render

1. Crear **Background Worker** en Render.
2. Python **3.11**.
3. **Start Command**: `python bot_gemini.py`
4. Agregar variables de entorno desde `.env`.
5. Deploy y revisar logs para ver `Bot iniciado… 🚀`.

## 🔒 Seguridad

- Claves en variables de entorno, no en el código.
- `.gitignore` configurado para ignorar `.env` y archivos sensibles.
- Uso de modelo `gemini-1.5-flash` para evitar gastos innecesarios.

## 📜 Licencia

Uso personal / educativo. Ajustar según tus necesidades.
