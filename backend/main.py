from chart_engine import compute_birth_chart
from interpreter import interpret_chart
import sys

def get_input(prompt, example=""):
    if example:
        print(f"  Example: {example}")
    value = input(f"  {prompt}: ").strip()
    if not value:
        print("  This field cannot be empty. Please try again.")
        return get_input(prompt, example)
    return value

def get_system_choice() -> str:
    print("\n  Which zodiac system would you like to use?")
    print("  [1] Vedic / Sidereal  (Jyotish — Indian astrology)")
    print("  [2] Western / Tropical (Co-Star, most horoscope sites)")
    choice = input("  Enter 1 or 2: ").strip()
    if choice == "1":
        return "vedic"
    elif choice == "2":
        return "western"
    else:
        print("  Invalid choice. Please enter 1 or 2.")
        return get_system_choice()

def print_divider():
    print("\n" + "=" * 55)

def run():
    print_divider()
    print("       JYOTISH AI — Personal Astrology Assistant")
    print_divider()
    print("\n  Enter your birth details to generate your chart.\n")

    try:
        name   = get_input("Your name",                  "Arjun Sharma")
        dob    = get_input("Date of birth (YYYY-MM-DD)", "1995-08-15")
        tob    = get_input("Time of birth (HH:MM 24hr)", "07:30")
        place  = get_input("Place of birth",             "Mumbai, India")
        system = get_system_choice()

        print("\n  Calculating your birth chart, please wait...")

        chart           = compute_birth_chart(name, dob, tob, place, system)
        interpretations = interpret_chart(chart["planets"])

        system_label = "Vedic / Sidereal (Lahiri)" if system == "vedic" else "Western / Tropical"

        print_divider()
        print(f"  BIRTH CHART FOR: {name.upper()}")
        print(f"  Born : {dob} at {tob} | {place}")
        print(f"  System : {system_label}")
        if system == "vedic":
            print(f"  Ayanamsa : {chart['ayanamsa']}°  (Lahiri)")
        print_divider()

        # Planet positions table — show both signs side by side
        print("\n  PLANET POSITIONS\n")
        print(f"  {'Planet':<12} {'Vedic Sign':<16} {'Western Sign':<16} {'House'}")
        print(f"  {'-'*12} {'-'*16} {'-'*16} {'-'*5}")
        for planet, data in chart["planets"].items():
            vedic   = data["vedic_sign"]
            western = data["western_sign"]
            house   = data["house"]
            # Mark the active system with an arrow
            v_mark = " <" if system == "vedic"   else ""
            w_mark = " <" if system == "western" else ""
            print(f"  {planet:<12} {vedic+v_mark:<16} {western+w_mark:<16} {house}")

        print_divider()
        print("\n  YOUR PERSONALIZED READINGS\n")
        for planet, data in interpretations.items():
            print(f"  {data['reading']}\n")

        print_divider()
        print("\n  CAREER SUGGESTION\n")
        sun_sign  = chart["planets"]["Sun"]["sign"]
        moon_sign = chart["planets"]["Moon"]["sign"]
        print(f"  With Sun in {sun_sign} and Moon in {moon_sign},")
        print(f"  you may thrive in careers that blend {sun_sign} energy")
        print(f"  with {moon_sign} emotional intelligence.")
        print(f"  Fields like leadership, research, or creative roles may suit you.\n")

        print_divider()

    except ValueError as e:
        print(f"\n  Error: {e}")
        print("  Check your date (YYYY-MM-DD) and time (HH:MM) format.\n")
    except Exception as e:
        print(f"\n  Something went wrong: {e}")
        print("  Make sure your internet is on (needed for location lookup).\n")

    again = input("\n  Generate another chart? (yes / no): ").strip().lower()
    if again in ("yes", "y"):
        print("\n")
        run()
    else:
        print("\n  Goodbye!\n")
        sys.exit(0)

if __name__ == "__main__":
    run()