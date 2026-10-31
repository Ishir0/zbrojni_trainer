"""Download official supporting references with provenance. Run explicitly; no app runtime network calls."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
from datetime import datetime, timezone
import subprocess, hashlib, json
ROOT=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.current=None
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.current=[dict(attrs).get('href',''),'']
 def handle_data(self,text):
  if self.current:self.current[1]+=text
 def handle_endtag(self,tag):
  if tag=='a' and self.current:self.links.append(self.current);self.current=None
manifest=ROOT/'sources/source-manifest.json'
previous=json.loads(manifest.read_text()) if manifest.exists() else []
entries=[]
for file,base in [('ministry-full-index.html','https://mv.gov.cz/'),('first-aid-resources.html','https://www.cervenykriz.eu/')]:
 parser=Links();parser.feed((ROOT/'sources'/file).read_text())
 for href,title in parser.links:
  url=urljoin(base,href)
  # Ministry bank is already retained; separate ammunition permits are outside scope.
  if file.startswith('ministry'):
   if '/sb/2024/91' in url:break
   if not ('/soubor/' in url or '/sb/' in url):continue
  elif not '.pdf' in url or '2017' in url:continue
  if any(e['url']==url for e in entries):continue
  name=url.split('/')[-1].split('?')[0]
  if '/sb/' in url:name='law-'+url.split('/sb/')[1].split('?')[0].replace('/','-')+'.html'
  else:name=name.replace('.aspx','.pdf')
  entries.append({'title':title.strip(),'url':url,'file':'sources/references/'+name})
# Preserve additional legal references and already-rendered snapshots on recollection.
for old in previous:
 if '/law-' in old['file'] and not any(e['url']==old['url'] for e in entries):entries.append(old.copy())
for e in entries:
 old=next((old for old in previous if old['url']==e['url']),{})
 if old.get('renderedText'):e['renderedText']=old['renderedText']
 target=ROOT/e['file'];target.parent.mkdir(exist_ok=True,parents=True)
 if not target.exists():
  result=subprocess.run(['curl','-fL','--max-time','40','--silent','--show-error',e['url'],'-o',str(target)])
  if result.returncode:e['status']='download-failed';continue
 e['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 e['retrievedAt']=old.get('retrievedAt',datetime.now(timezone.utc).isoformat()) if old.get('sha256')==e['sha256'] else datetime.now(timezone.utc).isoformat()
 e['status']='downloaded-pdf' if target.read_bytes().startswith(b'%PDF') else 'html-requires-text-extraction'
 if e.get('renderedText'):e['status']='rendered-official-text'
 print(e['status'],e['title'][:70],flush=True)
(ROOT/'sources/source-manifest.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
public=[{'title':e['title'],'url':e['url'],'status':e['status']} for e in entries]
(ROOT/'public/data/sources.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
