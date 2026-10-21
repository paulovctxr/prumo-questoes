// Run against the existing local server: node tools/test-bank.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = 'http://127.0.0.1:8000/';
const root = path.resolve(__dirname, '..');
const summaries = JSON.parse(fs.readFileSync(path.join(root, 'dist/questoes-algebra-index.json')));
const detail = JSON.parse(fs.readFileSync(path.join(root, 'dist/questoes-algebra/1011002.json')));

async function ready(page) {
  await page.goto(base, {waitUntil: 'networkidle'});
  await page.waitForFunction(() => window.prumoBankSync?.loaded === 712 && QUESTIONS.length === 2822);
}

async function transcriptionVisible(page) {
  await page.waitForFunction(() => {
    const statement = document.querySelector('.question-card .bank-transcribed-statement');
    return statement?.textContent.trim().length > 0;
  });
}

function mockBridge(databaseError, legacy = false) {
  const legacyOptions = detail.options.map((_,index) => `Alternativa ${'ABCDE'[index]}`);
  const remote = legacy ? {...detail,
    text: `${detail.text}\n\na) Todas as proposições estão corretas.\n\nb) Apenas I, II, III e IV estão corretas\n\nc) Apenas I, II e V estão corretas\n\nd) Somente IV está incorreta\n\ne) Todas as proposições estão incorretas.`,
    options: legacyOptions, bookImages:[{src:'livro-algebra/q.webp'}],
    bookAnswerImages:[{src:'livro-algebra/answers.webp'}], contentVersion:'legacy'}
    : {...detail, steps: [...detail.steps, 'Origem remota confirmada no teste.']};
  const remoteSummaries = legacy ? summaries.map(question => {
    const oldMetadata = {...question, difficulty:'Não classificada', year:null, exam:'Fonte antiga'};
    return question.id === detail.id
      ? {...oldMetadata, options:legacyOptions, contentVersion:'legacy'} : oldMetadata;
  }) : summaries;
  return `window.prumoSupabaseClient = {
    auth: {getSession: async () => ({data: {session: {user: {id: 'test'}}}}), onAuthStateChange() {}},
    from(table) {
      if (table !== 'questoes') throw Error('Wrong table');
      return {select(fields) {this.fields = fields; return this;}, not() {return this;}, order() {return this;},
        eq(field,id) {if (field !== 'id' || id !== 1011002) throw Error('Wrong detail ID'); return this;},
        range: async (start,end) => (${databaseError ? "{error: {message: 'column not installed'}}" :
          `{data: ${JSON.stringify(remoteSummaries.map(q => ({id:q.id,resumo_aplicacao:q})))},error:null}`} ),
        single: async () => ({data: {dados_aplicacao: ${JSON.stringify(remote)}},error:null})};
    }
  };`;
}

