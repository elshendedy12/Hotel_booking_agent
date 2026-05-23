# 🏨 Smart Hotel Booking Dynamic Concierge Agent

An autonomous, multi-turn AI Agent designed exclusively for hotel room bookings. This project implements a **Hybrid Agent Pattern** that combines LLM reasoning (via Groq & Llama-3.3-70b) with rigid structural validation using **Pydantic**, alongside a persistent long-term memory layer powered by **SQLite**.

---

## 🚀 Key Features

- **Autonomous Agentic Loop:** Operates dynamically via native LLM function calling rather than a rigid, linear form-filling prompt.
- **Pydantic Validation Shield:** Enforces strict compliance with business rules (ISO date formats, chronological check-in/out order, and full guest name requirements).
- **Dynamic Self-Correction (Self-Healing):** Catches validation exceptions, passes the raw error string back to the LLM context, and lets the agent autonomously correct its mistakes with the user.
- **Long-Term Preference Memory (Bonus Track):** Automatically extracts and persists user preferences into a local SQLite database at the end of successful bookings, loading them cleanly upon subsequent sessions.
- **Interactive Session Logs:** Features a dedicated Streamlit sidebar that outputs dynamic, live tracking of agent operations, tool executions, and self-correction chains.

---

## 📂 Project Structure

- `app.py`: Streamlit frontend UI state management and dynamic sidebar log visualizer.
- `agent.py`: Continuous operational loop orchestration, multi-turn history handling, and self-correction triggering.
- `schemas.py`: Pydantic configurations with robust field and model-level validators.
- `tools.py`: Deterministic mock availability tool and SQLite persistent storage interaction handlers.

---

## 🛠️ Setup & Installation Instructions

### 1. Clone the Repository
```bash
git clone [https://github.com/elshendedy12/Hotel_booking_agent.git](https://github.com/elshendedy12/Hotel_booking_agent.git)
cd Hotel_booking_agent


2. Create and Activate a Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate



3. Install Required Dependencies
pip install -r requirements.txt
(If you don't have a requirements file yet, run: pip install streamlit pydantic groq python-dotenv)


4. Environment Variables Configuration
Create a .env file in the root directory and append your Groq API Key:

GROQ_API_KEY=your_actual_groq_api_key_here


5. Launch the Application
streamlit run app.py

🛡️ Practical Session Logs & Validation Flow
When interacting with the agent:

Missing Parameters: The agent intelligently probes for missing details (Name, Room Type, Dates) instead of using static fields.

Execution: Once valid inputs match, check_room_availability triggers automatically.

Self-Correction Demonstration: If an invalid name (e.g., single name) or a past date is provided, the backend catches the Pydantic exception, appends it to the LLM chat history, and the agent asks the user for a tailored correction.