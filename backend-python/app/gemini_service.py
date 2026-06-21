import os
import json
import traceback
import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional
from app.circuit_breaker import gemini_cb, CircuitBreakerOpen
# Configuration handled in server.py
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_APP_DIR)
_DOTENV_PATH = os.path.join(_BACKEND_DIR, '.env')

# ===== LAZY INITIALIZATION WITH MODEL FALLBACK =====
_model: Optional[genai.GenerativeModel] = None
_model_initialized = False
_model_name = None
_configured_api_key: Optional[str] = None

# Models to try in order (first working one wins)
_env_model = os.getenv("GEMINI_MODEL", "").strip()
MODEL_CANDIDATES = []
if _env_model:
    MODEL_CANDIDATES.append(_env_model)

for candidate in [
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
]:
    if candidate not in MODEL_CANDIDATES:
        MODEL_CANDIDATES.append(candidate)



def _get_model() -> Optional[genai.GenerativeModel]:
    """Lazily initialize the Gemini model on first use with automatic fallback."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    global _model, _model_initialized, _model_name, _configured_api_key

    # Fast path: already initialized for the same key.
    if _model_initialized and api_key == _configured_api_key:
        return _model

    # If key changed during runtime, allow re-initialization without server restart.
    if _model_initialized and api_key != _configured_api_key:
        print("[Gemini] GEMINI_API_KEY changed; reinitializing Gemini model...")
        _model = None
        _model_name = None
        _model_initialized = False

    if not api_key:
        _model = None
        _model_initialized = True
        _configured_api_key = None
        # Bug #4: Show a helpful, actionable message when the key is missing.
        env_keys = [k for k in os.environ if 'GEMINI' in k or 'GOOGLE' in k or 'API_KEY' in k]
        hint = f"Available env keys matching GEMINI/GOOGLE/API_KEY: {env_keys}" if env_keys else "No GEMINI/GOOGLE env keys found in environment."
        print("")
        print("=" * 60)
        print("[Gemini] GEMINI_API_KEY / GOOGLE_API_KEY is not set - AI features are disabled.")
        print(hint)
        print(f"   Set GEMINI_API_KEY in {_DOTENV_PATH} to enable AI chat & workout config.")
        print("   Get a key at: https://aistudio.google.com/app/apikey")
        print("=" * 60)
        print("")
        return None

    # Enhanced diagnostic: Log API key presence (masked)
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"[Gemini] Attempting to initialize with API key: {masked_key}")
    print(f"[Gemini] Model candidates: {MODEL_CANDIDATES}")

    try:
        genai.configure(api_key=api_key)
        _configured_api_key = api_key
        print(f"[Gemini] Configuration successful")
    except Exception as e:
        print(f"[Gemini] configure failed: {e}")
        _model = None
        _model_initialized = True
        _configured_api_key = None
        return None

    # Try each model candidate until one works
    for candidate in MODEL_CANDIDATES:
        try:
            print(f"[Gemini] Testing model: {candidate}...")
            test_model = genai.GenerativeModel(candidate)

            # Validation call: avoid tiny token limits and ensure we can read text output.
            response = test_model.generate_content(
                "Reply exactly with: OK",
                generation_config=genai.types.GenerationConfig(max_output_tokens=32, temperature=0),
            )

            has_text = False
            response_text = getattr(response, "text", None)
            if isinstance(response_text, str) and response_text.strip():
                has_text = True
            else:
                candidates = getattr(response, "candidates", None) or []
                if candidates:
                    first = candidates[0]
                    content = getattr(first, "content", None)
                    parts = getattr(content, "parts", None) or []
                    has_text = any(getattr(p, "text", "").strip() for p in parts)

            if not has_text:
                finish_reason = None
                candidates = getattr(response, "candidates", None) or []
                if candidates:
                    finish_reason = getattr(candidates[0], "finish_reason", None)
                raise RuntimeError(f"validation returned empty text (finish_reason={finish_reason})")

            _model = test_model
            _model_name = candidate
            print(f"[Gemini] AI initialized successfully with model: {candidate}")
            break
        except Exception as e:
            err_str = str(e).lower()
            if '429' in err_str or 'quota' in err_str or 'exhausted' in err_str:
                print(f"[Gemini] Model {candidate}: quota exhausted, trying next...")
            elif '404' in err_str or 'not found' in err_str:
                print(f"[Gemini] Model {candidate}: not available, trying next...")
            else:
                print(f"[Gemini] Model {candidate}: {type(e).__name__}: {str(e)[:80]}")
    
    if _model is None:
        print("[Gemini] All Gemini models failed. AI chatbot will use offline fallback responses.")

    _model_initialized = True
    return _model


def is_gemini_available() -> bool:
    """Return True only when a Gemini model is actually initialized and usable."""
    return _get_model() is not None


def generate_workout_config(profile: Dict[str, Any], intensity: float) -> Optional[Tuple[int, str, int, list]]:
    """
    Given a user profile and an intensity goal, use Gemini to intelligently
    determine the perfect: (sets, reps_range, rest_time_sec, rest_days_list)
    """
    model = _get_model()
    if not model:
        print("Gemini model not initialized, skipping AI workout config.")
        return None

    prompt = f"""
    You are an elite fitness AI. Return ONLY valid JSON, NO markdown.
    
    Given this user profile:
    - Age: {profile.get('age', 'Unknown')}
    - Goal: {profile.get('goal', 'General Fitness')}
    - Experience: {profile.get('experience', 'Beginner')}
    - Injuries: {', '.join(profile.get('body_issues', []))}
    - Requested Days Per Week: {profile.get('days_per_week', 4)}
    
    Return EXACTLY these four keys:
    "sets": <integer 1-6>,
    "reps": <string range, e.g. "8-12">,
    "rest": <integer seconds, e.g. 60>,
    "rest_days": <a list of integers from 0 to 6 representing the rest days in a 7-day week, e.g. [2, 6] or [1, 3, 5]>
    
    Make the rest days specifically cater to their experience and requested schedule.
    """

    try:
        # ARCH-7: Route through circuit breaker — if Gemini is repeatedly
        # failing (quota, network outage) the circuit opens and we skip
        # further calls until the breaker resets.
        def _call():
            response = model.generate_content(prompt)
            text_resp = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text_resp)
            return (
                int(data.get('sets', 3)),
                str(data.get('reps', '10-12')),
                int(data.get('rest', 60)),
                list(data.get('rest_days', [2, 6])),
            )
        return gemini_cb.call(_call)
    except CircuitBreakerOpen as cbo:
        print(f"[Gemini] {cbo}")
        return None
    except Exception as e:
        print(f"Failed to generate AI request: {e}")
        return None


# ===== CHATBOT =====

# Maximum conversation history to send to Gemini (prevents token overflow)
MAX_HISTORY_MESSAGES = 20
# Maximum characters per user message
MAX_MESSAGE_LENGTH = 2000

# ===== OFFLINE FALLBACK RESPONSES =====
# Enhanced offline responses that actually provide value when API is unavailable
FALLBACK_RESPONSES = {
    'greeting': "Hey there! 👋 I'm your Elevate AI Coach. I'm currently running in offline mode to give you instant answers!\n\n💡 **Quick Tip:** Focus on compound exercises like squats, deadlifts, and bench press — they give you the most bang for your buck!\n\n🔥 **Today's Motivation:** Consistency beats perfection. Show up every day!\n\nAsk me about workouts, nutrition, or recovery — I've got plenty of built-in knowledge to share!",
    'workout': "Great that you're thinking about workouts! 💪 Here's expert advice:\n\n**Training Splits by Level:**\n• **Beginners:** 3-4 days/week, full body (squats, push-ups, rows)\n• **Intermediate:** 4-5 days/week, upper/lower or push/pull/legs\n• **Advanced:** 5-6 days/week, specific muscle group focus\n\n**Key Principles:**\n• Progressive overload: Add weight/reps weekly\n• Rest 48 hours before training same muscle\n• Form > weight — always!\n\nWhat specific exercise or muscle group are you targeting? 🎯",
    'nutrition': "Nutrition is 80% of your results! 🥗 Here's what works:\n\n**By Goal:**\n• **Muscle Gain:** 300-500 cal surplus, 1.6-2.2g protein/kg bodyweight\n• **Weight Loss:** 300-500 cal deficit, prioritize protein to keep muscle\n• **Maintenance:** Match calories, focus on whole foods\n\n**Daily Targets:**\n• Protein: 1.6-2.2g per kg bodyweight\n• Carbs: 3-5g per kg (higher on training days)\n• Fats: 0.8-1g per kg\n• Water: 2-3 liters minimum\n\nWant meal timing tips or specific food recommendations? 🍎",
    'recovery': "Smart question! Recovery is where gains happen! 😴\n\n**Sleep (Most Important!):**\n• 7-9 hours per night\n• Same sleep/wake times daily\n• No screens 1 hour before bed\n\n**Active Recovery:**\n• Light walking on rest days\n• 10-15 mins stretching post-workout\n• Foam rolling for tight muscles\n\n**Signs You Need More Rest:**\n• Persistent soreness >72 hours\n• Decreased performance\n• Trouble sleeping or irritability\n\nListen to your body — it's telling you something! 🧘",
    'form': "Form is EVERYTHING! 🎯 Poor form = injuries + poor results\n\n**Universal Cues:**\n• **Core:** Brace like someone's punching your stomach\n• **Breathing:** Exhale on effort, inhale on return\n• **Tempo:** Control the weight — no bouncing!\n• **Range:** Full range of motion beats partial reps\n\n**Common Mistakes:**\n• Squats: Knees caving in, heels lifting\n• Deadlifts: Rounding lower back\n• Bench: Flared elbows (keep 45-75°)\n• Overhead: Arching lower back excessively\n\nWant specific form tips for an exercise? 📹",
    'motivation': "You got this! 🔥 Here's your motivation boost:\n\n**Remember:**\n• Progress, not perfection\n• One workout is better than zero\n• Compare yourself to yesterday's you\n• Results come from consistency, not intensity\n• Even elite athletes have bad days\n\n**When You Don't Feel Like Training:**\n1. Put on gym clothes (commitment device)\n2. Tell yourself 'just 10 minutes'\n3. Once started, you'll usually finish\n4. If not — rest is also productive!\n\nYou're building a lifestyle, not rushing to a destination. 💪",
    'default': "Great question! 🤔 I'm currently in offline mode with instant responses. Here's what I can help with:\n\n**Ask me about:**\n• 💪 **Workouts** — exercise selection, splits, progression\n• 🥗 **Nutrition** — macros, meal timing, food choices\n• 🎯 **Form tips** — technique cues, common mistakes\n• 😴 **Recovery** — sleep, rest days, soreness management\n• 🔥 **Motivation** — staying consistent, mental game\n\nAll my offline knowledge is based on exercise science and fitness best practices. What would you like to dive into?"
}

def _get_fallback_response(message: str) -> str:
    """Return a helpful offline response when the AI is unavailable."""
    msg = message.lower()
    
    greetings = ['hi', 'hello', 'hey', 'sup', 'whats up', "what's up", 'good morning', 'good evening', 'yo', 'howdy']
    if any(g in msg for g in greetings):
        return FALLBACK_RESPONSES['greeting']
    
    # Check for motivation-related keywords first (before general workout)
    motivation_kw = ['motivation', 'motivate', 'inspire', 'discipline', 'lazy', 'dont feel', "don't feel", 'no energy', 'tired of', 'bored', 'quit', 'giving up', 'struggling', 'hard', 'difficult']
    if any(k in msg for k in motivation_kw):
        return FALLBACK_RESPONSES['motivation']
    
    # Check for form/technique keywords
    form_kw = ['form', 'technique', 'posture', 'position', 'alignment', 'stance', 'grip', 'how to do', 'proper way', 'correct', 'wrong', 'mistake', 'fix my', 'back hurts', 'knee hurts', 'elbow', 'wrist', 'shoulder']
    if any(k in msg for k in form_kw):
        return FALLBACK_RESPONSES['form']
    
    workout_kw = ['workout', 'exercise', 'training', 'gym', 'lift', 'push', 'pull', 'squat', 'bench', 'deadlift', 'curl', 'press', 'row', 'muscle', 'strength', 'cardio', 'hiit', 'split', 'routine', 'plan', 'schedule']
    if any(k in msg for k in workout_kw):
        return FALLBACK_RESPONSES['workout']
    
    nutrition_kw = ['eat', 'food', 'diet', 'meal', 'nutrition', 'calorie', 'protein', 'carb', 'fat', 'cook', 'recipe', 'supplement', 'creatine', 'whey', 'vitamin', 'water', 'hydration', 'bulk', 'cut', 'lose weight', 'gain weight']
    if any(k in msg for k in nutrition_kw):
        return FALLBACK_RESPONSES['nutrition']
    
    recovery_kw = ['sleep', 'rest', 'recovery', 'tired', 'sore', 'pain', 'stretch', 'injury', 'hurt', 'massage', 'foam roll', 'ice', 'heat', 'rest day', 'deload']
    if any(k in msg for k in recovery_kw):
        return FALLBACK_RESPONSES['recovery']
    
    return FALLBACK_RESPONSES['default']


def _build_contextual_offline_response(user_message: str, profile: Dict[str, Any], chat_history: list = None) -> str:
    """Return a deterministic offline reply that reflects the current conversation context."""
    summary_bits = []
    prefix = "AI service is temporarily unavailable. "

    experience = str(profile.get("experience", "")).strip()
    goal = str(profile.get("goal", "")).strip()
    equipment = profile.get("equipment")
    workout_days = profile.get("workout_days") or profile.get("days_per_week")

    if experience:
        summary_bits.append(f"you are a {experience.lower()} lifter")
    if goal:
        summary_bits.append(f"your goal is {goal.replace('_', ' ')}")
    if isinstance(equipment, list):
        if not equipment:
            summary_bits.append("you have no equipment")
        else:
            summary_bits.append(f"your equipment includes {', '.join(str(item) for item in equipment[:4])}")
    if workout_days:
        summary_bits.append(f"you want to train {workout_days} days per week")

    if chat_history:
        recent_text = " ".join(_extract_message_text(msg).lower() for msg in _trim_history(chat_history))
        history_hits = []
        for keyword in ["beginner", "muscle", "equipment", "days", "train", "workout", "squat", "push-up", "push up", "shape"]:
            if keyword in recent_text:
                history_hits.append(keyword)
        if history_hits:
            unique_hits = ", ".join(dict.fromkeys(history_hits))
            summary_bits.append(f"our recent chat focused on {unique_hits}")

    if not summary_bits:
        return prefix + _get_fallback_response(user_message)

    summary = "; ".join(summary_bits)
    return (
        f"{prefix}Offline coach note: I remember that {summary}. "
        f"Based on that, I’d keep things simple: build around the basics, stay consistent, and progress gradually."
    )


def _extract_message_text(msg: Dict[str, Any]) -> str:
    for key in ("text", "content", "message", "body"):
        value = msg.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _map_role(role: Any) -> str:
    role_str = str(role).lower()
    if role_str in {"assistant", "bot", "coach"}:
        return "Coach"
    return "User"


def _build_system_prompt(profile: Dict[str, Any]) -> str:
    """Build the system prompt with user profile context."""
    def _safe_join(val):
        if isinstance(val, list):
            return ', '.join(val)
        if isinstance(val, str):
            return val
        return 'None'

    return f"""You are 'Elevate AI', an elite personal fitness coach and nutritionist for the 'Elevate' platform.

