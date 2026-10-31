import {openDB} from 'idb';
import type {Progress} from './types';
const db=openDB('zbrojni-trainer',1,{upgrade(db){db.createObjectStore('learner');}});
export async function loadProgress():Promise<Progress|undefined>{return (await db).get('learner','progress');}
export async function saveProgress(p:Progress){await (await db).put('learner',p,'progress');}
