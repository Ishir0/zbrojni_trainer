import {defineConfig} from '@playwright/test';
const port=Number(process.env.PLAYWRIGHT_PORT||4173);
const baseURL=`http://127.0.0.1:${port}`;
export default defineConfig({testDir:'./tests/browser',fullyParallel:false,use:{baseURL,headless:true},webServer:{command:`npm run dev -- --host 127.0.0.1 --port ${port} --strictPort`,url:baseURL,reuseExistingServer:true},projects:[{name:'desktop',use:{viewport:{width:1440,height:1080}}},{name:'mobile',use:{viewport:{width:390,height:844},isMobile:true,hasTouch:true}}]});