PERSONALITY:
- Friendly, motivating, and knowledgeable
- Use short, punchy sentences. Be concise but helpful.
- Use relevant emojis sparingly (💪 🏋️ 🥗 etc.)
- Keep responses under 200 words unless the user asks for detailed info

STRICT SCOPE — You may ONLY discuss:
- Fitness, workouts, exercise form, training plans, recovery
- Nutrition, meal planning, supplements, hydration, diet strategies
- The Elevate platform features and navigation
- General wellness, sleep, stress management related to fitness

REFUSAL — If the user asks about ANYTHING outside this scope (coding, politics, math, history, etc.):
- Politely refuse: "I'm your fitness coach — I can only help with health, nutrition, and workout topics! 💪"
- Do NOT attempt to answer off-topic questions

USER PROFILE:
- Goal: {profile.get('goal', 'General Fitness')}
- Experience: {profile.get('experience', 'Beginner')}
- Age: {profile.get('age', 'Unknown')}
- Weight: {profile.get('weight', 'Unknown')} kg
- Height: {profile.get('height', 'Unknown')} cm
- Gender: {profile.get('gender', 'Unknown')}
- Diet: {profile.get('dietary_preference', 'Any')}
- Allergies: {_safe_join(profile.get('allergies', ['None']))}
- Body Issues/Injuries: {_safe_join(profile.get('body_issues', ['None']))}
- Equipment: {_safe_join(profile.get('equipment', ['None']))}

