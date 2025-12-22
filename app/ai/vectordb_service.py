import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="trainings")

collection.add(
    ids=["id1", "id2","id3", "id4","id5", "id6", "id7"],
    documents=[
        "Distance: 20 km, Avg pace: 5:30 min/km, Avg heart rate: 148 bpm",
        "Distance: 6 km, Avg pace: 4:06 min/km, Avg heart rate: 165 bpm",
        "Distance: 4 km, Avg pace: 4:10 min/km, Avg heart rate: 162 bpm",
        "Distance: 7 km, Avg pace: 4:00 min/km, Avg heart rate: 171 bpm",
        "Distance: 26 km, Avg pace: 5:06 min/km, Avg heart rate: 153 bpm",
        "Distance: 36 km, Avg pace: 6:06 min/km, Avg heart rate: 140 bpm",
        "Distance: 22 km, Avg pace: 5:35 min/km, Avg heart rate: 144 bpm",
    ]
)

results = collection.query(
    query_texts=["Distance: 5 km, Avg pace: 3:55 min/km, Avg heart rate: 174 bpm"],
    n_results=2
)

print(results)