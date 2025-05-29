import subprocess
from app.services.db_service import get_top_activities


def summarize_training(df):

    df_text = df.to_string(index=False)

    print(df_text)

    prompt = f"""
    You are a sports training assistant. Summarize runner's training from the training log.
    Focus on volume, intensity, variation, and whether it suggests improvement or fatigue.
    
    Training log:
    {df_text}
    
    """
    print(prompt)
    response = subprocess.run(
        ["C:\\Users\\SzataLukasz\\AppData\\Local\\Programs\\Ollama\\ollama.exe", "run", "mistral", prompt], capture_output=True, text=True)

    return response.stdout


def test_ai():

    prompt = """
    How are you? Be concise in your answer
    """
    print("method being executed")
    response = subprocess.run(
        ["C:\\Users\\SzataLukasz\\AppData\\Local\\Programs\\Ollama\\ollama.exe", "run", "mistral", prompt], capture_output=True, text=True)

    return response.stdout


if __name__ == "__main__":
    activities = get_top_activities()
    print(summarize_training(activities))
