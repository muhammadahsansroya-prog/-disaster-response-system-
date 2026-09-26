import uuid
import requests
from .secrets import HF_API_TOKEN

RESPONSES = [
    (["submit", "help request", "how do i ask", "need help", "apply", "application",
      "register a request", "raise a request", "how can i request", "i need"],
     "To submit a help request: go to the 'Submit Request' page, allow location access, "
     "select the type of disaster or need (flood, medical, food, shelter), choose an "
     "urgency level, and click Submit. Your request is instantly logged and reviewed by our team."),

    (["status", "track", "where is my request", "pending", "update on my request",
      "check my request", "progress"],
     "Your request moves through these stages: Pending -> Matched -> Dispatched -> Completed. "
     "An admin reviews it and assigns the nearest available resource automatically."),

    (["urgency", "critical", "priority", "how urgent", "level 1"],
     "Urgency levels are Low, Medium, High, and Critical. Critical requests are always handled first by our dispatch system."),

    (["resource", "boat", "medical", "food", "shelter", "water", "helicopter", "supplies"],
     "We coordinate multiple resource types: Food, Water, Medical Teams, Rescue Boats, "
     "Shelters, and Aerial Air-Drop units. Each is matched to the nearest pending request using GPS."),

    (["responder", "login", "team", "field unit", "taskforce"],
     "Responders and field units log in through the Command Login page to view resources and dispatches assigned to them."),

    (["contact", "emergency number", "call", "phone number", "helpline"],
     "For life-threatening emergencies, always call your local emergency services first "
     "(Rescue 1122 in Pakistan). This portal coordinates resource dispatch alongside official emergency services."),

    (["admin", "dashboard", "command", "who manages"],
     "Administrators use the Command Dashboard to view all pending requests, monitor available resources, "
     "and dispatch the nearest match with one click."),

    (["disaster", "flood", "earthquake", "fire", "collapse", "type of emergency"],
     "This system currently supports flash flood evacuation, medical emergencies, food and water supply requests, "
     "and structural collapse rescue. Select the matching category when you submit your request."),

    (["hello", "hi", "hey", "assalam", "salam"],
     "Hello! I'm the Relief Assistant. Ask me about submitting a request, tracking status, urgency levels, or available resources."),
]

DEFAULT_RESPONSE = ("I can help with: submitting a request, tracking status, urgency levels, "
                     "resource types, responder login, or emergency contacts.")

# Hugging Face "Inference Providers" router (replaces the old api-inference.huggingface.co)
HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
HF_MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

SYSTEM_CONTEXT = (
    "You are the Relief Assistant for a disaster response coordination system in Pakistan. "
    "You help citizens understand how to submit help requests, track status, urgency levels, "
    "available resources (food, water, medical, rescue boats, shelter), and responder login. "
    "Keep answers short, factual, and calm. If asked about life-threatening emergencies, "
    "always tell the person to call Rescue 1122 first. Do not make up features that do not exist."
)


def get_rule_based_response(message):
    text = message.lower()
    for keywords, response in RESPONSES:
        if any(k in text for k in keywords):
            return response
    return None


def get_ai_response(message):
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": HF_MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_CONTEXT},
                {"role": "user", "content": message},
            ],
            "max_tokens": 200,
            "temperature": 0.4,
        }
        res = requests.post(HF_ROUTER_URL, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"].strip()
        return None
    except Exception:
        return None


def get_bot_response(message):
    rule_answer = get_rule_based_response(message)
    if rule_answer:
        return rule_answer

    ai_answer = get_ai_response(message)
    if ai_answer:
        return ai_answer

    return DEFAULT_RESPONSE


def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or str(uuid.uuid4())