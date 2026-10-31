export type OptionId = 'A' | 'B' | 'C';
export type Confidence = 'known' | 'unsure' | 'guess' | 'unknown';
export interface Question {id:string;number:number;stem:string;options:{id:OptionId;text:string}[];correctOptionId:OptionId;topic:string;page:number;images:{src:string;page:number;optionId:OptionId|null}[];verification:string;explanationStatus:'pending';datasetVersion:string}
export interface Dataset {version:string;sourceUrl:string;sourceSha256:string;topics:string[];questions:Question[]}
export interface Attempt {id:string;questionId:string;questionVersion:string;selected:OptionId;correct:boolean;confidence:Confidence;assisted:boolean;at:number;sessionId:string;mode:'practice'}
export interface Session {id:string;questionIds:string[];index:number;startedAt:number;selected:OptionId|null;confidence:Confidence;assisted:boolean;submittedAttemptId:string|null;finishedAt?:number;reasons:Record<string,string>}
export interface Progress {schemaVersion:1;attempts:Attempt[];bookmarks:string[];session:Session|null;sessionSize:number;onboarded:boolean;datasetVersion:string}
export interface QuestionState {seen:boolean;last?:Attempt;due:number;interval:number;independent:number;mastered:boolean;uncertain:boolean}
export interface ExplanationCitation {sourceId:string;url:string;file:string;locator:string;quote:string;evidenceType?:'web-reference';title?:string}
export interface Explanation {questionId:string;datasetVersion:string;correctOptionId:OptionId;status:'ai-draft'|'needs-source';evidenceBasis?:'source-grounded'|'official-answer';concise:string;simpler:string;optionReasoning:Record<OptionId,string>;decisiveDetail:string;sources:ExplanationCitation[];issues:string[];model:'gpt-6-luna'}
export interface ExplanationPack {schemaVersion:1;datasetVersion:string;generatedAt:string;model:'gpt-6-luna';reviewStatus:'ai-draft';coverage:{total:number;drafts:number;needsSource:number;missing:number};sources:{id:string;title:string;url:string;textSha256:string}[];explanations:Explanation[]}
