# multi-agent-travel-assistant-system

What I’ve set up so far
Backend (Python + FastAPI + Google ADK)
Project layout

backend/requirements.txt with:
fastapi, uvicorn[standard], google-adk, python-dotenv

backend/app/ package with:
config.py – central settings (app name, API prefix, GOOGLE_API_KEY, ADK model, CORS origin, SMTP config).

models.py – Pydantic models for:
Activity, ActivityVariation
Booking (+ BookingStatus)
Escalation
ChatMessage (+ ChatRole), ChatMessageCreate, ChatMessageResponse
mock_db.py – mock database with at least 10 Dubai activities:
Burj Khalifa, Desert Safari, Dubai Marina cruise, Dubai Frame, Global Village, Aquaventure, Skydive Palm, Miracle Garden, Dolphinarium, La Perle show.
Each has multiple variations (time slots, capacities, pricing), plus images, cancellation policy, reschedule policy.
Also in‑memory stores for BOOKINGS and ESCALATIONS, with helpers:
list_activities(), get_activity(...)
create_booking(...)
create_escalation(...)
email_service.py – simple escalation email sender:
Uses SMTP config from env.
If SMTP isn’t configured, it logs the email to stdout (so the escalation flow is demonstrable without a real provider).

agents.py – Google ADK multi-agent setup:

Tools:
search_activities_tool(query): full‑text search over activities.
get_activity_details_tool(activity_id)
get_pricing_for_variation_tool(activity_id, variation_id)

book_activity_tool(...):
Creates a Booking.
If variation is unavailable or group size invalid, marks booking as PENDING_SUPERVISOR, creates an Escalation, and calls send_escalation_email(...) with all booking details and reason.
Otherwise confirms immediately (BookingStatus.CONFIRMED).

Agents (LlmAgent):
information_agent – handles pictures, policies, pricing, general info using the info tools.
booking_agent – handles booking flow, calling booking tool and explaining supervisor reviews when needed.

conversation_handler (root):
Description + instructions tuned for Dubai activities + WhatsApp-style UX.

Tools:
AgentTool(agent=information_agent)
AgentTool(agent=booking_agent)
The shared DB+booking tools.
Instruction tells it to:
Route info queries vs booking queries.
Treat multiple short user messages as one combined request.
Explain supervisor escalation when it happens.

Global ADK runtime:
InMemorySessionService + Runner(agent=conversation_handler, app_name=...).
Helper build_agents() returns (root_agent, runner).

conversation_manager.py – message interruption / aggregation handler:

In‑memory structures:
CONVERSATIONS: Dict[conversation_id, List[ChatMessage]]

CONVERSATION_STATES: Dict[conversation_id, ConversationState] with:
pending_texts, is_processing.

Functions:
append_message(...), get_conversation_messages(...), get_or_create_state(...).

process_pending_messages(conversation_id, runner, app_name):
Designed to run as a FastAPI background task.

Implements interruption handling:
Waits ~0.4s, aggregates all pending_texts into one combined prompt.
Ensures an ADK session for that conversation.
Calls runner.run(user_id=conversation_id, session_id=conversation_id, new_message=Content(...)).
Streams events and, for each event.is_final_response(), collects text and appends a ChatMessage with role assistant.

main.py – FastAPI app & REST API:

Global initialization:
settings = get_settings()
root_agent, runner = build_agents()
app = FastAPI(title=settings.app_name)
Optional CORS if FRONTEND_ORIGIN is set.

Endpoints:
GET /health – health check.
GET /api/activities – returns all mock activities (with variations, images, policies, pricing).
GET /api/chat/{conversation_id} – returns ChatMessageResponse (all messages for that conversation).
POST /api/chat/{conversation_id}:
Accepts { "text": string }.
Appends a ChatMessage with role user.
Adds text to that conversation’s pending_texts.
If not already processing, schedules process_pending_messages(...) as a background task to aggregate and send to the ADK multi-agent runner.
Returns the created user message.

POST /api/escalations/{conversation_id}/supervisor-reply:
Simulates human-in-the-loop email reply.
Accepts { "message": string }.
Injects a ChatMessage with role supervisor into the conversation history.
Frontend then sees supervisor messages seamlessly in the chat.

This covers:
Activity Booking Agent (booking tools).
Information Agent (info tools).
Human-in-the-loop (email escalation + supervisor reply endpoint).
Conversation Handler with multi-message aggregation and context via ADK Runner + InMemorySessionService.
Frontend (React + Vite, WhatsApp-style UI)
Scaffold
Generated via Vite: frontend/ with React + TypeScript template.
Main components
src/App.tsx

Replaced template with:
App rendering a full-screen container and the Chat component (<div className="app-root"><Chat /></div>).
src/Chat.tsx

Implements a WhatsApp-themed chat interface:

