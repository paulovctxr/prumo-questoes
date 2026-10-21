/* Original book exercises. Solutions are authored separately from the source. */
(function () {
  let catalogPromise;
  const selection = {chapter: '', search: '', solvedOnly: false, page: 0};
  const pageSize = 8;
  let renderVersion = 0;
  const escape = value => String(value ?? '').replace(/[&<>"']/g,
    char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
  const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  function picture(image, alt) {
    return `<img class="book-original" src="${escape(image.src)}" width="${image.width}" height="${image.height}" loading="lazy" decoding="async" alt="${escape(alt)}">`;
  }

  function questionCard(question, book) {
    const chapter = book.chapters.find(item => item.id === question.chapter);
    const solution = question.solution;
    return `<article class="book-question" id="book-question-${question.chapter}-${question.number}">
      <header><h3>Questão ${question.number} · ${escape(chapter.title)}</h3>
        <p class="muted small">${escape(book.title)} (${book.year}) · página ${question.page}</p></header>
      ${question.images.map((image, index) => picture(image, `Questão ${question.number}, ${chapter.title}, original do livro, parte ${index + 1}`)).join('')}
      <a class="link small" href="livro-algebra/original.pdf#page=${question.page}" target="_blank" rel="noopener">Ver a página no PDF original</a>
      ${solution ? `<details class="book-solution"><summary>Ver gabarito e resolução passo a passo</summary>
        <p class="book-answer"><strong>Resposta:</strong> ${escape(solution.answer)}</p>
        ${solution.editorial_note ? `<p class="notice">${escape(solution.editorial_note)}</p>` : ''}
        <ol>${solution.steps.map(step => `<li>${fmt(step)}</li>`).join('')}</ol>
        <p class="muted small">Resolução elaborada para o PRUMO. Enunciado original preservado.</p>
      </details>` : `<p class="muted small book-pending">A resolução passo a passo desta questão ainda não foi adicionada.</p>`}
      <details class="book-answer-source"><summary>Consultar o gabarito original deste capítulo</summary>
        <p class="muted small">Localize a questão ${question.number} nas páginas de respostas abaixo. O gabarito impresso pode conter divergências; quando identificadas, elas são explicadas na resolução.</p>
        ${chapter.answerImages.map(image => picture(image, `Respostas originais de ${chapter.title}, página ${image.page}`)).join('')}
      </details>
    </article>`;
  }

  function update(book, host) {
    const chapter = selection.chapter;
    const search = normalize(selection.search.trim());
    const questions = book.questions.filter(question => (!chapter || question.chapter === chapter)
      && (!selection.solvedOnly || question.solution)
      && (!search || normalize(question.searchText + ' ' + question.number).includes(search)));
    const pages = Math.max(1, Math.ceil(questions.length / pageSize));
    selection.page = Math.min(selection.page, pages - 1);
    const visible = questions.slice(selection.page * pageSize, (selection.page + 1) * pageSize);
    host.querySelector('#book-count').textContent = `${questions.length} questões encontradas`;
    host.querySelector('#book-results').innerHTML = visible.map(question => questionCard(question, book)).join('')
      || '<p class="notice">Nenhuma questão corresponde aos filtros.</p>';
    host.querySelector('#book-pagination').innerHTML = `<button class="btn outline" data-book-page="prev" ${selection.page === 0 ? 'disabled' : ''}>Anterior</button>
      <span>Página ${selection.page + 1} de ${pages}</span>
      <button class="btn outline" data-book-page="next" ${selection.page >= pages - 1 ? 'disabled' : ''}>Próxima</button>`;
    math();
  }

  window.renderBook = async function () {
    const version = ++renderVersion;
    const host = document.getElementById('main');
    host.innerHTML = '<p role="status">Carregando as questões do livro…</p>';
    try {
      if (!catalogPromise) catalogPromise = fetch('livro-algebra/catalog.json').then(response => {
        if (!response.ok) throw new Error('Não foi possível carregar o catálogo.');
        return response.json();
      }).catch(error => {catalogPromise = null; throw error;});
      const book = await catalogPromise;
      if (version !== renderVersion || !host.isConnected || page !== 'book') return;
      host.innerHTML = `<section class="book-intro"><span class="badge">EXERCÍCIOS ORIGINAIS</span>
        <h1>${escape(book.title)}</h1><p>${escape(book.authors.join(' · '))} · ${book.year}</p>
        <p>Enunciados, alternativas e figuras preservados do PDF enviado.</p>
        <p class="muted">${book.total} exercícios · ${book.completeSolutions} com resolução passo a passo disponível.</p></section>
        <section class="book-filters" aria-label="Filtros do livro">
          <label class="field">Capítulo<select id="book-chapter"><option value="">Todos os capítulos</option>
            ${book.chapters.map(chapter => `<option value="${chapter.id}">${escape(chapter.title)}</option>`).join('')}</select></label>
          <label class="field">Buscar no enunciado<input id="book-search" type="search" placeholder="Palavra ou número da questão"></label>
          <label class="inline-check"><input type="checkbox" id="book-solved">Somente questões com resolução passo a passo</label>
        </section><p id="book-count" role="status"></p><div id="book-results"></div>
        <nav id="book-pagination" class="book-pagination" aria-label="Páginas do livro"></nav>`;
      const chapterInput = host.querySelector('#book-chapter');
      const searchInput = host.querySelector('#book-search');
      const solvedInput = host.querySelector('#book-solved');
      chapterInput.value = selection.chapter;
      searchInput.value = selection.search;
      solvedInput.checked = selection.solvedOnly;
      chapterInput.addEventListener('change', () => {selection.chapter = chapterInput.value; selection.page = 0; update(book, host);});
      searchInput.addEventListener('input', () => {selection.search = searchInput.value; selection.page = 0; update(book, host);});
      solvedInput.addEventListener('change', () => {selection.solvedOnly = solvedInput.checked; selection.page = 0; update(book, host);});
      host.querySelector('#book-pagination').addEventListener('click', event => {
        const button = event.target.closest('[data-book-page]');
        if (!button || button.disabled) return;
        selection.page += button.dataset.bookPage === 'next' ? 1 : -1;
        update(book, host);
        host.querySelector('#book-count').scrollIntoView({block: 'start'});
      });
      update(book, host);
    } catch (error) {
      if (!host.isConnected || page !== 'book') return;
      host.innerHTML = '<p role="alert">Não foi possível carregar o livro. Tente novamente.</p><button class="btn" id="book-retry">Tentar novamente</button>';
      host.querySelector('#book-retry').addEventListener('click', window.renderBook);
    }
  };
})();
