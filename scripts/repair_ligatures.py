"""Recover malformed ToUnicode ligatures from their distinct original PDF CIDs.
No visual or official wording edits; source remains byte-for-byte unchanged.
Requires pypdf. Outputs mapping for Poppler extraction only.
"""
from pathlib import Path
from pypdf import PdfReader
import xml.etree.ElementTree as ET
import re,json,hashlib
root=Path(__file__).resolve().parent.parent
pdf=root/'sources/official-questions.pdf'
r=PdfReader(pdf); seen=set()
# Font's three CIDs map to U+FFFD; their embedded shapes/text contexts were inspected.
# Preserve CID identity temporarily with private-use Unicode markers.
for p in r.pages:
 for f in p['/Resources']['/Font'].values():
  f=f.get_object()
  if str(f.get('/BaseFont'))!='/UGCMUP+Calibri' or id(f) in seen:continue
  seen.add(id(f));s=f['/ToUnicode'].get_data().decode()
  for cid,marker in [('014C','E000'),('019F','E001'),('01A1','E002')]:s=s.replace(f'<{cid}> <FFFD>',f'<{cid}> <{marker}>')
  f['/ToUnicode'].set_data(s.encode())
xml=ET.parse(root/'tmp/bank.xml').getroot();out={}
for i,page in enumerate(xml.findall('page')):
 text=r.pages[i].extract_text()
 raw=[m.group() for m in re.finditer('[\ue000-\ue002]',text)]
 damaged=sum(''.join(e.itertext()).count('�') for e in page.findall('text'))
 if len(raw)!=damaged:raise ValueError(f'Page {i+1}: ligature count mismatch')
 # Independently require same sequence of surrounding words in both extractions.
 a=re.findall(r'\w*[\ue000-\ue002]\w*',text)
 b=re.findall(r'\w*�\w*',''.join(''.join(e.itertext()) for e in page.findall('text')))
 normalized=[re.sub('[\ue000-\ue002]','�',x) for x in a]
 if len(normalized)!=len(b) or any(not (x.startswith(y) or y.startswith(x)) for x,y in zip(normalized,b)):raise ValueError(f'Page {i+1}: ligature context/order differs: {normalized} vs {b}')
 if raw:out[str(i+1)]=[{'\ue000':'ft','\ue001':'ti','\ue002':'tí'}[m] for m in raw]
(root/'sources/ligature-repairs.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'method':'Distinct original glyph CIDs 014C=ft, 019F=ti, 01A1=tí in UGCMUP+Calibri; independently checked ordered word contexts against Poppler XML.','pages':out},indent=2,ensure_ascii=False)+'\n')
print('Recovered',sum(len(v) for v in out.values()),'ligatures on',len(out),'pages')
