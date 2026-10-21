// Correções editoriais conferidas com as páginas 154–158 da apostila.
// As referências, IDs e gabaritos são preservados; não se inferem fórmulas ausentes.
(() => {
  const symbols = {
    '\uF041':'A', '\uF0CD':'⊆', '\uF0CE':'∈', '\uF0B9':'≠',
    '\uF0B1':'±', '\uF0B3':'≥', '\uF0A3':'≤', '\uF05B':'[',
    '\uF05D':']', '\uF03E':'>', '\uF03C':'<', '\uF06A':'ϕ',
    '\uF0C6':'∅', '\uF049':'I', '\uF04E':'N', '\uF022':'∀',
    '\uF0D7':'⋅', '\uF0B4':'×', '\uF0B0':'°', '\uF071':'θ',
    '\uF070':'π', '\uF0A5':'∞', '\uF06C':'λ', '\uF067':'γ',
    '\uF061':'α', '\uF0F2':'∫', '\uF0A2':'′'
  };
  function decodeSymbolFont(text) {
    return String(text).replace(/\uF049\s*\uF04E/g,'ℕ')
      .replace(/[\uE000-\uF8FF]/g, c => symbols[c] ?? c);
  }
  for (const q of QUESTIONS) {
    const text=decodeSymbolFont(q.text), options=q.options.map(decodeSymbolFont);
    if(text!==q.text || options.some((v,i)=>v!==q.options[i]))q.symbolEncodingCorrected=true;
    q.text=text; q.options=options;
  }
  const fixes = {
    164001: {text:String.raw`Seja um triângulo inscrito em uma circunferência de raio $R$. Se esse triângulo tem um ângulo medindo $30°$, seu lado oposto a esse ângulo mede`,options:[String.raw`$\frac{R}{2}$`,'$R$','$2R$',String.raw`$\frac{2R}{3}$`]},
    164002: {text:'Se A, B, C e D são pontos da circunferência, o valor de $x$ é múltiplo de'},
    164003: {text:'Considere uma roda de 20 cm de raio que gira, completamente e sem interrupção, 20 vezes no solo. Assim, a distância que ela percorre é ____ $π$ m.'},
    164004: {text:'Considere o quadrilátero ABCO, de vértices A, B e C na circunferência e vértice O no centro dela. Nessas condições, $x$ mede'},
    164005: {text:'O triângulo ABC está inscrito na circunferência. Se $BC = 8$, a medida do raio é',options:[String.raw`$4\sqrt{2}$`,String.raw`$2\sqrt{2}$`,'$4$','$2$']},
    164006: {text:String.raw`O segmento $\overline{AT}$ é tangente, em T, à circunferência de centro O e raio $R = 8$ cm. A potência de A em relação à circunferência é igual a ______ cm².`},
    164007: {text:String.raw`Dado um hexágono regular de 6 cm de lado, considere o seu apótema medindo $a$ cm e o raio da circunferência a ele circunscrita medindo $R$ cm. O valor de $(R + a\sqrt{3})$ é`},
    164008: {text:String.raw`O ponto $O_{\mathrm{I}}$ é o centro da circunferência I, que tem raio medindo 6 cm. O ponto $O_{\mathrm{II}}$ é o centro da circunferência II, que tem raio medindo 2 cm. O segmento $\overline{AB}$ é tangente à circunferência I, em A, e passa por $O_{\mathrm{II}}$. Se $O_{\mathrm{I}}O_{\mathrm{II}} = 10$ cm, então $AB =$ _______ cm.`},
    164009: {text:String.raw`Sejam A, B e C pontos da circunferência de centro O. Se $m(\widehat{AB}) = 108°$ e $m(\widehat{BC}) = \frac{26π}{45}$ rad, então $m(\widehat{ABC}) =$ ____ $π$ rad.`,options:[String.raw`$\frac{53}{45}$`,String.raw`$\frac{14}{15}$`,String.raw`$\frac{56}{45}$`,String.raw`$\frac{28}{15}$`]},
    164010: {text:String.raw`Os pontos O e P são os centros de duas circunferências que possuem raios medindo, respectivamente, 8 cm e 3 cm, conforme a figura. Se $OP = 5\sqrt{37}$ cm e se $\overline{AB}$ é tangente a essas circunferências, em A e B, então $AB =$ ______ cm.`},
    164011: {text:String.raw`Uma circunferência de 5 cm de raio possui duas cordas $AB = 6$ cm e $BC = x$ cm. Se $\overline{AB}$ é perpendicular a $\overline{BC}$, então $x$ é igual a`},
    164012: {text:String.raw`Seja O o centro da circunferência que passa por A, B, C e D. Se $\angle COD = 120°$ e se $\overline{AC}$ passa por O, então $\angle ABD =$ _____.`},
    164013: {text:String.raw`A figura representa uma pista de corrida, onde $\widehat{BC}$, $\widehat{DA}$, $\widehat{NO}$ e $\widehat{PM}$ são semicircunferências e $AB = CD = MN = OP = 100$ m. A diferença entre as distâncias percorridas por uma pessoa que completa uma volta sobre a linha externa (M, N, O, P) e outra que completa uma volta sobre a linha interna (A, B, C, D) é de, aproximadamente, ____ m. Considere $π = 3{,}14$ e que as medidas indicadas na figura estão em metros.`},
    164014: {text:String.raw`Um jardim tem a forma da figura, sendo $\triangle ABC$ um triângulo retângulo em A e $\widehat{BC}$ um arco de diâmetro $\overline{BC}$. De acordo com as medidas dadas na figura e usando $π = 3{,}14$, a área desse jardim é ____ m².`},
    164015: {text:String.raw`Seja ABC um triângulo isósceles de base $BC = x$ cm. Se cada ângulo da base mede $40°$ e se o raio da circunferência circunscrita a esse triângulo mede 2,55 cm, o valor aproximado de $x$ é ______. (Considere $\operatorname{sen} 80° = 0{,}98$.)`},
    164016: {text:String.raw`Na figura, o raio da circunferência de centro O é $\frac{25}{2}$ cm e a corda MP mede 10 cm. A medida, em centímetros, do segmento PQ é`,options:[String.raw`$\frac{25}{2}$`,'$10$',String.raw`$5\sqrt{21}$`,String.raw`$\sqrt{21}$`,String.raw`$2\sqrt{21}$`]},
    164017: {text:'Os centros de dois círculos distam 25 cm. Se os raios desses círculos medem 20 cm e 15 cm, a medida da corda comum a esses dois círculos é'},
    164018: {text:'Para fabricar uma mesa redonda que comporte 8 pessoas em sua volta, um projetista concluiu que essa mesa, para ser confortável, deverá considerar, para cada um dos ocupantes, um arco de circunferência com 62,8 cm de comprimento. O tampo redondo da mesa será obtido a partir de uma placa quadrada de madeira compensada. Adotando $π = 3{,}14$, a menor medida do lado dessa placa quadrada que permite obter esse tampo de mesa é'},
    164019: {text:'Foram construídos círculos concêntricos de raios 5 cm e 13 cm. Em seguida, foi construído um segmento de reta com maior comprimento possível, contido inteiramente na região interna ao círculo maior e externa ao menor. O valor do segmento é'},
    164020: {text:"Seja ABC um triângulo inscrito em uma circunferência de centro O. Sejam O′ e E o incentro do triângulo ABC e o ponto médio do arco BC que não contém o ponto A, respectivamente. Assinale a opção que apresenta a relação entre os segmentos EB, EO′ e EC.",options:["$EB = EO' = EC$","$EB < EO' = EC$","$EB > EO' > EC$","$EB = EO' > EC$","$EB < EO' < EC$"]},
    164021: {text:'Rafael está apreciando a vista da cidade de Curitiba numa roda-gigante, com raio de 10 m, que gira a uma taxa de uma volta a cada dois minutos. A velocidade vertical, em metros/minuto, na qual Rafael está subindo, quando seu assento estiver 16 metros acima do nível do solo, será de',options:['$2π$','$4π$','$8π$','$16π$','$32π$']},
    164022: {text:String.raw`Seja $\overline{AB}$ o lado de um decágono inscrito em um círculo de raio $R$ e centro O. Considere o ponto C sobre a reta que passa por A e B tal que $\overline{AC} = R$. O lado $\overline{OC}$ do triângulo de vértices O, A e C mede`,options:[String.raw`$R\sqrt{2-\sqrt{5}}$`,String.raw`$\frac{R}{2}\sqrt{5-\sqrt{2}}$`,String.raw`$\frac{R}{2}\sqrt{10-2\sqrt{5}}$`,String.raw`$\frac{\sqrt{5}-1}{2}R$`,String.raw`$\frac{R}{4}(\sqrt{5}+1)$`]},
    164023: {text:'Rola-se, sem deslizar, uma roda de 1 metro de diâmetro, por um percurso reto de 30 centímetros, em uma superfície plana. O ângulo central de giro da roda, em radianos, é'},
    164024: {text:String.raw`Um triângulo inscrito em um círculo possui um lado de medida $2\sqrt[4]{3}$ oposto ao ângulo de $15°$. O produto do apótema do hexágono regular pelo apótema do triângulo equilátero inscritos nesse círculo é igual a:`,options:[String.raw`$3(\sqrt{3}+2)$`,String.raw`$4(2\sqrt{3}+2)$`,String.raw`$\sqrt{8\sqrt{3}+12}$`,String.raw`$\sqrt{2}(2\sqrt{3}+3)$`,String.raw`$6(\sqrt{2}+1)$`]},
    164025: {text:'Dois amigos se encontram em dois portões de acesso, pontos A e B, de um ginásio com um muro circular de raio 12 metros, conforme figura ilustrativa abaixo.\n\nAquele que se encontra no portão A caminha, na área externa ao muro, $x$ metros, numa trajetória retilínea, até avistar o ponto B. Sabendo que o comprimento do arco AB é de $3π$ metros, o menor valor de $x$, em metros, vale:',options:[String.raw`$12\sqrt{2}+12$`,String.raw`$12\sqrt{2}-12$`,String.raw`$12\sqrt{2}$`,String.raw`$12\sqrt{2-\sqrt{2}}$`,String.raw`$12\sqrt{2+\sqrt{2}}$`]},
    164026: {text:String.raw`Seja o triângulo ABC, retângulo em B, com $AB = 8\sqrt{2}$ e $BC = 6\sqrt{2}$. Sabendo que CD é bissetriz de $\angle ACB$, D é centro da circunferência de raio BD e $x$ é a razão $\frac{EF}{CE}$, podemos afirmar que $x$ é tal que`},
    164027: {text:String.raw`Sejam uma circunferência C com centro O e raio $R$, e uma reta $r$ tangente a C no ponto T. Traça-se o diâmetro AB oblíquo a $r$. A projeção de AB sobre $r$ é o segmento PQ. Sabendo que a razão entre OQ e o raio $R$ é $\frac{\sqrt{7}}{2}$, o ângulo, em radianos, entre AB e PQ é`,options:[String.raw`$\frac{π}{4}$`,String.raw`$\frac{π}{6}$`,String.raw`$\frac{5π}{18}$`,String.raw`$\frac{π}{3}$`,String.raw`$\frac{7π}{18}$`]},
    164028: {text:String.raw`Um triângulo ABC tem lados com medidas $a = \frac{\sqrt{3}}{2}$ cm, $b = 1$ cm e $c = \frac{1}{2}$ cm. Uma circunferência é tangente ao lado $a$ e também aos prolongamentos dos outros dois lados do triângulo, ou seja, a circunferência é ex-inscrita ao triângulo. Então, o raio da circunferência, em cm, é igual a`,options:[String.raw`$\frac{\sqrt{3}+1}{4}$`,String.raw`$\frac{\sqrt{3}}{4}$`,String.raw`$\frac{\sqrt{3}+1}{3}$`,String.raw`$\frac{\sqrt{3}}{2}$`,String.raw`$\frac{\sqrt{3}+2}{4}$`]},
    164029: {text:String.raw`Uma reta $r$ tangencia uma circunferência num ponto B e intercepta uma reta $s$ num ponto A exterior à circunferência. A reta $s$ passa pelo centro desta circunferência e a intercepta num ponto C, tal que o ângulo $\angle ABC$ seja obtuso. Então o ângulo $\angle CAB$ é igual a`,options:[String.raw`$\frac{1}{2}\angle ABC$`,String.raw`$2\angle ABC-π$`,String.raw`$\frac{3π}{2}-2\angle ABC$`,String.raw`$\angle ABC-\frac{π}{2}$`,String.raw`$\frac{2}{3}\angle ABC$`]},
    164030: {text:String.raw`Seja $P_n$ um polígono convexo regular de $n$ lados, com $n ≥ 3$. Considere as afirmações a seguir:
I. $P_n$ é inscritível numa circunferência.
II. $P_n$ é circunscritível a uma circunferência.
III. Se $ℓ_n$ é o comprimento de um lado de $P_n$ e $a_n$ é o comprimento de um apótema de $P_n$, então $\frac{a_n}{ℓ_n} ≤ 1$ para todo $n ≥ 3$.
É (são) verdadeira(s)`},
    164031: {text:'Seis circunferências de raio 5 cm são tangentes entre si duas a duas e seus centros são vértices de um hexágono regular, conforme a figura abaixo. O comprimento de uma correia tensionada que envolve externamente as seis circunferências mede, em cm,',options:['$18 + 3π$','$30 + 10π$','$18 + 6π$','$60 + 10π$','$36 + 6π$']},
    164032: {text:String.raw`Os lados de um triângulo de vértices A, B e C medem $AB = 3$ cm, $BC = 7$ cm e $CA = 8$ cm. A circunferência inscrita no triângulo tangencia o lado $\overline{AB}$ no ponto N e o lado $\overline{CA}$ no ponto K. Então, o comprimento do segmento $\overline{NK}$, em cm, é`,options:['$2$',String.raw`$2\sqrt{2}$`,'$3$',String.raw`$2\sqrt{3}$`,String.raw`$\frac{7}{2}$`]},
    164033: {text:String.raw`Seja A um ponto externo a uma circunferência $λ$ de centro O e raio $r$. Considere uma reta passando por A e secante a $λ$ nos pontos C e D tal que o segmento $\overline{AC}$ é externo a $λ$ e tem comprimento igual a $r$. Seja B o ponto de $λ$ tal que O pertence ao segmento $\overline{AB}$. Se o ângulo $\angle BAD$ mede $10°$, então a medida do ângulo $\angle BOD$ é igual a`},
    164034: {text:String.raw`Considere um triângulo ABC tal que $m(\overline{AB}) = 14$, $\cos(\angle BAC) = \frac{3}{5}$ e $\cos(\angle ABC) = \frac{5}{13}$. Então, o raio da circunferência inscrita ao triângulo é igual a:
Obs.: $\angle AOB$ é o ângulo formado pelos segmentos $\overline{OA}$ e $\overline{OB}$, com vértice no ponto O.`,options:['$2$',String.raw`$2\sqrt{2}$`,'$3$','$4$',String.raw`$4\sqrt{2}$`]},
    164035: {text:String.raw`Seja T um triângulo de vértices A, B e C com $m(\overline{AB}) = 2\sqrt{5}$ e $m(\overline{BC}) = 6$. Sabendo que $\angle ABC$ é agudo e T é inscritível em uma circunferência de raio $R = 5$, podemos afirmar que:
Obs.: $m(\overline{AB})$ é a medida do segmento $\overline{AB}$.`,options:[String.raw`$m(\overline{AC}) = \frac{\sqrt{5}}{5}$`,String.raw`$m(\overline{AC}) = \frac{2\sqrt{5}}{5}$`,String.raw`$m(\overline{AC}) = \frac{4\sqrt{5}}{5}$`,String.raw`$m(\overline{AC}) = \frac{8\sqrt{5}}{5}$`,String.raw`$m(\overline{AC}) = \frac{14\sqrt{5}}{5}$`]}
  };
  for (const [id, patch] of Object.entries(fixes)) {
    const q=QUESTIONS.find(q=>q.id===Number(id));
    if(!q)throw new Error(`Questão ausente na revisão: ${id}`);
    Object.assign(q,patch,{transcriptionReviewed:true});
    delete q.originalExcerpt;
    delete q.originalExcerptWidth;
    delete q.originalExcerptHeight;
  }
})();
