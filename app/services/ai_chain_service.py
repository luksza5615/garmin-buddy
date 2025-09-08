from langchain_core.runnables import RunnableLambda, RunnableSequence
from app.services.db_service import get_last_activity
from app.services.llm_google_service import summarize_workout, plan_workouts

fetch = RunnableLambda(lambda _: get_last_activity())
summarize = RunnableLambda(summarize_workout)
plan = RunnableLambda(plan_workouts)

chain = fetch | summarize | plan

def run_chain():
    result = chain.invoke(None)

    return result

if __name__ == "__main__":
    run_chain()