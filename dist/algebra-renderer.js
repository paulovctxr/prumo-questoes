/* Rendering text transcriptions inside the existing practice interface. */

function algebraQuestionContent(q, selected, showAnswer) {
  if (!q.detailLoaded) return `${questionHeader(q)}<div class="question-text" role="${q.detailError ? 'alert' : 'status'}">
    ${q.detailError ? `Não foi possível carregar esta questão. <button class="btn outline" data-bank-retry="${q.id}">Tentar novamente</button>` : 'Carregando enunciado…'}
    </div>`;
  const graded = Number.isInteger(q.answer);
  const choices = q.options.length ? `<div role="group" aria-label="Alternativas">${q.options.map((option, index) => `
    <button class="option ${showAnswer && graded ? (index === q.answer ? 'correct' : index === selected ? 'wrong' : '') : index === selected ? 'selected' : ''}"
      data-choice="${index}" aria-pressed="${selected === index}" ${showAnswer ? 'disabled' : ''}>
      <span class="letter">${'ABCDE'[index]}</span><span>${fmt(option)}</span>
    </button>`).join('')}</div>` : `<label class="field written-answer-label">Sua resposta
      <textarea rows="4" maxlength="2000" data-written-question="${q.id}"
        ${showAnswer ? 'readonly' : ''} placeholder="Escreva sua resposta antes de consultar a resolução.">${esc(state.writtenAnswers?.[q.id] || '')}</textarea></label>`;
  const figure = q.figure ? `<figure class="bank-essential-figure"><img src="${esc(q.figure.src)}"
    width="${q.figure.width}" height="${q.figure.height}" loading="lazy" decoding="async"
    alt="${esc(q.figure.alt)}"></figure>` : '';
  return `${questionHeader(q)}<div class="question-text bank-transcribed-statement">${fmt(q.text)}</div>${figure}
    ${choices}${showAnswer ? solutionHTML(q, selected) : ''}`;
}

function algebraSolutionHTML(q, selected) {
  const graded = Number.isInteger(q.answer);
  const submitted = graded && Number.isInteger(selected);
  const status = submitted ? (selected === q.answer ? '✓ Você acertou!' : '✕ Você errou esta questão.') : '';
  const answer = q.answerText || (graded ? 'Alternativa ' + 'ABCDE'[q.answer] : '');
  const steps = q.steps.length ? `<ol>${q.steps.map(step => `<li>${fmt(step)}</li>`).join('')}</ol>`
    : '<p class="muted">A resolução comentada desta questão ainda não está disponível.</p>';
  return `${q.steps.length ? `<section class="answer-review" aria-label="Resposta comentada da questão">
      ${status ? `<div class="answer-status ${selected === q.answer ? 'correct' : 'wrong'}" role="status">${status}</div>` : ''}
      <p><strong>Resposta:</strong> ${fmt(answer)}</p>
    </section>` : ''}<section class="solution"><div class="solution-heading"><h3>Resolução comentada</h3></div>
      ${q.solutionNote ? `<p class="notice">${esc(q.solutionNote)}</p>` : ''}${steps}</section>`;
}

document.addEventListener('input', event => {
  const input = event.target.closest('[data-written-question]');
  if (!input || input.readOnly) return;
  state.writtenAnswers ||= {};
  state.writtenAnswers[input.dataset.writtenQuestion] = input.value;
  save();
});
