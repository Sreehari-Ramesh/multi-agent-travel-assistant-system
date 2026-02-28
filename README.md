# Dubai Travel Multi-Agent Assistant

A WhatsApp-style AI assistant for discovering and booking Dubai activities, with real-time chat, booking workflow, and human-in-the-loop escalation via email.


##  Overview

This project is a multi-agent travel assistant built using:

* **FastAPI** (Backend API)
* **React + Vite + TypeScript** (Frontend UI)
* **Google ADK + LiteLLM** (LLM agent orchestration)
* **SMTP (Gmail)** for email escalation
* **IMAP polling** for supervisor reply injection

The assistant can:

* Provide detailed activity information (images, pricing, policies)
* Handle bookings with validation logic
* Escalate complex cases to a human supervisor
* Inject supervisor replies back into chat automatically
* Render activity images directly inside chat bubbles

---

##  Architecture

### 🔹 Multi-Agent Design

The system consists of:

1. **Root Conversation Agent**

   * Orchestrates conversation
   * Routes to information or booking tools
   * Enforces escalation rules

2. **Information Agent**

   * Fetches activity details
   * Returns images, policies, pricing

3. **Booking Agent**

   * Validates availability
   * Creates bookings
   * Triggers escalation if needed

4. **Human-in-the-Loop System**

   * Sends escalation emails via SMTP
   * Polls supervisor inbox via IMAP
   * Injects supervisor response into active chat

---

##  Project Structure

```
multi-agent-travel-assistant/
│
├── backend/
│   ├── app/
│   │   ├── agents.py
│   │   ├── conversation_manager.py
│   │   ├── email_service.py
│   │   ├── imap.py
│   │   ├── mock_db.py
│   │   ├── models.py
│   │   ├── main.py
│   │   └── config.py
│   └── travelagent_env/
│
├── frontend/
│   ├── src/
│   │   ├── Chat.tsx
│   │   ├── App.tsx
│   │   └── App.css
│   └── vite.config.ts
│
└── README.md
```

---

#  Setup Instructions

---

## 1️⃣ Backend Setup

### Step 1 — Create Virtual Environment

```bash
cd backend
python -m venv travelagent_env
travelagent_env\Scripts\activate   # Windows
```

---

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

If no requirements file exists:

```bash
pip install fastapi uvicorn pydantic pydantic-settings requests google-adk litellm python-dotenv
```

---

### Step 3 — Configure Environment Variables

Create a `.env` file inside `/backend/app/`:

```
OPENAI_API_KEY=your_openai_key_here

# SMTP (Escalation Sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_supervisor_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_supervisor_email@gmail.com
SUPERVISOR_EMAIL=your_supervisor_email@gmail.com

# IMAP (Supervisor Reply Polling)
SUPERVISOR_IMAP_HOST=imap.gmail.com
SUPERVISOR_IMAP_PORT=993
SUPERVISOR_IMAP_EMAIL=your_supervisor_email@gmail.com
SUPERVISOR_IMAP_APP_PASSWORD=your_gmail_app_password
```

---

###  How To Generate Gmail App Password

1. Enable 2FA on Gmail.
2. Go to Google → Security → App Passwords.
3. Generate password for "Mail".
4. Use that password for both SMTP and IMAP.

---

### Step 4 — Run Backend API

```bash
uvicorn app.main:app --reload --port 8000
```

Backend runs at:

```
http://localhost:8000
```

---

### Step 5 — Run IMAP Poller (Terminal 2)

```bash
python -m app.imap
```

This:

* Connects to Gmail
* Checks for supervisor replies
* Injects responses into chat

---

## 2️⃣ Frontend Setup

### Step 1 — Install Dependencies

```bash
cd frontend
npm install
```

---

### Step 2 — Configure API URL

In `.env` inside frontend:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

---

### Step 3 — Run Frontend

```bash
npm run dev
```

Open:

```
http://localhost:5173
```

---

#  How The Flow Works

###  Information Request

User:

> Give me details for Desert Safari

Assistant:

* Fetches activity
* Returns description + pricing
* Outputs image URLs
* Frontend renders images

---

###  Booking Flow

User:

> I want to book Private 4x4 for 5 people

Assistant:

* Validates group size
* Creates booking
* Returns confirmation

---

###  Escalation Flow

User:

> Can I get 90% discount?

Assistant:

* Calls escalate tool
* Sends email to supervisor

Supervisor:

* Replies to email

IMAP:

* Detects reply
* Injects into chat

Frontend:

* Displays supervisor message

---

#  Image Rendering

Images are:

* Stored in mock DB
* Returned by information tool
* Printed as raw URLs
* Extracted via regex
* Rendered as `<img>` inside chat bubble

---

# 🛠 Technologies Used

| Layer    | Technology                |
| -------- | ------------------------- |
| Backend  | FastAPI                   |
| Agents   | Google ADK + LiteLLM      |
| LLM      | OpenAI GPT-4.1            |
| Frontend | React + Vite + TypeScript |
| Email    | SMTP + IMAP (Gmail)       |
| State    | In-memory session store   |

---

#  Demo Test Scenarios

### Information

```
Give me details for Burj Khalifa
```

### Booking

```
Book Private 4x4 for 4 people on 20th Dec
```

### Escalation

```
Can you give me 90% discount?
```

Reply via supervisor email and watch it appear in chat.

---

#  Future Improvements

* Replace polling with WebSocket for real-time updates
* Replace IMAP polling with webhook (SendGrid/Gmail API)
* Store data in PostgreSQL instead of in-memory
* Add booking approval endpoint
* Add admin dashboard
* Add image carousel
* Add authentication layer

---

#  Why This Project Is Strong

This demonstrates:

* Multi-agent orchestration
* Tool-based LLM reasoning
* Human-in-the-loop architecture
* Email integration
* Real-time frontend updates
* Structured output control
* Clean separation of concerns

This is a production-style applied AI system.

