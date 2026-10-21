'use strict';
// Editorial estimates, not item response statistics or official exam ratings.
const DIFFICULTY_REFERENCES=[
  {title:'Curso Progressão — análise da prova ESA de 08/10/2023',url:'https://www.cursoprogressao.com.br/wp-content/uploads/2023/10/Gabarito-ESA-Modelo-C.pdf',note:'Professores descrevem a matemática dessa edição como fácil/média; não é uma classificação de todas as edições.'},
  {title:'Fábrica D — preparação IME/ITA',url:'https://www.fabricad.online/fabrica-de-engenheiros-militares-dois-anos',note:'Preparatório caracteriza IME e ITA entre os vestibulares mais difíceis do país.'},
  {title:'O Dia — preparação para Escola Naval',url:'https://odia.ig.com.br/rio-de-janeiro/2021/03/amp/6096963-como-se-preparar-para-a-escola-naval.html',note:'Especialista destaca a dificuldade elevada da matemática e conteúdos avançados.'},
  {title:'Elementar — listas para concursos militares',url:'https://sistemaelementar.com.br/blog/listas-de-exercicios-gratuitas-epcar',note:'Relaciona o nível de exigência de matemática das provas EEAR, ESA e EAM.'},
  {title:'Gabarite — simulado de matemática CFN',url:'https://gabarite.com.br/simulado-concurso/7494-cfn-matematica-financeira-soldado-fuzileiro-naval-2016',note:'Exemplo de simulado CFN classificado como fácil; evidência limitada, não generalizável a cada questão.'},
  {title:'Gabarite — simulado de matemática EFOMM',url:'https://gabarite.com.br/simulado-concurso/2918-marinha-mercante-efomm-matematica-oficial-da-marinha',note:'Exemplo de simulado EFOMM classificado como difícil; usado somente como referência editorial.'}
];
const EXAM_DIFFICULTY_POLICY={
  IME:{level:'Difícil',sources:[1],reason:'Estimativa editorial pelo perfil avançado da prova.'},
  ITA:{level:'Difícil',sources:[1],reason:'Estimativa editorial pelo perfil avançado da prova.'},
  'ESCOLA NAVAL':{level:'Difícil',sources:[2],reason:'Estimativa editorial pelo perfil avançado de matemática da prova.'},
  EFOMM:{level:'Difícil',sources:[5],reason:'Estimativa editorial pelo perfil da prova; o simulado consultado não avalia todas as edições.'},
  AFA:{level:'Difícil',sources:[],reason:'Estimativa editorial provisória para prova de formação de oficiais. Requer revisão individual; não há consenso específico cadastrado.'},
  ESA:{level:'Média',sources:[0],reason:'Faixa editorial intermediária, seguindo a referência fácil/média e a preferência do responsável pelo PRUMO.'},
  EEAR:{level:'Média',sources:[3],reason:'Faixa editorial intermediária, comparada ao grupo ESA e seguindo a preferência do responsável pelo PRUMO.'},
  ESPCEX:{level:'Média',sources:[],reason:'Estimativa editorial provisória para o perfil da prova. Sem referência específica validada nesta rodada.'},
  CFN:{level:'Fácil',sources:[4],reason:'Faixa editorial inicial, seguindo a preferência do responsável pelo PRUMO e exemplo de simulado. Não significa que todas as questões sejam fáceis.'},
  EAM:{level:'Fácil',sources:[3],reason:'Estimativa editorial provisória de faixa inicial. A referência aproxima ESA, EEAR e EAM; a distinção em três faixas é do PRUMO.'},
  EPCAR:{level:'Média',sources:[],reason:'Estimativa editorial provisória; sem referência específica validada nesta rodada.'},
  CPCAR:{level:'Média',sources:[],reason:'Estimativa editorial provisória; sem referência específica validada nesta rodada.'},
  'COLÉGIO NAVAL':{level:'Difícil',sources:[],reason:'Estimativa editorial provisória para matemática aprofundada no nível fundamental. Sem referência específica validada nesta rodada.'}
};
for(const q of QUESTIONS){
  if(q.difficulty!=='Não classificada')continue;
  const policy=EXAM_DIFFICULTY_POLICY[String(q.exam||'').trim().toLocaleUpperCase('pt-BR')];
  const topic=String(q.topic||'').toLocaleLowerCase('pt-BR');
  const advanced=/cálculo diferencial|cálculo integral|limites e continuidade/.test(topic);
  const basic=/matemática básica|aritmética|razão, proporção|porcentagem|noções de lógica|conjuntos/.test(topic);
  q.difficultyOriginal=q.difficulty;
  q.difficulty=policy?.level||(advanced?'Difícil':basic?'Fácil':'Média');
  q.difficultyEstimated=true;
  q.difficultyMethod=policy?'Perfil da prova':'Triagem pelo assunto';
  q.difficultyReason=policy?.reason||'Estimativa automática provisória pelo assunto: fundamentos → fácil; cálculo avançado → difícil; demais conteúdos → média. Não houve avaliação individual do enunciado nem pesquisa específica para esta prova.';
  q.difficultySources=policy?.sources||[];
}
