"""Extract official text and answer markers with Poppler; never infer answer keys.
Requires pdftohtml / pdftotext. Whitespace and PDF line breaks are normalized.
"""
import xml.etree.ElementTree as ET
import subprocess, re, json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT/'sources/official-questions.pdf'
TMP = ROOT/'tmp'
TMP.mkdir(exist_ok=True)
subprocess.run(['pdftohtml','-q','-xml','-hidden','-fmt','png',str(PDF),str(TMP/'bank.xml')], check=True)
subprocess.run(['pdftotext','-layout',str(PDF),str(TMP/'bank-layout.txt')],check=True)
root=ET.parse(TMP/'bank.xml').getroot()
repairs=json.loads((ROOT/'sources/ligature-repairs.json').read_text())
assert repairs['sourceSha256']==hashlib.sha256(PDF.read_bytes()).hexdigest(), 'Ligature repairs are source-specific'
for page in root.findall('page'):
 replacements=iter(repairs['pages'].get(page.get('number'),[]))
 for element in page.findall('text'):
  for node in element.iter():
   if node.text: node.text=re.sub('�',lambda _:next(replacements),node.text)
   if node.tail: node.tail=re.sub('�',lambda _:next(replacements),node.tail)
 assert next(replacements,None) is None
# Expand presentation ligatures only; preserve wording, accents and punctuation.
for el in root.iter():
 if el.text: el.text=el.text.replace('ﬁ','fi').replace('ﬂ','fl')
 if el.tail: el.tail=el.tail.replace('ﬁ','fi').replace('ﬂ','fl')
topics=['Zákon o zbraních a střelivu','Prováděcí právní předpisy','Jiné právní předpisy','Nauka o zbraních a střelivu','Zdravotnické minimum']
questions=[]; current=None; option=None; issues=[]
for page in root.findall('page'):
 p=int(page.get('number'))
 if p==1: continue
 topic=topics[0 if p<132 else 1 if p<148 else 2 if p<158 else 3 if p<210 else 4]
 # Poppler can split runs at the same baseline by one pixel. Recombine geometrically.
 rows=[]
 for el in page.findall('text'):
  y=int(el.get('top')); x=int(el.get('left')); s=''.join(el.itertext())
  if not s.strip() or y>1145: continue
  row=next((r for r in rows if abs(r['y']-y)<=2),None)
  if row is None: row={'y':y,'runs':[]};rows.append(row)
  row['runs'].append((x,el,s))
 events=[(r['y'],'text',r) for r in rows]+[(int(el.get('top')),'image',el) for el in page.findall('image')]
 for y,kind,item in sorted(events,key=lambda e:e[0]):
  if kind=='image':
   if current:
    src=Path(item.get('src')); src=src if src.is_absolute() else ROOT/src
    target=ROOT/'public/data/images'/src.name
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
    current['images'].append({'src':'/data/images/'+src.name,'page':p,'optionId':option['id'] if option else None})
   continue
  runs=sorted(item['runs']); text=''; end=None; italic=0
  for x,el,s in runs:
   if end is not None and x-end>2 and text and not text.endswith(' ') and not s.startswith(' '): text+=' '
   text+=s;end=x+int(el.get('width'))
   if el.find('.//i') is not None: italic+=sum(c.isalnum() for c in s)
  text=re.sub(r'\s+',' ',text).strip()
  if not text or re.match(r'^(I{1,3}|IV|V)\.',text):continue
  match=re.match(r'^(\d+)\.\s*(.*)',text)
  if match and int(match[1])==len(questions)+1:
   current={'id':'q-'+match[1],'number':int(match[1]),'stem':match[2],'options':[],'correctOptionId':None,'topic':topic,'page':p,'images':[],'verification':'format-checked','explanationStatus':'pending','datasetVersion':'mv-2026-'+hashlib.sha256(PDF.read_bytes()).hexdigest()[:12]}
   questions.append(current);option=None;continue
  if not current:continue
  match=re.match(r'^([ABCabc])\)\s*(.*)',text)
  if match:
   option={'id':match[1].upper(),'text':match[2],'_italic':italic};current['options'].append(option)
  elif option: option['text']+=' '+text;option['_italic']+=italic
  else: current['stem']+=' '+text
for q in questions:
 q['stem']=q['stem'].strip()
 for o in q['options']:o['text']=o['text'].strip()
 if q['number'] in [1,2,3,4,562,563,564,610,611,612,613,649,650,800,801,802,803,835,836,837]:q['verification']='visually-checked'
 keys=[o['id'] for o in q['options'] if o['_italic']>0]
 if q['number'] in [716,717]:
  # These two answers are grey-highlighted without italics in the original.
  # Visually verified on PDF pp. 190-191; no legal inference.
  keys=[{716:'A',717:'B'}[q['number']]]
  q['verification']='visually-checked'
 if len(keys)!=1:issues.append({'number':q['number'],'error':'ambiguous italic key','keys':keys})
 else:q['correctOptionId']=keys[0]
 if [o['id'] for o in q['options']]!=['A','B','C']:issues.append({'number':q['number'],'error':'invalid options'})
 for o in q['options']:del o['_italic']
 if not q['stem']:issues.append({'number':q['number'],'error':'empty stem'})
 if any(re.search(r'\b\d{1,3}\. ',o['text']) for o in q['options']):pass # numeric legal references are valid
# A second extraction verifies question numbering independently of the XML parser.
layout=(TMP/'bank-layout.txt').read_text()
layout_numbers=[int(n) for n in re.findall(r'^\s*(\d+)\.\s',layout,re.M)]
expected=list(range(1,len(questions)+1))
if layout_numbers!=expected:issues.append({'error':'independent layout numbering differs','count':len(layout_numbers)})
if len(questions)!=837:issues.append({'error':'source snapshot expected 837 questions','actual':len(questions)})
report={'manualKeyChecks': {'716': 'A, grey-highlighted on page 190', '717': 'B, grey-highlighted on page 191'}, 'source':'official-questions.pdf','sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'extractedAt':datetime.now(timezone.utc).isoformat(),'count':len(questions),'topicCounts':{t:sum(q['topic']==t for q in questions) for t in topics},'illustratedQuestions':sum(bool(q['images']) for q in questions),'method':'Poppler XML preserves italic official key markers; exactly one marked option per question; independent layout text numbering cross-check. Not a full manual editorial audit.','issues':issues,'explanationReview':'All pending; no AI-certified legal/medical explanations.'}
(ROOT/'sources/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if issues:
 print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit('Extraction failed: do not publish dataset')
out=ROOT/'public/data/questions.json'
out.write_text(json.dumps({'version':questions[0]['datasetVersion'],'sourceUrl':'https://mv.gov.cz/soubor/mv-soubor-testovych-otazek-pro-teoretickou-cast-zkousky-odborne-zpusobilosti-a-komisionalni-zkousku.aspx','sourceSha256':report['sha256'],'topics':topics,'questions':questions},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
