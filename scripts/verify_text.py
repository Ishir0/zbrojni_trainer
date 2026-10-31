"""Independent layout-text comparison of every stem and answer against Poppler XML.
Ignores whitespace only (PDF runs and physical line wrapping); normalizes known
presentation ligatures using the source-specific CID repair manifest.
"""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parent.parent
repairs=json.loads((R/'sources/ligature-repairs.json').read_text())
pages=(R/'tmp/bank-layout.txt').read_text().split('\f');clean=[]
for i,page in enumerate(pages):
 if i==0:continue
 replacement=iter(repairs['pages'].get(str(i+1),[]))
 page=re.sub('�',lambda _:next(replacement),page)
 assert next(replacement,None) is None
 lines=[]
 for line in page.splitlines():
  text=line.strip()
  if not text or re.fullmatch(r'\d+',text):continue
  if re.match(r'^(I{1,3}|IV|V)\.\s',text):continue
  lines.append(text)
 clean.extend(lines)
text='\n'.join(clean).replace('ﬁ','fi').replace('ﬂ','fl')
blocks=re.split(r'(?m)^\s*(\d+)\.\s*',text)
questions=json.loads((R/'public/data/questions.json').read_text())['questions'];issues=[]
norm=lambda t:re.sub(r'\s+','',t)
for i in range(1,len(blocks),2):
 number=int(blocks[i]);body=blocks[i+1]
 parts=re.split(r'(?m)^\s*([ABCabc])\)\s*',body)
 q=questions[number-1]
 if norm(parts[0])!=norm(q['stem']):issues.append({'number':number,'field':'stem','layout':parts[0],'xml':q['stem']})
 options=[(parts[j].upper(),parts[j+1]) for j in range(1,len(parts),2)]
 for oid,txt in options:
  if norm(txt)!=norm(next(o['text'] for o in q['options'] if o['id']==oid)):issues.append({'number':number,'field':oid,'layout':txt,'xml':next(o['text'] for o in q['options'] if o['id']==oid)})
 if len(options)!=3:issues.append({'number':number,'field':'option count'})
(R/'sources/text-comparison-report.json').write_text(json.dumps({'method':'Independent pdftotext -layout vs geometry-aware pdftohtml XML; whitespace-insensitive exact comparison of all stems and options.','questionsCompared':(len(blocks)-1)//2,'issues':issues},ensure_ascii=False,indent=2)+'\n')
print('Questions compared:',(len(blocks)-1)//2,'differences:',len(issues))
for issue in issues[:10]:print(issue)
if issues:raise SystemExit(1)
