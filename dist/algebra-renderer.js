/* Rendering original-page exercises inside the existing practice interface. */
function algebraOriginalImages(images, label) {
  return images.map((image, index) => `<img class="bank-original-image" src="${esc(image.src)}"
    width="${image.width}" height="${image.height}" loading="lazy" decoding="async"
    alt="${esc(label)}${images.length > 1 ? ', parte ' + (index + 1) : ''}">`).join('');
}

function algebraQuestionContent(q, selected, showAnswer) {
  if (!q.detailLoaded) return `${questionHeader(q)}<div class="question-text" role="${q.detailError ? 'alert' : 'status'}">
    ${q.detailError ? `Não foi possível carregar esta questão. <button class="btn outline" data-bank-retry="${q.id}">Tentar novamente</button>` : 'Carregando enunciado…'}
    </div>`;
  const graded = Number.isInteger(q.answer);
  const choices = q.options.length ? `<div role="group" aria-label="Alternativas">${q.options.map((option, index) => `
    <button class="option ${showAnswer && graded ? (index === q.answer ? 'correct' : index === selected ? 'wrong' : '') : index === selected ? 'selected' : ''}"
      data-choice="${index}" aria-pressed="${selected === index}" ${showAnswer ? 'disabled' : ''}>
      <span class="letter">${'ABCDE'[index]}</span><span>Alternativa ${'ABCDE'[index]} (na imagem)</span>
    </button>`).join('')}</div>` : `<label class="field written-answer-label">Sua resposta
      <textarea rows="4" maxlength="2000" data-written-question="${q.id}"
        ${showAnswer ? 'readonly' : ''} placeholder="Escreva sua resposta antes de consultar a resolução.">${esc(state.writtenAnswers?.[q.id] || '')}</textarea></label>`;
  return `${questionHeader(q)}<div class="bank-original-statement">${algebraOriginalImages(q.bookImages,
    `Enunciado e alternativas originais da questão ${q.source.number}, ${q.source.chapter}`)}</div>
    ${choices}${showAnswer ? solutionHTML(q, selected) : ''}`;
}

function algebraSolutionHTML(q, selected) {
  const graded = Number.isInteger(q.answer);
  const submitted = graded && Number.isInteger(selected);
  const status = submitted ? (selected === q.answer ? '✓ Você acertou!' : '✕ Você errou esta questão.') : '';
  const answer = q.answerText || (graded ? 'Alternativa ' + 'ABCDE'[q.answer] : 'Consulte o gabarito original abaixo.');
  const steps = q.steps.length ? `<ol>${q.steps.map(step => `<li>${fmt(step)}</li>`).join('')}</ol>`
    : '<p class="muted">A resolução comentada desta questão ainda não está disponível.</p>';
  return `<section class="answer-review" aria-label="Gabarito da questão">
      ${status ? `<div class="answer-status ${selected === q.answer ? 'correct' : 'wrong'}" role="status">${status}</div>` : ''}
      <p><strong>${q.steps.length ? 'Resposta:' : 'Gabarito transcrito:'}</strong> ${esc(answer)}</p>
    </section><section class="solution"><div class="solution-heading"><h3>Resolução comentada</h3></div>
      ${q.solutionNote ? `<p class="notice">${esc(q.solutionNote)}</p>` : ''}${steps}
      <details class="bank-printed-answer"><summary>Gabarito original · questão ${q.source.number}</summary>
        ${algebraOriginalImages(q.bookAnswerImages, `Gabarito original de ${q.source.chapter}`)}
      </details></section>`;
}

document.addEventListener('input', event => {
  const input = event.target.closest('[data-written-question]');
  if (!input || input.readOnly) return;
  state.writtenAnswers ||= {};
  state.writtenAnswers[input.dataset.writtenQuestion] = input.value;
  save();
});
