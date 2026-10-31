import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
test('study screens satisfy automated WCAG accessibility checks',async({page})=>{
 await page.goto('/');await expect(page.locator('.brand')).toBeVisible();
 for(const screen of ['home','question','feedback']){
  if(screen==='question')await page.getByRole('button',{name:'Začít s učením'}).click();
  if(screen==='feedback'){await page.locator('.current-question button[data-option="C"]').click();}
  const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),screen).toEqual([]);
 }
});
