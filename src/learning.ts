import type {Attempt, Confidence, Dataset, OptionId, Progress, Question, QuestionState, Session} from './types';
export const DAY = 86_400_000;
export const INTERVALS = [1,3,7,14,30];
export function emptyProgress(version:string):Progress {return {schemaVersion:1,attempts:[],bookmarks:[],session:null,sessionSize:10,onboarded:false,datasetVersion:version};}
export function stateFor(question:Question, attempts:Attempt[]):QuestionState {
 const history=attempts.filter(a=>a.questionId===question.id && a.questionVersion===question.datasetVersion).sort((a,b)=>a.at-b.at);
 let due=0,interval=0,independent=0;let last:Attempt|undefined;
 for(const a of history){
  const delayed=!last || a.at-last.at>=DAY;
  if(a.correct && !a.assisted && a.confidence==='known' && delayed){independent++;interval=INTERVALS[Math.min(independent-1,INTERVALS.length-1)]*DAY;}
  else if(!a.correct){independent=0;interval=10*60_000;}
  else if(a.assisted || a.confidence!=='known'){interval=DAY;}
  // Immediate retries do not extend an existing interval or establish mastery.
  due=a.at+interval;last=a;
 }
 return {seen:history.length>0,last,due,interval,independent,mastered:independent>=3 && !!last?.correct && !last.assisted && last.confidence==='known',uncertain:!!last && (last.assisted || last.confidence!=='known')};
}
export function overview(data:Dataset,p:Progress,now=Date.now()) {
 const states=data.questions.map(q=>({q,s:stateFor(q,p.attempts)}));
 return {total:states.length,seen:states.filter(x=>x.s.seen).length,unseen:states.filter(x=>!x.s.seen).length,mastered:states.filter(x=>x.s.mastered).length,due:states.filter(x=>x.s.seen && x.s.due<=now).length,incorrect:states.filter(x=>x.s.last && !x.s.last.correct).length,uncertain:states.filter(x=>x.s.uncertain).length};
}
function shuffled<T>(items:T[],random:()=>number):T[]{
 const result=[...items];
 for(let i=result.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[result[i],result[j]]=[result[j],result[i]];}
 return result;
}
function balanced(questions:Question[],count:number,random:()=>number,randomizePools=true):Question[]{
 const pools=new Map<string,Question[]>();for(const q of questions){if(!pools.has(q.topic))pools.set(q.topic,[]);pools.get(q.topic)!.push(q);}
 const topicPools=shuffled([...pools.values()].map(pool=>randomizePools?shuffled(pool,random):pool),random);
 const out:Question[]=[];while(out.length<count && topicPools.some(a=>a.length)){for(const pool of topicPools){if(pool.length && out.length<count)out.push(pool.shift()!);}}return out;
}
export function createSession(data:Dataset,p:Progress,now=Date.now(),onlyIds?:string[],random:()=>number=Math.random):Session {
 const size=p.sessionSize;const states=data.questions.map(q=>({q,s:stateFor(q,p.attempts)}));
 const due=states.filter(x=>x.s.seen && x.s.due<=now).sort((a,b)=>a.s.due-b.s.due).map(x=>x.q);
 const unseen=states.filter(x=>!x.s.seen).map(x=>x.q);
 let chosen:Question[]=[];const reasons:Record<string,string>={};
 if(onlyIds)chosen=shuffled(data.questions.filter(q=>onlyIds.includes(q.id)),random).slice(0,size);
 else {
  const reviewSlots=Math.round(size*0.6);
  const reviews=balanced(due,reviewSlots,random);const fresh=balanced(unseen,size-reviews.length,random);
  chosen=[...reviews,...fresh];
  if(chosen.length<size){const used=new Set(chosen.map(q=>q.id));chosen.push(...balanced(due.filter(q=>!used.has(q.id)),size-chosen.length,random));}
  // Once the bank is covered, offer earliest future reviews as optional additional practice.
  if(chosen.length===0)chosen=balanced([...states].sort((a,b)=>a.s.due-b.s.due).map(x=>x.q),size,random,false);
 }
 chosen=shuffled(chosen,random);
 for(const q of chosen){const s=stateFor(q,p.attempts);reasons[q.id]=onlyIds?'Vracíme se k chybě z posledního procvičování.':!s.seen?'Náhodně vybraná dosud neprobraná otázka.':s.due<=now?'Je čas tuto otázku zopakovat.':'Dobrovolné opakování již probrané otázky.';}
 return {id:crypto.randomUUID(),questionIds:chosen.map(q=>q.id),index:0,startedAt:now,selected:null,confidence:'unknown',assisted:false,submittedAttemptId:null,reasons};
}
export function submit(p:Progress,q:Question,now=Date.now()):Progress {
 const s=p.session;if(!s || !s.selected || s.submittedAttemptId || s.finishedAt || s.questionIds[s.index]!==q.id)return p;
 const a:Attempt={id:crypto.randomUUID(),questionId:q.id,questionVersion:q.datasetVersion,selected:s.selected,correct:s.selected===q.correctOptionId,confidence:s.confidence,assisted:s.assisted,at:now,sessionId:s.id,mode:'practice'};
 return {...p,attempts:[...p.attempts,a],session:{...s,submittedAttemptId:a.id}};
}
export function next(p:Progress,now=Date.now()):Progress {
 const s=p.session;if(!s?.submittedAttemptId)return p;
 return {...p,session:s.index+1>=s.questionIds.length?{...s,finishedAt:now}:{...s,index:s.index+1,selected:null,confidence:'unknown',assisted:false,submittedAttemptId:null}};
}
export function answerAndAdvance(p:Progress,q:Question,selected:OptionId,now=Date.now()):Progress {
 const s=p.session;if(!s||s.finishedAt||s.submittedAttemptId||s.questionIds[s.index]!==q.id)return p;
 return next(submit({...p,session:{...s,selected}},q,now),now);
}
const CONFIDENCES:Confidence[]=['known','unsure','guess','unknown'];
export function validateImport(value:unknown,data:Dataset):Progress {
 if(!value || typeof value!=='object')throw Error('Soubor neobsahuje platný pokrok.');
 const p=value as Progress;
 if(p.schemaVersion!==1)throw Error('Nepodporovaná verze souboru.');
 if(p.datasetVersion!==data.version)throw Error('Soubor patří k jiné verzi otázek. Import vyžaduje migraci.');
 if(!Array.isArray(p.attempts)||p.attempts.length>100_000 || !Array.isArray(p.bookmarks)|| ![10,15,25].includes(p.sessionSize) || typeof p.onboarded!=='boolean')throw Error('Neplatná struktura pokroku.');
 const ids=new Set(data.questions.map(q=>q.id));const attemptIds=new Set<string>();
 for(const a of p.attempts){if(!a||typeof a!=='object')throw Error('Soubor obsahuje neplatné odpovědi.');const q=data.questions.find(q=>q.id===a.questionId);if(!q || typeof a.id!=='string' || attemptIds.has(a.id) || a.questionVersion!==data.version || !['A','B','C'].includes(a.selected)||typeof a.correct!=='boolean'||a.correct!==(a.selected===q.correctOptionId)||!CONFIDENCES.includes(a.confidence)||typeof a.assisted!=='boolean'||!Number.isFinite(a.at)||a.at<0||typeof a.sessionId!=='string'||a.mode!=='practice')throw Error('Soubor obsahuje neplatné odpovědi.');attemptIds.add(a.id);}
 if(p.bookmarks.some(id=>!ids.has(id)) || new Set(p.bookmarks).size!==p.bookmarks.length)throw Error('Neplatné záložky.');
 if(p.session){const s=p.session;
  if(typeof s.id!=='string'||!Array.isArray(s.questionIds)||!s.questionIds.length||s.questionIds.some(id=>!ids.has(id))||new Set(s.questionIds).size!==s.questionIds.length||!Number.isInteger(s.index)||s.index<0||s.index>=s.questionIds.length||!Number.isFinite(s.startedAt)||!CONFIDENCES.includes(s.confidence)||typeof s.assisted!=='boolean'||!(s.selected===null||['A','B','C'].includes(s.selected))||!s.reasons||typeof s.reasons!=='object'||Object.values(s.reasons).some(x=>typeof x!=='string')||(s.finishedAt!==undefined&&!Number.isFinite(s.finishedAt)))throw Error('Neplatné rozpracované procvičování.');
  const a=p.attempts.find(a=>a.id===s.submittedAttemptId);
  if(s.submittedAttemptId!==null&&(!a||a.sessionId!==s.id||a.questionId!==s.questionIds[s.index]||a.selected!==s.selected))throw Error('Neplatná uložená odpověď.');
 }
 return structuredClone(p);
}
export function mergeProgress(current:Progress,incoming:Progress):Progress {
 const attempts=[...new Map([...incoming.attempts,...current.attempts].map(a=>[a.id,a])).values()].sort((a,b)=>a.at-b.at);
 return {...current,attempts,bookmarks:[...new Set([...current.bookmarks,...incoming.bookmarks])]};
}