SAFETY:
- NEVER prescribe exercises that could aggravate their listed injuries
- For injury treatment, ALWAYS advise consulting a doctor/physiotherapist
- Don't provide medical diagnoses"""


def _trim_history(history: list) -> list:
    """Trim conversation history to prevent token overflow."""
    if not history or not isinstance(history, list):
        return []
    return history[-MAX_HISTORY_MESSAGES:]


def get_chatbot_response(user_message: str, profile: Dict[str, Any], chat_history: list = None) -> str:
    """
    Generate an AI response to a user's fitness question.
    Falls back to smart offline responses when AI is unavailable.
    """
    model = _get_model()

    # Sanitize input
    if not user_message or not user_message.strip():
        return "I didn't catch that. Could you ask your question again? 🤔"

    if len(user_message) > MAX_MESSAGE_LENGTH:
        user_message = user_message[:MAX_MESSAGE_LENGTH] + "..."

    # If model is unavailable, use smart offline fallback
    if not model:
        return _build_contextual_offline_response(user_message, profile, chat_history)

    # Build conversation context from history
    history_context = ""
    if chat_history:
        trimmed = _trim_history(chat_history)
        history_lines = []
        for msg in trimmed:
            role = _map_role(msg.get('role'))
            text = _extract_message_text(msg)
            if len(text) > 500:
                text = text[:500] + "..."
            if text:
                history_lines.append(f"{role}:\n{text}")

        if history_lines:
            history_context = "=== Start History ===\n\n" + "\n\n".join(history_lines) + "\n\n=== End History ==="

    system_prompt = _build_system_prompt(profile)

    full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{history_context if history_context else "(New conversation)"}

