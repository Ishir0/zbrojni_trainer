import {test,expect} from '@playwright/test';
import {seedPractice,navigate} from './helpers';
test('precomputed AI explanation appears only after submission, with choice reasoning and exact sources',async({page},info)=>{
 await seedPractice(page);
 await expect(page.getByRole('region',{name:'AI vysvětlení',exact:true})).toHaveCount(0);
 await page.locator('.current-question button[data-option="A"]').click();
 const explanation=page.getByRole('region',{name:'AI vysvětlení',exact:true});await expect(explanation).toBeVisible();await expect(explanation).toHaveCSS('background-color','rgb(240, 244, 233)');await expect(explanation).toContainText('Návrh · bez odborné kontroly');await expect(explanation.locator('.selected-reason')).toContainText('Proč odpověď A neplatí');
 await explanation.getByText('Vysvětlit jednoduše',{exact:true}).click();await expect(explanation.locator('.explanation-detail')).toBeVisible();
 await explanation.getByText('Zdroje vysvětlení',{exact:true}).click();await expect(explanation.locator('blockquote')).toContainText('Právo nabývat, držet a nosit zbraně');await expect(explanation.locator('.explanation-citations a')).toHaveAttribute('href','https://www.e-sbirka.cz/sb/2024/90?zalozka=text');
 await page.screenshot({path:`tmp/ai-explanation-${info.project.name}.png`,fullPage:true});await page.reload();await page.getByRole('button',{name:'Pokračovat v učení',exact:true}).click();await expect(page.getByRole('region',{name:'AI vysvětlení',exact:true})).toBeVisible();
});
test('unavailable explanations do not block official practice or expose unvalidated prose',async({page})=>{
 await page.route('**/data/explanations.json',route=>route.fulfill({status:404,body:'not available'}));
 await seedPractice(page);await page.locator('.current-question button[data-option="C"]').click();await expect(page.getByRole('region',{name:'Zpětná vazba'}).getByText('Správná odpověď',{exact:true})).toBeVisible();await expect(page.getByText('Vysvětlení připravujeme',{exact:true})).toBeVisible();await expect(page.getByRole('region',{name:'AI vysvětlení',exact:true})).toHaveCount(0);await expect(page.locator('.practice-top')).toContainText('Otázka 2 z 10');await expect(page.locator('.current-question button[data-option="A"]')).toBeEnabled();
});
test('an unresolved source issue stays visible while the official key and browser filters remain usable',async({page})=>{
 await page.route('**/data/explanations.json',async route=>{
  const response=await route.fetch();const pack=await response.json();const original=pack.explanations.find((e:any)=>e.questionId==='q-1');
  pack.explanations=[{...original,status:'needs-source',concise:'',simpler:'',decisiveDetail:'',optionReasoning:{A:'',B:'',C:''},sources:[],issues:['Pro tuto otázku ověřujeme další podklad.']}];pack.coverage={total:837,drafts:0,needsSource:1,missing:836};await route.fulfill({json:pack});
 });
 await seedPractice(page);await page.locator('.current-question button[data-option="C"]').click();await expect(page.getByText('Vysvětlení čeká na ověření',{exact:true})).toBeVisible();await expect(page.getByRole('region',{name:'AI vysvětlení',exact:true})).toHaveCount(0);await page.getByText('Co zbývá ověřit?',{exact:true}).click();await expect(page.getByText('Pro tuto otázku ověřujeme další podklad.',{exact:true})).toBeVisible();await expect(page.locator('.previous-answer .feedback')).toContainText('za podmínek stanovených');
 const menu=page.getByRole('button',{name:'Otevřít navigaci'});if(await menu.isVisible())await menu.click();await page.getByRole('button',{name:'Otázky',exact:true}).click();await page.getByRole('button',{name:'Čeká na podklady',exact:true}).click();await expect(page.locator('.question-row')).toHaveCount(1);await expect(page.locator('.question-row')).toContainText('Právo nabývat, držet a nosit');
});
test('technical explanations derived from the official answer show their basis without invented citations',async({page})=>{
 await page.route('**/data/explanations.json',async route=>{const response=await route.fetch();const pack=await response.json();const e=pack.explanations.find((e:any)=>e.questionId==='q-755');Object.assign(e,{status:'ai-draft',evidenceBasis:'official-answer',concise:'Označení ráže je smluvní označení náboje a jeho použití, nikoli jediný přesný rozměr.',sources:[],issues:[]});await route.fulfill({json:pack});});
 await page.goto('/');await expect(page.locator('.brand')).toBeVisible();const menu=page.getByRole('button',{name:'Otevřít navigaci'});if(await menu.isVisible())await menu.click();await page.getByRole('button',{name:'Otázky',exact:true}).click();await page.getByRole('textbox',{name:'Hledat otázku'}).fill('755');await page.locator('.question-row').click();await page.getByRole('button',{name:'Zobrazit odpověď',exact:true}).click();const explanation=page.getByRole('region',{name:'AI vysvětlení',exact:true});await expect(explanation).toBeVisible();await expect(explanation).toContainText('Odvozeno z oficiální správné odpovědi.');await expect(explanation.getByText('Zdroje vysvětlení',{exact:true})).toHaveCount(0);
});
