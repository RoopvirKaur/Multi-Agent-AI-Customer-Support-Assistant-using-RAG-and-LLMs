import sys
from pathlib import Path
sys.path.insert(0, '.')
from backend.rag.pipeline import process_document

kb = Path('knowledge_base')
for fname in ['Pricing.pdf', 'ShippingPolicy.pdf', 'UserManual.pdf']:
    path = kb / fname
    chunks = process_document(path)
    print(f'\n== {fname}: {len(chunks)} chunks ==')
    for c in chunks[:3]:
        cid = c['chunk_id']
        preview = c['text'][:200].replace('\n', ' ')
        scopes = c['scopes']
        print(f'  [{cid}] scopes={scopes}')
        print(f'  {preview}')
        print()
