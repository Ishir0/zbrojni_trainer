import {chromium} from '@playwright/test';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const manifest=JSON.parse(await readFile('sources/source-manifest.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 for(const entry of manifest.filter(e=>e.file.includes('/law-')&&!e.renderedText)){
  const page=await browser.newPage();
  const responses=[];
  page.on('response',async r=>{if(r.url().includes('/dokumenty-sbirky/'))responses.push({url:r.url(),status:r.status()});});
  await page.goto(entry.url,{waitUntil:'networkidle',timeout:50000});
  await page.getByText('Stáhnout',{exact:true}).first().waitFor();
  const text=await page.locator('body').innerText();
  if(text.length<2500 || !(text.includes('§ 1')||text.includes('Čl. 1')||text.includes('Čl.1')))throw Error(`Law text not loaded: ${entry.url}`);
  const file=entry.file.replace('.html','.txt');
  await writeFile(file,text);
  entry.renderedText={file,sha256:createHash('sha256').update(text).digest('hex'),retrievedAt:new Date().toISOString(),characters:text.length,note:'Rendered official page text; includes page navigation. Verify completeness and effective version before editorial use.'};
  entry.status='rendered-official-text';
  console.log(entry.title,text.length,'characters');
  // Retain observed official metadata endpoints for reproducible follow-up.
  await writeFile(file.replace('.txt','-requests.json'),JSON.stringify(responses,null,2)+'\n');
  await writeFile('sources/source-manifest.json',JSON.stringify(manifest,null,2)+'\n');
  await page.close();
 }
 await writeFile('sources/source-manifest.json',JSON.stringify(manifest,null,2)+'\n');
 await writeFile('public/data/sources.json',JSON.stringify(manifest.map(({title,url,status})=>({title,url,status})),null,2)+'\n');
}finally{await browser.close();}
