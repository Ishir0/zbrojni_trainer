import type {Dataset,Explanation,ExplanationPack,Question} from './types';
export function explanationFor(pack:ExplanationPack|null,q:Question):Explanation|undefined {
 if(!pack||pack.datasetVersion!==q.datasetVersion)return;
 const e=pack.explanations.find(e=>e.questionId===q.id);
 if(e?.datasetVersion!==q.datasetVersion||e.correctOptionId!==q.correctOptionId)return;
 if(e.status==='ai-draft'&&(!e.concise?.trim()||(!e.sources?.length&&e.evidenceBasis!=='official-answer')))return;
 return e;
}
export function readExplanationPack(raw:unknown,data:Dataset):ExplanationPack {
 if(!raw||typeof raw!=='object')throw Error('Invalid explanation data');
 const pack=raw as ExplanationPack;
 if(pack.schemaVersion!==1||pack.datasetVersion!==data.version||pack.model!=='gpt-6-luna'||pack.reviewStatus!=='ai-draft'||!Array.isArray(pack.explanations)||!Array.isArray(pack.sources)||!pack.coverage)throw Error('Incompatible explanation data');
 const ids=new Set<string>();const sourceIds=new Set(pack.sources.map(s=>s.id));
 for(const e of pack.explanations){
  const q=data.questions.find(q=>q.id===e.questionId);
  if(!q||ids.has(e.questionId)||e.datasetVersion!==q.datasetVersion||e.correctOptionId!==q.correctOptionId||!['ai-draft','needs-source'].includes(e.status)||e.model!=='gpt-6-luna'||!Array.isArray(e.sources)||!Array.isArray(e.issues)||!e.issues.every(s=>typeof s==='string')||!['concise','simpler','decisiveDetail'].every(k=>typeof e[k as keyof Explanation]==='string')||!e.optionReasoning||!['A','B','C'].every(k=>typeof e.optionReasoning[k as 'A'|'B'|'C']==='string'))throw Error('Invalid explanation record');
  if(e.evidenceBasis!==undefined&&!['source-grounded','official-answer'].includes(e.evidenceBasis))throw Error('Invalid explanation basis');
  for(const c of e.sources){const source=pack.sources.find(s=>s.id===c.sourceId);if(!sourceIds.has(c.sourceId)||!source||source.url!==c.url||!/^https:\/\//.test(c.url)||typeof c.quote!=='string'||typeof c.locator!=='string')throw Error('Invalid explanation source');}
  if(e.status==='ai-draft'&&(!e.concise.trim()||(!e.sources.length&&e.evidenceBasis!=='official-answer')))throw Error('Unsupported explanation');
  if(e.status==='needs-source'&&(e.concise||e.simpler||e.decisiveDetail||Object.values(e.optionReasoning).some(Boolean)||!e.issues.length))throw Error('Blocked explanation contains draft prose');
  ids.add(e.questionId);
 }
 return pack;
}
