from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent;m=json.loads((r/'manifest.json').read_text());data=[]
for part in m['parts']:
 b=(r/part['file']).read_bytes();assert len(b)==part['size'] and hashlib.sha256(b).hexdigest()==part['sha256'];data.append(b)
b=b''.join(data);assert len(b)==m['size'] and hashlib.sha256(b).hexdigest()==m['sha256'];(r/m['output']).write_bytes(b);print(m['output'])