USER MESSAGE: {user_message}

RESPONSE (be concise, helpful, and motivating):"""

    try:
        def _call():
            return model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1024,
                    temperature=0.7,
                    top_p=0.9,
                )
            )
        # ARCH-7: circuit breaker guards chatbot calls
        response = gemini_cb.call(_call)

        reply = response.text.strip()
        if not reply:
            return "Hmm, I couldn't formulate a response. Could you rephrase your question? 🤔"
        return reply

    except CircuitBreakerOpen as cbo:
        print(f"[Gemini] {cbo}")
        return _build_contextual_offline_response(user_message, profile, chat_history)
    except Exception as e:
        error_str = str(e).lower()
        print(f"[Gemini] Chatbot error: {e}")

        # If quota exhausted, use fallback
        if '429' in error_str or 'quota' in error_str or 'exhausted' in error_str or 'rate' in error_str:
            return _build_contextual_offline_response(user_message, profile, chat_history)
        elif 'safety' in error_str or 'blocked' in error_str:
            return "I can't respond to that particular question. Let's keep our chat focused on fitness and nutrition! 💪"
        elif 'invalid' in error_str and 'key' in error_str:
            return _build_contextual_offline_response(user_message, profile, chat_history)
        else:
            return _build_contextual_offline_response(user_message, profile, chat_history)

