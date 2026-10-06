import google.generativeai as genai
import uuid
import asyncio
from src.core.config import settings
from src.services.memory import memory_manager
from src.models.schemas import ActionIntent
from duckduckgo_search import DDGS 

def set_alarm(time: str, message: str = ""):
    """Sets an alarm on the Android device.
    Args:
        time: Time in HH:MM format (e.g., 08:00).
        message: Title or note for the alarm.
    """
    pass

def open_app(app_name: str):
    """Opens an application on the Android device.
    Args:
        app_name: Name of the app (e.g., Telegram, YouTube).
    """
    pass

def set_timer(duration_seconds: int, message: str = ""):
    """Starts a timer on the Android device.
    Args:
        duration_seconds: Timer duration in seconds.
        message: Title of the timer.
    """
    pass

def create_note(title: str, content: str):
    """Creates a text note on the device.
    Args:
        title: Title of the note.
        content: Content of the note.
    """
    pass

def search_internet(query: str):
    """Searches the internet for up-to-date information (weather, news, facts).
    Args:
        query: Search query.
    """
    pass

ANDROID_TOOLS = ["set_alarm", "open_app", "set_timer", "create_note"]


class RylanorBrain:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        system_instruction = (
            "You are Rylanor, a personal AI assistant for Android. "
            "Your responses will be converted to speech (TTS), so DO NOT use markdown formatting, asterisks, or long lists. "
            "ALWAYS reply in Russian.\n\n"
            "Behavioral Rules:\n"
            "1. Fact & Command Mode: If the user asks for a specific fact, requests a web search, or gives a command (alarm, timer, note), "
            "answer extremely concisely and directly. No fluff, no 'water', just the requested information or confirmation.\n"
            "2. Conversational Mode: If the user is casually chatting, sharing thoughts, or joking, act as an engaging, warm, and natural conversational partner. Ask counter-questions if appropriate.\n\n"
            "Use the provided context from past conversations if it is relevant."
        )
        
        self.model = genai.GenerativeModel(
            model_name='gemini-3.7-flash',
            system_instruction=system_instruction,
            tools=[set_alarm, open_app, set_timer, create_note, search_internet]
        )

    async def _extract_and_save_facts(self, user_id: str, message: str, ai_reply: str):
        prompt = f"""
        Analyze the following short dialogue. Your task is to extract only important facts about the user 
        (name, preferences, habits, important events, deadlines) that should be saved in long-term memory.
        
        Dialogue:
        User: {message}
        AI: {ai_reply}
        
        If there are no important facts to remember, output exactly one word: NONE.
        If there are facts, write them concisely in Russian as statements (e.g., "Пользователь не любит лук").
        """
        
        extractor = genai.GenerativeModel('gemini-1.5-flash')
        
        try:
            response = await extractor.generate_content_async(prompt)
            facts = response.text.strip()
            
            if facts and "NONE" not in facts.upper():
                doc_id = str(uuid.uuid4())
                memory_manager.add_to_long_term(user_id, facts, doc_id)
                print(f"[Умная память] Сохранен новый факт: {facts}")
        except Exception as e:
            print(f"[Умная память] Ошибка при извлечении фактов: {e}")
        
    async def process_message(self, user_id: str, message: str) -> tuple[str, ActionIntent | None]:
        context = memory_manager.get_relevant_context(user_id, message)
        
        if context:
            enriched_message = f"[Past context: {context}]\n\nCurrent request: {message}"
        else:
            enriched_message = message

        history = memory_manager.get_short_term(user_id)
        
        chat = self.model.start_chat(history=history)
        
        response = chat.send_message(enriched_message)


        
        action_intent = None
        
        if response.function_call:
            fc = response.function_call
            func_name = fc.name
            args = dict(fc.args)
            
            if func_name in ANDROID_TOOLS:
                action_intent = ActionIntent(
                    action_type=func_name.upper(),
                    parameters=args
                )
                
                response = chat.send_message(
                    genai.types.Part.from_function_response(
                        name=func_name, response={"status": "success"}
                    )
                )
            elif func_name == "search_internet":
                print(f"[Поиск в сети] Ищу: {args.get('query')}")
                try:
                    results = DDGS().text(args.get("query"), max_results=3)
                    search_result_text = "\n".join([f"{r['title']}: {r['body']}" for r in results])
                except Exception as e:
                    search_result_text = "Ошибка при поиске информации в интернете."

                response = chat.send_message(
                    genai.types.Part.from_function_response(
                        name=func_name, response={"results": search_result_text}
                    )
                )

        ai_reply = response.text

        memory_manager.add_to_short_term(user_id, "user", message)
        memory_manager.add_to_short_term(user_id, "model", ai_reply)
        
        import asyncio
        asyncio.create_task(self._extract_and_save_facts(user_id, message, ai_reply))

        return ai_reply, action_intent

rylanor_brain = RylanorBrain()