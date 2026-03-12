PLANET_IN_SIGN = {
    ("Sun", "Aries"):        "Strong willpower, natural leader, bold and courageous.",
    ("Sun", "Taurus"):       "Stable, determined, enjoys material comforts and security.",
    ("Sun", "Gemini"):       "Curious, communicative, adaptable and quick-witted.",
    ("Sun", "Cancer"):       "Deeply emotional, nurturing, strong family bonds.",
    ("Sun", "Leo"):          "Charismatic, confident, natural performer and leader.",
    ("Sun", "Virgo"):        "Analytical, detail-oriented, health-conscious and practical.",
    ("Sun", "Libra"):        "Diplomatic, charming, seeks harmony and balance.",
    ("Sun", "Scorpio"):      "Intense, perceptive, deeply transformative nature.",
    ("Sun", "Sagittarius"):  "Adventurous, philosophical, loves freedom and travel.",
    ("Sun", "Capricorn"):    "Disciplined, ambitious, strong sense of responsibility.",
    ("Sun", "Aquarius"):     "Innovative, humanitarian, independent thinker.",
    ("Sun", "Pisces"):       "Empathetic, intuitive, deeply spiritual and creative.",

    ("Moon", "Aries"):       "Emotionally impulsive, needs action to feel secure.",
    ("Moon", "Taurus"):      "Emotionally stable, craves comfort and routine.",
    ("Moon", "Gemini"):      "Emotionally curious, needs mental stimulation.",
    ("Moon", "Cancer"):      "Deeply nurturing, highly intuitive, emotionally sensitive.",
    ("Moon", "Leo"):         "Needs recognition and warmth, generous emotions.",
    ("Moon", "Virgo"):       "Emotionally reserved, finds comfort in order.",
    ("Moon", "Libra"):       "Needs harmony, dislikes emotional conflict.",
    ("Moon", "Scorpio"):     "Intense emotions, deep loyalty, fear of betrayal.",
    ("Moon", "Sagittarius"): "Needs freedom, optimistic and adventurous emotions.",
    ("Moon", "Capricorn"):   "Emotionally controlled, finds security in achievement.",
    ("Moon", "Aquarius"):    "Emotionally detached, values friendship and ideals.",
    ("Moon", "Pisces"):      "Dreamy, compassionate, absorbs others' emotions.",
}

PLANET_IN_HOUSE = {
    1:  "strongly shapes your personality and outward appearance.",
    2:  "influences your finances, values and material possessions.",
    3:  "affects communication, siblings and short travels.",
    4:  "shapes your home, family and emotional roots.",
    5:  "influences creativity, romance and children.",
    6:  "affects health, daily work and service to others.",
    7:  "shapes partnerships, marriage and open enemies.",
    8:  "influences transformation, shared resources and mysteries.",
    9:  "affects higher learning, philosophy and long journeys.",
    10: "shapes career, reputation and public image.",
    11: "influences friendships, goals and social causes.",
    12: "affects the subconscious, isolation and spiritual growth.",
}

def interpret_chart(planets: dict) -> dict:
    interpretations = {}

    for planet, data in planets.items():
        sign = data["sign"]
        house = data["house"]

        sign_meaning = PLANET_IN_SIGN.get(
            (planet, sign),
            f"{planet} in {sign} brings unique and personal energy."
        )

        house_meaning = PLANET_IN_HOUSE.get(
            house,
            "influences various areas of your life."
        )

        interpretations[planet] = {
            "sign": sign,
            "house": house,
            "reading": f"{planet} in {sign}: {sign_meaning} "
                       f"In house {house}, it {house_meaning}"
        }

    return interpretations