Types:
ChatRole union ('user' | 'assistant' | 'supervisor' | 'system').
ChatMessage aligned with backend shape.

Config:
API_BASE from VITE_API_BASE_URL (defaults to http://localhost:8000/api).
Fixed DEFAULT_CONVERSATION_ID = 'demo-conversation' for now.

Behavior:

Polling for real-time updates:
useEffect polls GET {API_BASE}/chat/demo-conversation every ~1.2s and updates messages.

Sending messages:
handleSend() posts to POST {API_BASE}/chat/demo-conversation with { text }.
Supports Enter-to-send.

Auto-scroll:
Keeps view scrolled to latest messages.

Renders messages via MessageBubble:
Different bubble styling for:
User (role === 'user').
Assistant (default).
Supervisor (tagged with a small “Supervisor” label).

Header mimics WhatsApp style:
Avatar circle with “DA”.
Title “Dubai Activities Assistant” and “online” subtitle.
src/App.css

Completely replaced with a WhatsApp-like theme:
Dark chat container with:
Rounded corners, subtle border and shadow.
Gradient header similar to WhatsApp Web.

Chat body:
Dark background + subtle texture.

Bubbles:
User bubbles: right-aligned, greenish (#005c4b).
Assistant bubbles: left-aligned, dark gray (#202c33).
Supervisor bubbles: left-aligned, gray-blue, with yellow accent border and “Supervisor” label.

Input bar:
Rounded input + “Send” button styled close to WhatsApp’s send CTAs.
Fully responsive within viewport (100vw / 100vh).




How to run it locally
Backend

From repo root:
cd backend

Create a virtualenv (recommended):
Windows PowerShell:
python -m venv .venv
.venv\Scripts\Activate.ps1

Install deps:
pip install -r requirements.txt

Set env vars (at minimum):
GOOGLE_API_KEY for ADK (Gemini API).
Optionally SMTP config (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SUPERVISOR_EMAIL) if you want real escalation emails.
Without these, escalation emails are printed to the console.

Run FastAPI (e.g.):
uvicorn app.main:app --reload --port 8000
Test:
GET http://localhost:8000/health
GET http://localhost:8000/api/activities
POST http://localhost:8000/api/chat/demo-conversation with { "text": "Show me desert safaris" }.



Frontend
From repo root:
cd frontend
npm install
Create .env in frontend/ (optional but recommended):
VITE_API_BASE_URL=http://localhost:8000/api
Run dev server:
npm run dev
Open the Vite URL (usually http://localhost:5173) and start chatting.
Next steps I can add
Create a concise README and ARCHITECTURE.md describing:
Multi-agent design (information/booking/conversation agents + human-in-the-loop).
How interruption handling and message aggregation work.
Enhance the UI to show activity images inline when the assistant mentions them.
Add a small dev control/endpoint to easily simulate supervisor approvals/rejections with structured payloads.
If you’d like, I can next focus on: (a) polishing the WhatsApp UI further, (b) expanding the ADK agent instructions/tools, or (c) writing the README + architecture doc.


If index.html is missing:

Run this from frontend folder:

npm create vite@latest .

############################
Perfect — we found the issue.

You **do not have `index.html`** in the frontend root.

That is exactly why Vite is returning 404.

Vite serves the `index.html` file from the project root.
If it doesn’t exist → 404.

---

# ✅ Why This Happened

You likely:

* Copied only `src/`, `package.json`, and `node_modules`
* But never created the actual Vite project scaffold

A Vite React project must have:

```
frontend/
 ├── index.html   ❗ REQUIRED
 ├── package.json
 ├── vite.config.ts (or js)
 └── src/
```

You’re missing:

* index.html
* vite.config.ts
* main.tsx (probably inside src)

---

# 🚀 CLEAN FIX (DO THIS)

Inside your `frontend` folder:

### 1️⃣ Delete everything inside frontend EXCEPT:

Keep:

* src/ (your code)
* package.json
* package-lock.json (optional)

Then run:

```bash
npm create vite@latest .
```

Choose:

* React
* TypeScript (if you're using TS)

It will generate:

* index.html
* vite.config.ts
* proper project structure

---

### 2️⃣ Then run:

```bash
npm install
```

---

### 3️⃣ Make sure your structure becomes:

```
frontend/
 ├── index.html
 ├── package.json
 ├── vite.config.ts
 └── src/
     ├── main.tsx
     ├── App.tsx
     ├── Chat.tsx
```

If `main.tsx` doesn’t exist, create it:

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

---

### 4️⃣ Then run:

```bash
npm run dev
```

Now open the port it shows.

It will work.

---

# 🎯 Root Cause Summary

Your frontend was not actually a Vite project.
It was just a folder with React files.

Vite needs index.html at root to serve `/`.

---

Do this and tell me once it starts loading — then we’ll test full chat flow.
######################

