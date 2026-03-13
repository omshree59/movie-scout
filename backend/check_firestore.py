import sys
sys.path.insert(0, '.')
from app.core.firebase import get_db

db = get_db()
all_docs = list(db.collection('dramas').stream())
total = len(all_docs)
print(f"Total dramas in Firestore: {total}")
for d in all_docs[:5]:
    data = d.to_dict()
    print(f"  - {data.get('title','?')} ({data.get('year','?')}) pop={data.get('tmdb_popularity',0):.1f}")