(async () => {
  const browser = await chromium.launch({executablePath:'/usr/bin/chromium', args:['--no-sandbox']});
  try {
    const context = await browser.newContext();
    await context.addInitScript(() => sessionStorage.setItem('prumo-demo','yes'));
    const page = await context.newPage();
    const errors = [];
    const requestedDetails = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (/\/questoes-algebra\/\d+\.json$/.test(request.url())) requestedDetails.push(request.url());
    });
    await ready(page);
    assert.equal(await page.evaluate(() => QUESTIONS.filter(question => question.bookOriginal
      && question.difficulty === 'Difícil' && question.year === 2026).length),712);
    assert.deepEqual(requestedDetails, [], 'Opening filters must not download all question details');
    assert.match(await page.locator('#matchCount').innerText(), /2822/);
    assert.equal(await page.locator('[data-nav="book"],.book-entry').count(), 0);
    await page.locator('input[data-multi="topics"][value="Conjuntos"]').check();
    assert.equal(await page.evaluate(() => filterQuestions(state, filters).filter(q => q.bookOriginal).length),34);
    await page.evaluate(() => startQuestions([1011002]));
    await transcriptionVisible(page);
    assert.equal(await page.locator('.question-card img').count(),0);
    assert.match(await page.locator('.question-card .option').first().innerText(),/Todas as proposições/);
    assert.equal(requestedDetails.length,1);
    await page.locator('.question-card .option').nth(3).click();
    await page.getByRole('button',{name:'Responder →',exact:true}).click();
    assert.equal(await page.evaluate(() => state.attempts.at(-1).correct),true);
    await page.getByRole('button',{name:'Ver solução e comentários',exact:true}).click();
    await page.waitForSelector('.solution-drawer');
    assert.equal(await page.locator('.solution-drawer .solution li').count(),4);
    assert.equal(await page.locator('.katex-error').count(),0);
    await page.getByRole('button',{name:'Fechar resolução',exact:true}).click();
    await page.evaluate(() => startQuestions([1011001]));
    await transcriptionVisible(page);
    await page.locator('[data-written-question="1011001"]').fill('32 subconjuntos');
    assert.equal(await page.evaluate(() => state.writtenAnswers[1011001]),'32 subconjuntos');
    assert.equal(await page.locator('.question-card [data-action="answer"]').count(),0);
    assert.equal(await page.evaluate(() => state.attempts.length),1);
    await page.evaluate(() => {
      state.activeExam={id:'test',name:'Teste de integração',ids:[1011008],answers:{},flags:[],startedAt:Date.now(),duration:300,index:0};
      page='exam';render();
    });
    await transcriptionVisible(page);
    await page.locator('.question-card .option').nth(4).click();
    await page.evaluate(() => finishExam(true));
    assert.equal(await page.evaluate(() => scoreExam(state.exams.at(-1)).correct),1);
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(() => startQuestions([1011002]));
    await transcriptionVisible(page);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    let attempts=0;
    await page.route('**/questoes-algebra/1011003.json', route => ++attempts===1
      ? route.fulfill({status:503,body:'Unavailable'}) : route.continue());
    await page.evaluate(() => startQuestions([1011003]));
    await page.waitForSelector('[data-bank-retry="1011003"]');
    await page.locator('[data-bank-retry="1011003"]').click();
    await transcriptionVisible(page);
    assert.equal(attempts,2);
    await page.evaluate(() => startQuestions([1272029]));
    await transcriptionVisible(page);
    await page.waitForFunction(() => {
      const image=document.querySelector('.bank-essential-figure img');
      return image?.complete && image.naturalWidth>0;
    });
    assert.match(await page.locator('.bank-essential-figure img').getAttribute('src'),
      /^questoes-algebra-figuras\/1272029\.webp$/);
    assert.equal(await page.locator('.question-card .option').count(),4);
    await page.evaluate(() => {filters=blankFilters();nav('questions')});
    await page.getByRole('button',{name:'Criar lista',exact:true}).click();
    await page.waitForSelector('.list-drawer');
    assert.equal(await page.locator('[name="name"]').getAttribute('placeholder'),'Insira o nome da lista');
    assert.equal(await page.locator('.list-specialty-row').count(),
      await page.evaluate(() => new Set(QUESTIONS.map(question => question.topic)).size));
    assert.match(await page.locator('#listSelectedMessage').innerText(),/2\.822 questões/);
    assert.equal(await page.locator('#createListSubmit').isDisabled(),true);
    await page.locator('[name="name"]').fill('Lista de revisão completa');
    await page.locator('#fitListLimit').click();
    assert.match(await page.locator('#listSelectedMessage').innerText(),/1\.000 questões/);
    assert.equal(await page.locator('#createListSubmit').isEnabled(),true);
    await page.locator('#createListSubmit').click();
    await page.waitForSelector('.list-card');
    assert.equal(await page.evaluate(() => state.lists.at(-1).ids.length),1000);
    assert.equal(await page.getByRole('heading',{name:'Lista de revisão completa'}).count(),1);
    assert.deepEqual(errors,[]);
    await context.close();
    console.log('PASS shared bank: 2822 questions, topic filters, demand loading, grading, written responses, exams, mobile and retry.');

    const remoteContext = await browser.newContext();
    await remoteContext.addInitScript(() => sessionStorage.setItem('prumo-demo','yes'));
    const remotePage = await remoteContext.newPage();
    const remoteErrors=[];
    remotePage.on('pageerror', e => remoteErrors.push(e.message));
    await remotePage.route('**/supabase-auth.js', route => route.fulfill({contentType:'text/javascript',body:mockBridge(false)}));
    await remotePage.route('**/questoes-algebra-index.json', route => route.abort());
    await remotePage.route('**/questoes-algebra/*.json', route => route.abort());
    await ready(remotePage);
    assert.equal(await remotePage.evaluate(() => prumoBankSync.source),'supabase');
    await remotePage.evaluate(() => startQuestions([1011002]));
    await transcriptionVisible(remotePage);
    assert(await remotePage.evaluate(() => QUESTIONS.find(q=>q.id===1011002).steps.includes('Origem remota confirmada no teste.')));
    await remotePage.evaluate(() => prumoBankSync.refresh());
    assert.equal(await remotePage.evaluate(() => QUESTIONS.length),2822);
    assert.deepEqual(remoteErrors,[]);
    await remoteContext.close();
    console.log('PASS Supabase adapter (mock): light metadata query, one-question detail, no static fallback requests, refresh without duplicates.');

    const legacyContext = await browser.newContext();
    await legacyContext.addInitScript(() => sessionStorage.setItem('prumo-demo','yes'));
    const legacyPage = await legacyContext.newPage();
    const legacyRequests=[];
    legacyPage.on('request', request => {
      if (/\/questoes-algebra\/1011002\.json$/.test(request.url())) legacyRequests.push(request.url());
    });
    await legacyPage.route('**/supabase-auth.js', route => route.fulfill({contentType:'text/javascript',body:mockBridge(false,true)}));
    await legacyPage.route('**/questoes-algebra-index.json', route => route.abort());
    await ready(legacyPage);
    assert.equal(await legacyPage.evaluate(() => QUESTIONS.filter(question => question.bookOriginal
      && question.difficulty === 'Difícil' && question.year === 2026
      && question.exam === 'Tópicos de Álgebra Elementar').length),712);
    await legacyPage.evaluate(() => startQuestions([1011002]));
    await transcriptionVisible(legacyPage);
    assert.equal(legacyRequests.length,1);
    assert.doesNotMatch(await legacyPage.locator('.bank-transcribed-statement').innerText(),/a\)\s*Todas/);
    assert.match(await legacyPage.locator('.question-card .option').first().innerText(),/Todas as proposições/);
    await legacyContext.close();
    console.log('PASS legacy Supabase import: photographed duplicate falls back to the current text and real option buttons.');

    const fallbackContext=await browser.newContext();
    await fallbackContext.addInitScript(() => sessionStorage.setItem('prumo-demo','yes'));
    const fallback=await fallbackContext.newPage();
    await fallback.route('**/supabase-auth.js', route => route.fulfill({contentType:'text/javascript',body:mockBridge(true)}));
    await ready(fallback);
    assert.equal(await fallback.evaluate(() => prumoBankSync.source),'local');
    await fallbackContext.close();
    console.log('PASS missing Supabase migration: original bank remains usable with the prepared metadata index.');
  } finally {await browser.close();}
})().catch(error => {console.error(error);process.exit(1);});
