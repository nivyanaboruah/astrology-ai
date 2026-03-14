from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from chart_engine import compute_birth_chart
from interpreter import interpret_chart

load_dotenv()

app = FastAPI(
    title="Jyotish AI API",
    description="AI-powered Vedic & Western astrology backend",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Models ───────────────────────────────────────────

class KundliRequest(BaseModel):
    name: str
    dob: str              # YYYY-MM-DD
    tob: str              # HH:MM
    place: str
    system: Optional[str] = "vedic"   # "vedic" or "western"

class ChatRequest(BaseModel):
    question: str
    name: Optional[str] = "User"
    sun_sign: Optional[str] = ""
    moon_sign: Optional[str] = ""
    system: Optional[str] = "vedic"

class CompatibilityRequest(BaseModel):
    sign1: str
    sign2: str

# ─── Routes ───────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Jyotish AI API is running!"}


@app.post("/kundli")
def generate_kundli(request: KundliRequest):
    try:
        chart = compute_birth_chart(
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            place=request.place,
            system=request.system
        )
        interpretations = interpret_chart(chart["planets"])

        # Attach readings to planet data
        for planet in chart["planets"]:
            if planet in interpretations:
                chart["planets"][planet]["reading"] = interpretations[planet]["reading"]

        return {
            "success": True,
            "chart": chart
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/horoscope/{sun_sign}")
def get_horoscope(sun_sign: str, system: str = "vedic"):
    horoscopes = {
        "Aries":       "Your energy is high today. Take initiative in professional matters. Avoid impulsive decisions after 3 PM.",
        "Taurus":      "Financial opportunities arise. Stay grounded and trust your instincts. A loved one needs your attention.",
        "Gemini":      "Communication is your strength today. Express your ideas clearly. Short travel may bring unexpected gains.",
        "Cancer":      "Emotional clarity comes to you. Focus on home and family. Avoid lending money today.",
        "Leo":         "Your charisma attracts attention. Use it wisely in career matters. Romance is favored in the evening.",
        "Virgo":       "Detail-oriented work brings rewards. Health improvements are possible. Avoid overthinking relationships.",
        "Libra":       "Balance is key today. Legal and partnership matters go smoothly. Artistic pursuits bring joy.",
        "Scorpio":     "Deep insights guide your decisions. Financial transformation is possible. Trust your intuition.",
        "Sagittarius": "Adventure calls. Higher learning and travel are favored. Be honest in all communications.",
        "Capricorn":   "Career ambitions are supported. Discipline brings rewards. Take care of your health today.",
        "Aquarius":    "Innovation and teamwork bring success. Social causes benefit from your involvement.",
        "Pisces":      "Spiritual insights are strong. Creative projects flourish. Avoid escapism and stay grounded.",
    }

    sign = sun_sign.capitalize()
    if sign not in horoscopes:
        raise HTTPException(status_code=400, detail=f"Unknown sun sign: {sun_sign}")

    return {
        "success":   True,
        "sun_sign":  sign,
        "system":    system,
        "horoscope": horoscopes[sign],
        "lucky_color":  get_lucky_color(sign),
        "lucky_number": get_lucky_number(sign),
        "lucky_day":    get_lucky_day(sign),
    }


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = generate_chat_response(
            question=request.question,
            name=request.name,
            sun_sign=request.sun_sign,
            moon_sign=request.moon_sign,
            system=request.system
        )
        return {
            "success": True,
            "answer":  answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compatibility")
def check_compatibility(request: CompatibilityRequest):
    score, description = get_compatibility(request.sign1, request.sign2)
    return {
        "success":     True,
        "sign1":       request.sign1,
        "sign2":       request.sign2,
        "score":       score,
        "description": description
    }


@app.get("/lucky/{sun_sign}")
def get_lucky_days(sun_sign: str):
    sign = sun_sign.capitalize()
    days = generate_lucky_days(sign)
    return {
        "success":  True,
        "sun_sign": sign,
        "days":     days
    }


# ─── Helper Functions ─────────────────────────────────────────

def get_lucky_color(sign: str) -> str:
    colors = {
        "Aries": "Red", "Taurus": "Green", "Gemini": "Yellow",
        "Cancer": "Silver", "Leo": "Gold", "Virgo": "Navy Blue",
        "Libra": "Pink", "Scorpio": "Maroon", "Sagittarius": "Purple",
        "Capricorn": "Brown", "Aquarius": "Electric Blue", "Pisces": "Sea Green"
    }
    return colors.get(sign, "White")

def get_lucky_number(sign: str) -> int:
    numbers = {
        "Aries": 9, "Taurus": 6, "Gemini": 5, "Cancer": 2,
        "Leo": 1, "Virgo": 5, "Libra": 6, "Scorpio": 8,
        "Sagittarius": 3, "Capricorn": 8, "Aquarius": 4, "Pisces": 7
    }
    return numbers.get(sign, 1)

def get_lucky_day(sign: str) -> str:
    days = {
        "Aries": "Tuesday", "Taurus": "Friday", "Gemini": "Wednesday",
        "Cancer": "Monday", "Leo": "Sunday", "Virgo": "Wednesday",
        "Libra": "Friday", "Scorpio": "Tuesday", "Sagittarius": "Thursday",
        "Capricorn": "Saturday", "Aquarius": "Saturday", "Pisces": "Thursday"
    }
    return days.get(sign, "Monday")

def generate_lucky_days(sign: str) -> list:
    import datetime
    today = datetime.date.today()
    lucky_day = get_lucky_day(sign)
    day_map = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    target = day_map.get(lucky_day, 0)
    days = []
    for i in range(30):
        d = today + datetime.timedelta(days=i)
        rating = "Excellent" if d.weekday() == target else (
                 "Good" if d.weekday() in [(target+3)%7, (target-3)%7] else
                 "Neutral")
        days.append({
            "date":   d.strftime("%Y-%m-%d"),
            "day":    d.strftime("%A"),
            "rating": rating
        })
    return days

def get_compatibility(sign1: str, sign2: str) -> tuple:
    fire  = {"Aries", "Leo", "Sagittarius"}
    earth = {"Taurus", "Virgo", "Capricorn"}
    air   = {"Gemini", "Libra", "Aquarius"}
    water = {"Cancer", "Scorpio", "Pisces"}

    def element(s):
        s = s.capitalize()
        if s in fire:  return "Fire"
        if s in earth: return "Earth"
        if s in air:   return "Air"
        if s in water: return "Water"
        return "Unknown"

    e1, e2 = element(sign1), element(sign2)

    if e1 == e2:
        score, desc = 90, f"Both {sign1} and {sign2} share the {e1} element — natural harmony and deep understanding."
    elif {e1, e2} in [{"Fire","Air"}, {"Earth","Water"}]:
        score, desc = 80, f"{e1} and {e2} complement each other well — this pairing has strong potential."
    elif {e1, e2} in [{"Fire","Water"}, {"Earth","Air"}]:
        score, desc = 50, f"{e1} and {e2} can clash — but with effort, differences become strengths."
    else:
        score, desc = 65, f"{sign1} and {sign2} have a unique dynamic that requires mutual understanding."

    return score, desc

def generate_chat_response(question: str, name: str, sun_sign: str, moon_sign: str, system: str) -> str:
    system_label = "Vedic" if system == "vedic" else "Western"

    # Try OpenAI if key is set
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and api_key != "your_key_here":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = f"""You are Jyotish AI, an expert astrology assistant specializing in {system_label} astrology.
The user's name is {name}. Their Sun sign is {sun_sign} and Moon sign is {moon_sign} ({system_label} system).
Answer this question in 3-4 sentences in a warm, insightful tone: {question}"""
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Fallback rule-based responses
    q = question.lower()
    if any(w in q for w in ["career", "job", "work", "profession"]):
        return f"Based on your {sun_sign} Sun, you are well-suited for careers that require {sun_sign} traits like leadership and creativity. Your {moon_sign} Moon adds emotional intelligence to your professional approach."
    elif any(w in q for w in ["love", "relationship", "marriage", "partner"]):
        return f"Your {sun_sign} Sun brings passion and loyalty to relationships. With your {moon_sign} Moon, you seek emotional depth and genuine connection in a partner."
    elif any(w in q for w in ["health", "body", "fitness"]):
        return f"As a {sun_sign}, you should pay attention to the body areas ruled by your sign. Regular routine and mindful eating will support your overall wellbeing."
    elif any(w in q for w in ["money", "finance", "wealth", "rich"]):
        return f"Your {sun_sign} energy supports financial growth through bold decisions. Your {moon_sign} Moon advises saving and emotional stability before making big investments."
    else:
        return f"As a {sun_sign} Sun with a {moon_sign} Moon ({system_label} system), your path is shaped by the unique blend of these energies. Trust your intuition and the planetary guidance available to you right now."