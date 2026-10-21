/* PRUMO authentication bridge. Configure the two public values in index.html
   or through the Vercel environment at build time before enabling production auth. */
(function () {
  const url = window.PRUMO_SUPABASE_URL;
  const anon = window.PRUMO_SUPABASE_ANON_KEY;
  const configured = Boolean(url && anon && window.supabase);
  const client = configured ? window.supabase.createClient(url, anon) : null;
  window.prumoSupabaseClient = client;

  function message(text, error) {
    const note = document.querySelector('.login-note');
    if (note) { note.textContent = text; note.classList.toggle('error', Boolean(error)); }
  }

  document.addEventListener('submit', async (event) => {
    if (!event.target || event.target.id !== 'authForm') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const form = event.target;
    const email = form.elements.email?.value.trim();
    const password = form.elements.password?.value;
    const button = form.querySelector('[type="submit"]');
    if (!configured) {
      message('Configure o Supabase na Vercel para ativar o acesso às contas.', true);
      return;
    }
    button.disabled = true;
    button.textContent = 'Acessando…';
    let result;
    const mode = form.elements.name ? 'register' : (form.elements.password ? 'login' : 'recover');
    if (mode === 'register') {
      result = await client.auth.signUp({ email, password, options: { data: { name: form.elements.name?.value.trim() || '' } } });
    } else if (mode === 'recover') {
      result = await client.auth.resetPasswordForEmail(email, { redirectTo: window.location.origin });
    } else {
      result = await client.auth.signInWithPassword({ email, password });
    }
    if (result.error) message(result.error.message, true);
    else if (mode === 'recover') message('Confira seu e-mail para redefinir a senha.');
    else { sessionStorage.setItem('prumo-demo', 'yes'); window.location.reload(); }
    button.disabled = false;
    button.textContent = 'Continuar';
  }, true);

  const cleanDemoCopy = () => {
    document.querySelectorAll('.demo,.login-note').forEach((node) => {
    const replacement = node.classList.contains('demo')
      ? 'Banco de questões de matemática'
      : (configured ? 'Acesse sua conta para continuar.' : null);
    if (replacement !== null && node.textContent !== replacement) node.textContent = replacement;
    });
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const replacement = node.nodeValue.replace(/demonstração|demonstrativo/gi, 'conta');
      if (replacement !== node.nodeValue) node.nodeValue = replacement;
    });
  };
  new MutationObserver(cleanDemoCopy).observe(document.documentElement, { childList: true, subtree: true });
  cleanDemoCopy();
})();
