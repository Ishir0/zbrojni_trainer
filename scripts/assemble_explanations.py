"""Validate AI-authored drafts against immutable official keys and retained sources.
Citation existence checks do not certify that a source supports the interpretation.
"""
from pathlib import Path
import hashlib,json,re,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
normalize=lambda text:re.sub(r'\s+',' ',text).strip()
def assemble(partial=False):
 bank=json.loads((ROOT/'public/data/questions.json').read_text()); questions={q['id']:q for q in bank['questions']}
 index=json.loads((ROOT/'sources/passages.json').read_text()); docs={d['id']:d for d in index['documents']}
 texts={}
 for d in docs.values():
  for name in ['textFile','originalFile']:
   path=ROOT/d[name]
   if path.suffix=='.txt' and path.exists():texts[d[name]]=normalize(path.read_text())
 entries=[];errors=[];seen=set()
 for file in sorted((ROOT/'content/explanations').glob('questions-*.json')):
  try: records=json.loads(file.read_text())
  except (ValueError,OSError) as e:errors.append({'file':str(file.relative_to(ROOT)),'error':str(e)});continue
  if not isinstance(records,list):errors.append({'file':str(file),'error':'Expected array'});continue
  for item in records:
   issues=[]
   if not isinstance(item,dict):errors.append({'file':str(file),'error':'Entry is not an object'});continue
   qid=item.get('questionId');q=questions.get(qid)
   if not q:issues.append('Unknown question ID')
   if qid in seen:issues.append('Duplicate explanation')
   seen.add(qid)
   if q and item.get('correctOptionId')!=q['correctOptionId']:issues.append('Official key mismatch')
   if item.get('datasetVersion')!=bank['version']:issues.append('Dataset version mismatch')
   if item.get('model')!='gpt-6-luna':issues.append('Unexpected drafting model')
   status=item.get('status')
   basis=item.get('evidenceBasis','source-grounded')
   if basis not in ['source-grounded','official-answer']:issues.append('Invalid evidence basis')
   if status not in ['ai-draft','needs-source']:issues.append('Invalid status; AI drafts cannot self-certify review')
   for field in ['concise','simpler','decisiveDetail']:
    if not isinstance(item.get(field),str):issues.append('Invalid text field '+field)
   reasons=item.get('optionReasoning',{})
   if not isinstance(reasons,dict) or set(reasons)!=set('ABC') or not all(isinstance(v,str) for v in reasons.values()):issues.append('Invalid per-option reasoning')
   if not isinstance(item.get('issues'),list) or not all(isinstance(x,str) for x in item.get('issues',[])):issues.append('Invalid issue list')
   citations=item.get('sources',[])
   if not isinstance(citations,list):issues.append('Invalid source references');citations=[]
   supporting=0
   for c in citations:
    if not isinstance(c,dict):issues.append('Invalid citation');continue
    doc=docs.get(c.get('sourceId'))
    if c.get('evidenceType')=='web-reference':
     url=c.get('url',''); sid='s-'+hashlib.sha256(url.encode()).hexdigest()[:12]
     if not q or q['number']<649 or not url.startswith('https://') or c.get('sourceId')!=sid or not c.get('title') or not c.get('locator') or c.get('quote')!='':
      issues.append('Invalid general web reference');continue
     if not doc:
      doc={'id':sid,'title':c['title'],'url':url,'textSha256':'','role':'supporting-source'};docs[sid]=doc
     supporting+=1;continue
    if not doc:issues.append('Unknown citation source');continue
    if c.get('url')!=doc['url']:issues.append('Citation URL does not match retained source')
    if c.get('file') not in [doc['textFile'],doc['originalFile']]:issues.append('Citation file does not match retained source')
    quote=c.get('quote');locator=c.get('locator')
    if not isinstance(locator,str) or not locator.strip():issues.append('Missing citation locator')
    if not isinstance(quote,str) or len(quote.strip())<15:issues.append('Missing substantive exact quote');continue
    if '�' in quote:issues.append('Citation contains damaged Unicode')
    # A citation may point to the original PDF while quoting its extracted text.
    sourceText=texts.get(c.get('file')) or texts.get(doc['textFile'],'')
    if normalize(quote) not in sourceText:issues.append('Citation quote not found verbatim in retained source')
    if doc['role']=='supporting-source':supporting+=1
   if status=='ai-draft':
    # These patterns identify answer-restatement filler, not explanatory reasoning.
    prose=' '.join(str(item.get(k,'')) for k in ['concise','simpler'])+' '+ ' '.join(str(v) for v in reasons.values())
    if any(phrase in prose for phrase in ['Otázka míří na ', 'mění rozsah nebo přidává/ubírá podmínku', 'ostatní možnosti ji posouvají']):issues.append('Generic answer-restatement template is not an explanation')
    if not isinstance(item.get('concise'),str) or len(item['concise'].strip())<35:issues.append('Draft lacks substantive explanation')
    if not isinstance(reasons,dict) or any(len(str(reasons.get(k,'')).strip())<10 for k in 'ABC'):issues.append('Draft lacks specific reasoning for every choice')
    if supporting==0 and basis!='official-answer':issues.append('Draft requires supporting evidence or an explicit official-answer basis')
    if item.get('issues'):issues.append('Unresolved evidence issues must remain blocked, not publish as draft')
    for oid,reason in reasons.items():
     marker=re.match(r'^([ABC]):',reason.strip())
     if marker and marker[1]!=oid:issues.append('Per-option reasoning label is mapped to a different option')
     if q and oid!=q['correctOptionId'] and re.match(r'^(?:[ABC]:\s*)?(?:Správně|Správná|Ano\b)',reason,re.I):issues.append('Wrong-choice reasoning appears to identify it as correct; requires review')
    for field in ['concise','simpler','decisiveDetail']:
     if '�' in str(item.get(field,'')):issues.append('Damaged Unicode in explanation')
   if status=='needs-source':
    if item.get('concise') or item.get('simpler') or item.get('decisiveDetail') or any(reasons.values()):issues.append('Blocked item must not publish unsupported explanatory prose')
    if not item.get('issues'):issues.append('Blocked item requires a specific issue')
   if issues:errors.append({'file':str(file.relative_to(ROOT)),'questionId':qid,'errors':issues});continue
   allowed=['questionId','datasetVersion','correctOptionId','status','concise','simpler','optionReasoning','decisiveDetail','sources','issues','model']
   entry={k:item[k] for k in allowed};entry['evidenceBasis']=basis;entries.append(entry)
 missing=sorted(set(questions)-seen,key=lambda x:int(x.split('-')[1]))
 report={'schemaVersion':1,'datasetVersion':bank['version'],'checkedAt':datetime.now(timezone.utc).isoformat(),'totalQuestions':len(questions),'validEntries':len(entries),'drafts':sum(e['status']=='ai-draft' for e in entries),'answerBasedDrafts':sum(e['status']=='ai-draft' and e['evidenceBasis']=='official-answer' for e in entries),'needsSource':sum(e['status']=='needs-source' for e in entries),'missing':missing,'errors':errors,'limits':'Checks validate structure, fixed official keys and retained quotations where supplied. Drafts may explicitly derive from the official answer; technical/first-aid drafts may use general web references. Checks do not certify legal/medical accuracy or entailment.'}
 (ROOT/'sources/explanation-validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ['missing','errors']},ensure_ascii=False));print('Missing:',len(missing),'Errors:',len(errors))
 if errors or (missing and not partial):
  for e in errors[:15]:print(json.dumps(e,ensure_ascii=False))
  if not partial:return False
 output={'schemaVersion':1,'datasetVersion':bank['version'],'generatedAt':report['checkedAt'],'model':'gpt-6-luna','reviewStatus':'ai-draft','coverage':{'total':len(questions),'drafts':report['drafts'],'needsSource':report['needsSource'],'missing':len(questions)-len(entries)},'sources':[{k:d[k] for k in ['id','title','url','textSha256']} for d in docs.values()],'explanations':sorted(entries,key=lambda e:int(e['questionId'].split('-')[1]))}
 (ROOT/'public/data/explanations.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');return not errors
if __name__=='__main__':raise SystemExit(0 if assemble('--partial' in sys.argv) else 1)
