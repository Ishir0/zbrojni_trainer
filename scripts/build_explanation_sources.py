"""Prepare locally searchable, versioned passages for AI explanation drafting.
Original source bytes stay unchanged. No model calls or external requests.
"""
from pathlib import Path
import json,hashlib,re,subprocess
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/'sources/source-manifest.json').read_text())
docs=[];passages=[]
for entry in manifest:
 sid='s-'+hashlib.sha256(entry['url'].encode()).hexdigest()[:12]
 original=ROOT/entry['file'];pages=None
 if entry.get('renderedText'):
  textpath=ROOT/entry['renderedText']['file'];text=textpath.read_text()
 elif entry['status']=='downloaded-pdf':
  textpath=ROOT/'sources/text'/f'{sid}.txt';textpath.parent.mkdir(exist_ok=True,parents=True)
  subprocess.run(['pdftotext','-layout',str(original),str(textpath)],check=True)
  text=textpath.read_text();pages=text.split('\f')
 else:continue
 role='question-bank' if 'mv-soubor-testovych-otazek' in entry['url'] else 'supporting-source'
 doc={'id':sid,'title':entry['title'],'url':entry['url'],'originalFile':entry['file'],'textFile':str(textpath.relative_to(ROOT)),'sha256':hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else entry['renderedText']['sha256'],'textSha256':hashlib.sha256(text.encode()).hexdigest(),'role':role}
 docs.append(doc)
 if pages is not None:
  for i,page in enumerate(pages,1):
   if len(page.strip())<20:continue
   passages.append({'id':f'{sid}:p{i}','sourceId':sid,'file':doc['textFile'],'locator':f'strana {i}','page':i,'text':page.strip()})
 else:
  # A clause may have a heading immediately preceding its section marker.
  chunks=re.split(r'(?m)^(?=(?:§\s*\d+[a-z]?|Čl\.\s*\d+)\s*$)',text)
  for i,chunk in enumerate(chunks):
   if len(chunk.strip())<20:continue
   first=chunk.strip().splitlines()[0]
   locator=first if re.match(r'^(?:§|Čl\.)',first) else 'úvod a údaje o znění'
   passages.append({'id':f'{sid}:s{i}','sourceId':sid,'file':doc['textFile'],'locator':locator,'text':chunk.strip()})
output={'schemaVersion':1,'documents':docs,'passages':passages,'notes':['Machine-extracted text; source interpretation and effective-date applicability require review.','PDF passages keep original page boundaries. PDF typography/diagrams may require visual inspection.','Do not use the official answer bank alone as evidence for an explanatory legal/medical rule.']}
(ROOT/'sources/passages.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'documents':len(docs),'passages':len(passages),'characters':sum(len(p['text']) for p in passages)}))
