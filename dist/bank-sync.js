/* Fetch a light filter index; load original statements and solutions on demand. */
(function () {
  const client = window.prumoSupabaseClient;
  const detailRequests = new Map();
  const remoteIds = new Set();
  let pending;
  const status = {source: 'local', loaded: 0, refresh};
  window.prumoBankSync = status;

  function validSummary(question, rowId = question?.id) {
    return question && question.bookOriginal === true && Number.isSafeInteger(question.id)
      && question.id === Number(rowId) && typeof question.topic === 'string'
      && typeof question.sub === 'string' && Array.isArray(question.options)
      && (question.answer === null || (Number.isInteger(question.answer)
        && question.answer >= 0 && question.answer < question.options.length));
  }

  async function localIndex() {
    const response = await fetch('questoes-algebra-index.json');
    if (!response.ok) throw new Error('Question index unavailable');
    return response.json();
  }

  async function remoteIndex() {
    if (!client) return [];
    const session = await client.auth.getSession();
    if (!session.data?.session) return [];
    const questions = [];
    for (let offset = 0; ; offset += 1000) {
      const result = await client.from('questoes').select('id,resumo_aplicacao')
        .not('resumo_aplicacao', 'is', null).order('id').range(offset, offset + 999);
      if (result.error || !Array.isArray(result.data)) return [];
      for (const row of result.data) {
        if (validSummary(row.resumo_aplicacao, row.id)) questions.push(row.resumo_aplicacao);
      }
      if (result.data.length < 1000) return questions;
    }
  }

  async function readBank() {
    let summaries;
    try {summaries = await remoteIndex();} catch {summaries = [];}
    const remote = summaries.length > 0;
    if (!remote) summaries = await localIndex();
    const indexes = new Map(QUESTIONS.map((question, index) => [question.id, index]));
    let loaded = 0;
    for (const summary of summaries) {
      if (!validSummary(summary)) continue;
      const previous = indexes.has(summary.id) ? QUESTIONS[indexes.get(summary.id)] : null;
      const cached = previous?.detailLoaded && previous.contentVersion === summary.contentVersion;
      const question = cached ? {...previous, ...summary}
        : {...summary, text: '', steps: [], detailLoaded: false};
      if (indexes.has(summary.id)) QUESTIONS[indexes.get(summary.id)] = question;
      else {indexes.set(summary.id, QUESTIONS.length); QUESTIONS.push(question);}
      if (remote) remoteIds.add(summary.id); else remoteIds.delete(summary.id);
      let topic = TOPICS.find(([name]) => name === question.topic);
      if (!topic) {topic = [question.topic, []]; TOPICS.push(topic);}
      if (!topic[1].includes(question.sub)) topic[1].push(question.sub);
      loaded++;
    }
    status.loaded = loaded;
    status.source = remote ? 'supabase' : 'local';
    if (page === 'questions' || page === 'home') render();
  }

  function refresh() {
    if (!pending) {
      if (page === 'questions') {
        const count = document.getElementById('matchCount');
        const button = document.getElementById('seeQuestions');
        if (count) count.textContent = 'Carregando banco de questões…';
        if (button) button.disabled = true;
      }
      pending = readBank().catch(() => {if (page === 'questions') render();})
        .finally(() => {pending = null;});
    }
    return pending;
  }

  async function readDetail(id) {
    const index = QUESTIONS.findIndex(question => question.id === id);
    if (index < 0) throw new Error('Unknown question');
    const original = QUESTIONS[index];
    let detail;
    if (client && remoteIds.has(id)) {
      try {
        const result = await client.from('questoes').select('dados_aplicacao').eq('id', id).single();
        if (!result.error) detail = result.data?.dados_aplicacao;
      } catch {}
    }
    if (!detail) {
      const response = await fetch(`questoes-algebra/${id}.json`);
      if (!response.ok) throw new Error('Question details unavailable');
      detail = await response.json();
    }
    if (!validSummary(detail, id) || typeof detail.text !== 'string'
      || !Array.isArray(detail.steps)) {
      throw new Error('Invalid question details');
    }
    QUESTIONS[index] = {...original, ...detail, detailLoaded: true, detailError: false};
    return QUESTIONS[index];
  }

  window.ensureQuestionDetail = function (id) {
    const question = QUESTIONS.find(item => item.id === id);
    if (!question?.bookOriginal || question.detailLoaded) return Promise.resolve(question);
    if (!detailRequests.has(id)) {
      const request = readDetail(id).catch(error => {
        const current = QUESTIONS.find(item => item.id === id);
        if (current) current.detailError = true;
        throw error;
      }).finally(() => {detailRequests.delete(id);});
      detailRequests.set(id, request);
    }
    return detailRequests.get(id);
  };

  const visibleKey = () => currentIds.slice(Math.floor(currentIndex / questionsPerPage) * questionsPerPage,
    (Math.floor(currentIndex / questionsPerPage) + 1) * questionsPerPage).join(',');
  window.loadVisibleBankQuestions = function () {
    if (page === 'exam' && state.activeExam) {
      const id = state.activeExam.ids[state.activeExam.index];
      const question = QUESTIONS.find(item => item.id === id);
      if (question?.bookOriginal && !question.detailLoaded && !question.detailError) {
        window.ensureQuestionDetail(id).catch(() => {}).then(() => {
          if (page === 'exam' && state.activeExam?.ids[state.activeExam.index] === id) render();
        });
      }
      return;
    }
    const key = visibleKey();
    const ids = key.split(',').map(Number).filter(id => {
      const question = QUESTIONS.find(item => item.id === id);
      return question?.bookOriginal && !question.detailLoaded && !question.detailError;
    });
    if (!ids.length) return;
    Promise.allSettled(ids.map(window.ensureQuestionDetail)).then(() => {
      if (page === 'resolve' && visibleKey() === key) render();
    });
  };

  document.addEventListener('click', event => {
    const button = event.target.closest('[data-bank-retry]');
    if (!button) return;
    const id = Number(button.dataset.bankRetry);
    const question = QUESTIONS.find(item => item.id === id);
    if (question) question.detailError = false;
    window.ensureQuestionDetail(id).catch(() => {}).then(() => {
      if (solutionDrawerQuestionId === id) {
        openSolutionDrawer(QUESTIONS.find(item => item.id === id), questionDrafts[id]);
      } else if (page === 'resolve') render();
    });
  });

  if (client) {
    client.auth.onAuthStateChange((event, session) => {
      if (session && ['INITIAL_SESSION', 'SIGNED_IN', 'TOKEN_REFRESHED'].includes(event)) setTimeout(refresh, 0);
    });
  }
  if (logged) refresh();
})();
