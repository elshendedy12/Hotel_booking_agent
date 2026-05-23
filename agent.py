import json
import re
from datetime import datetime
from groq import Groq
from schemas import RoomBookingSchema
from tools import check_room_availability, load_preferences, save_preferences

class StableBookingAgent:
    def __init__(self, user_id: str, api_key: str):
        self.user_id = user_id
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"
        
        self.past_prefs = load_preferences(user_id)
        current_today = datetime.today().strftime('%Y-%m-%d')
        day_name = datetime.today().strftime('%A')
        
        self.system_instruction = f"""You are an autonomous Hotel Room Booking Assistant.
STRICT SCOPE: Exclusively handle hotel room bookings. Do NOT assist with flights or tours.
CURRENT DATE: Today is {day_name}, {current_today}.

HISTORICAL USER PREFERENCES:
{self.past_prefs}

YOUR OPERATIONAL FLOW:
1. If user dates are before {current_today}, immediately reject and say you cannot book in the past.
2. Use 'check_room_availability' immediately when room types and dates are discussed.
3. Your only job is to chat and collect exactly 4 fields: guest_name, room_type, check_in_date, and check_out_date. 
4. Once you have confirmed ALL 4 fields are ready and available, simply tell the user that you are ready to confirm and ask for their final approval. Do NOT write any function tags, tags like <function>, or raw JSON code in your responses.
"""
        self.conversation_history = [{"role": "system", "content": self.system_instruction}]

        self.tools_definition = [
            {
                "type": "function",
                "function": {
                    "name": "check_room_availability",
                    "description": "Check if a specific room type is available for the given dates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room_type": {"type": "string"},
                            "check_in_date": {"type": "string"},
                            "check_out_date": {"type": "string"}
                        },
                        "required": ["room_type", "check_in_date", "check_out_date"]
                    }
                }
            }
        ]

    def chat(self, user_message: str, st_callback=None) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})
        
        
        casual_words = ["thanks", "thank you", "hello", "hi","bye"]
        if any(word in user_message.lower() for word in casual_words) and len(user_message.split()) < 4:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are a polite hotel assistant. Reply briefly and politely."}] + self.conversation_history[-3:],
                temperature=0.5
            )
            ai_reply = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_reply})
            return ai_reply

        
        confirmation_intents = ["yes", "ok", "confirm", "it's it", "thats it"]
        if any(intent in user_message.lower() for intent in confirmation_intents):
            if st_callback: st_callback("⚡ Python Controller: Analyzing history for auto-finalization...")
            extracted_args = self._force_extract_data_from_history()
            if extracted_args and all(extracted_args.values()):
                return self._execute_pydantic_seal(extracted_args, st_callback)

        # 3. نداء الموديل الطبيعي
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.conversation_history,
            tools=self.tools_definition,
            tool_choice="auto",
            temperature=0.0
        )
        
        response_message = response.choices[0].message
        ai_reply = response_message.content or ""
        
        
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if name == "check_room_availability":
                    if st_callback: st_callback(f"⚙️ [Executing Tool]: {name}...")
                    tool_result = check_room_availability(
                        room_type=args.get("room_type"),
                        check_in_date=args.get("check_in_date"),
                        check_out_date=args.get("check_out_date")
                    )
                    if st_callback: st_callback(f"📦 [Tool Result]: {tool_result['message']}")
                    
                    self.conversation_history.append(response_message)
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(tool_result)
                    })
                    
                    second_response = self.client.chat.completions.create(
                        model=self.model_name, messages=self.conversation_history, temperature=0.0
                    )
                    final_text = second_response.choices[0].message.content
                    self.conversation_history.append({"role": "assistant", "content": final_text})
                    return final_text

        # XML Tags error
        ai_reply = re.sub(r"<function.*?>.*?</function>", "", ai_reply).strip()
        ai_reply = re.sub(r"finalize_booking\(.*?\)", "", ai_reply).strip()

        self.conversation_history.append({"role": "assistant", "content": ai_reply})
        return ai_reply

    def _force_extract_data_from_history(self) -> dict:
        
        try:
            extract_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a data extraction bot. Look at the conversation history and extract the latest booking parameters. Output ONLY a clean valid JSON object with keys: guest_name, room_type, check_in_date, check_out_date. No markdown, no text, no tags."},
                    {"role": "user", "content": f"History:\n{str(self.conversation_history[-6:])}"}
                ],
                temperature=0.0
            )
            text = extract_response.choices[0].message.content
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return {}

    def _execute_pydantic_seal(self, args: dict, st_callback) -> str:
        if st_callback: st_callback("🛡️ Shield Active: Running Pydantic Schema Validation...")
        try:
            validated_data = RoomBookingSchema(**args)
            save_preferences(self.user_id, f"User prefers room type: {validated_data.room_type}. Confirmed Name: {validated_data.guest_name}")
            
            return f"🎉 **Booking Sealed Successfully (via Python Controller)!**\n\nReservation locked for **{validated_data.guest_name}** ({validated_data.room_type}) from {validated_data.check_in_date} to {validated_data.check_out_date}.\n\n```json\n{validated_data.model_dump_json(indent=2)}\n```"
        
        except Exception as e:
            if st_callback: st_callback(f"⚠️ Validation Failed: {str(e)}")
            error_msg = str(e)
            
            
            if "both a first and last name" in error_msg:
                return "⚠️ **Please provide your full name (First and Last name)** so I can finalize your booking properly."
            
            elif "strictly after the check-in" in error_msg or "after check-in date" in error_msg:
                return "⚠️ **Invalid Dates:** Your check-out date must be strictly *after* your check-in date. Please correct the dates to proceed."
            
            elif "cannot be in the past" in error_msg or "in the past" in error_msg:
                return "⚠️ **The dates you provided are in the past.** Please update your request with upcoming future dates."
            
            
            return "⚠️ I couldn't complete the booking. Please make sure you've provided a valid full name and logically correct future dates."