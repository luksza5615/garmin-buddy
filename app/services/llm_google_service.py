import os
from google import genai
from dotenv import load_dotenv
from app.services.db_service  import get_last_activity

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

def generate_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text

def generate_response_based_on_file():
    file = client.files.upload(file="C:/Users/LSzata/OneDrive - DXC Production/Projects/garmin/garmin-buddy/tests/app_test/services/resources/test.txt")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=['Analyze athleete fitness based on the file content', file]
    )

    return response.text

def get_workout_data():
    activity = get_last_activity()
    activity_details = activity.iloc[0].to_dict()
    print(activity_details)

    return activity_details


workout_example = {
    "avg_heart_rate": 150,
    "avg_pace": "5:30"
}

def stringify_workout(workout):
    return {
        f"Average heart rate: {workout["avg_heart_rate"]}"
    }


def build_prompt(workout_details):
    return (f"""
            1. Analyze below trainig in terms of:
             1.1. Intensity
             1.2. Effectiveness
             1.3. Athletee performance
             1.4. Recommendations for the future 
             

            Workout details: 
            Sport: {workout_details['subsport']}
            Distance: {workout_details['distance_in_km']} km
            Duration: {workout_details['elapsed_duration']}
            Grade adjusted average pace: {workout_details['grade_adjusted_avg_pace_min_per_km']} min/km
            Average heart rate: {workout_details['avg_heart_rate']}
            Calories burnt: {workout_details['calories_burnt']}
            Ascent: {workout_details['total_ascent_in_meters']} m
            Descent: {workout_details['total_descent_in_meters']} m

            # 2. Compare workout to my other past workouts
            # {context}
            """)

def summarize_workout(activity_details):
    prompt = build_prompt(activity_details)
    response = generate_response(prompt)
    return response

def plan_workouts(workout_summary):
    prompt = "Prepare plan for upcoming microcycle of 7 days"
    response = generate_response(prompt)
    print(response)
    return response


if __name__ == "__main__":
    workout = stringify_workout(workout_example)
    print(workout)
