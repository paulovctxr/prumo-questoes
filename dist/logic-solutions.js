'use strict';
// Resoluções revisadas da matéria Noções de lógica.
// O gabarito original é preservado; quando a expressão impressa apresenta
// inconsistência, a observação editorial é exibida junto da resolução.
(() => {
  const solutions = {
    26001: [
      'Defina $A$: “Carolina é alta”, $B$: “Bruno é baixo” e $R$: “Renan é calvo”. A frase dada é $A\\lor\\neg B\\lor R$.',
      'Uma disjunção só é falsa quando todas as parcelas são falsas. Portanto, $A=F$, $\\neg B=F$ e $R=F$. Assim, $B=V$ e $\\neg R=V$.',
      'Na alternativa C, $A\\to B$ é verdadeira porque $A$ é falsa. Além disso, $\\neg B\\to\\neg R$ é verdadeira porque $\\neg B$ é falsa. Logo, a alternativa C é verdadeira.'
    ],
    26002: [
      'A frase “Todo nauta é corajoso e sonhador” pode ser escrita como $\\forall x\\,[N(x)\\to(C(x)\\land S(x))]$.',
      'Negamos o quantificador universal: $\\neg\\forall x\\,P(x)\\equiv\\exists x\\,\\neg P(x)$. Portanto, deve existir pelo menos um nauta que não satisfaça a condição.',
      'Pela lei de De Morgan, $\\neg(C\\land S)\\equiv\\neg C\\lor\\neg S$. Assim, a negação é “Existe nauta que não é corajoso ou não é sonhador”, correspondente à alternativa D.'
    ],
    26003: [
      'Sejam $F$: “faz frio”, $C$: “chove”, $L$: “Luiz vai ao futebol” e $P$: “Paula vai ao futebol”. As premissas são $(\\neg F\\lor L)\\to P$ e $(\\text{noite}\\land\\neg C)\\to L$.',
      'Como Paula não foi ao futebol, $P=F$. Para a primeira condicional continuar verdadeira com consequente falso, o antecedente também precisa ser falso: $\\neg F\\lor L=F$. Logo, $F=V$ e $L=F$.',
      'Na segunda condicional, a noite é verdadeira e $L$ é falso. Então $\\neg C$ precisa ser falso; portanto, $C=V$. Concluímos: fez frio, Luiz não foi ao futebol e choveu. Alternativa C.'
    ],
    26004: [
      'Há 13 pessoas e apenas 12 meses possíveis para os aniversários.',
      'Pelo princípio da casa dos pombos, ao distribuir 13 aniversários em 12 meses, pelo menos dois aniversários caem no mesmo mês.',
      'As outras afirmações dependem de informações não fornecidas sobre altura, sexo ou dia do nascimento. Logo, a única necessariamente verdadeira é a alternativa C.'
    ],
    26005: [
      'Defina $p$: “Mateus é alto” e $q$: “Mateus é elegante”. A afirmação (1), “alto e elegante”, é $p\\land q$.',
      'A afirmação (2), “alto ou baixo e elegante”, é representada na tabela por $p\\lor(\\neg p\\land q)$, pois “baixo” é a negação de “alto”.',
      'A afirmação (3), “não é alto nem elegante”, é $\\neg p\\land\\neg q$. Assim, as três expressões aparecem, na ordem, como 2, 1 e 3. Alternativa A.'
    ],
    26006: [
      'A proposição $p\\to q$ é uma condicional: o primeiro enunciado é a hipótese e o segundo é a conclusão.',
      'Como $p$ significa “Matheus é professor” e $q$ significa “Paulo é locutor”, a leitura correta é “Se Matheus é professor, então Paulo é locutor”.',
      'Essa formulação corresponde à alternativa B.'
    ],
    26007: [
      'Seja $p$: “Joana é magra” e $q$: “Gerusa é baixa”. A alternativa A tem a forma $p\\to(p\\lor q)$.',
      'Se $p$ for verdadeira, então $p\\lor q$ também será verdadeira, pois uma disjunção já é verdadeira quando uma de suas parcelas é verdadeira.',
      'Se $p$ for falsa, a condicional será verdadeira por definição. Portanto, ela é verdadeira em todas as combinações: é uma tautologia. Alternativa A.'
    ],
    26008: [
      'Defina $J$: “João estuda” e $C$: “faz calor”. A frase original é $J\\leftrightarrow\\neg C$.',
      'Uma bicondicional é falsa quando seus dois lados têm valores diferentes. Portanto, sua negação ocorre quando $J$ e $\\neg C$ são diferentes.',
      'Algebricamente, $\\neg(J\\leftrightarrow\\neg C)\\equiv(J\\land C)\\lor(\\neg J\\land\\neg C)$. Isso é o “ou” exclusivo entre $J$ e $\\neg C$, descrito pela alternativa E.'
    ],
    26009: [
      'Temos $P:A\\leftrightarrow B$, $Q:A\\to B$ e $R:B\\to A$.',
      'Usando $A\\to B\\equiv\\neg A\\lor B$ e $B\\to A\\equiv\\neg B\\lor A$, a expressão $S$ fica $S=(A\\to B)\\land(B\\to A)$.',
      'Uma bicondicional é exatamente a conjunção das duas condicionais nos sentidos opostos. Portanto, $S\\equiv A\\leftrightarrow B\\equiv P$. Alternativa A.'
    ],
    26010: [
      'Uma contradição tem valor F em todas as linhas. A negação dela é uma tautologia; a negação novamente volta a ser F. Portanto, a primeira afirmação é falsa.',
      'Uma contingência não é sempre verdadeira nem sempre falsa. Logo, a segunda afirmação também é falsa.',
      'A disjunção de uma tautologia com qualquer proposição continua sendo uma tautologia, não uma contingência. A terceira afirmação é falsa.',
      'Para $(A\\to B)\\to(B\\to A)$, tomando $A=F,B=V$ obtemos $V\\to F=F$; tomando $A=V,B=F$ obtemos $F\\to V=V$. Ela assume valores diferentes e é uma contingência. A sequência é F, F, F e V: alternativa D.'
    ],
    26011: [
      'Na proposição (1), $p\\to q$ é logicamente equivalente a $\\neg p\\lor q$. Portanto, a bicondicional entre essas duas expressões é sempre verdadeira: I é verdadeira.',
      'A proposição (2), $(p\\land q)\\to(p\\lor q)$, é uma tautologia: quando $p\\land q$ é verdadeira, $p\\lor q$ também é; quando o antecedente é falso, a condicional é verdadeira. Assim, II é falsa.',
      'Em (3), escreva $X=p\\lor q$. Então $X\\to\\neg X$ é verdadeira quando $X$ é falsa e falsa quando $X$ é verdadeira. Portanto, é uma contingência: III é verdadeira.',
      'Somente I e III são verdadeiras. Alternativa C.'
    ],
    26012: [
      'A proposição da última coluna é $E=((p\\to q)\\lor r)\\leftrightarrow p$. Uma bicondicional vale V quando os dois lados têm o mesmo valor.',
      'Na segunda linha incompleta, $p=V,q=V,r=F$. Então $p\\to q=V$, $(p\\to q)\\lor r=V$ e $V\\leftrightarrow V=V$.',
      'Na terceira linha, $p=V,q=F,r=V$. Temos $p\\to q=F$, mas $F\\lor V=V$; logo, $V\\leftrightarrow V=V$.',
      'Na sexta linha, $p=F,q=V,r=F$: o primeiro lado vale V e $V\\leftrightarrow F=F$. Na sétima, $p=F,q=F,r=V$: novamente o primeiro lado vale V e o resultado é F.',
      'De cima para baixo, os valores que faltam são V, V, F e F. Alternativa D.'
    ],
    26013: [
      'Use $P\\to Q\\equiv\\neg P\\lor Q$. A expressão da alternativa E é $(P\\to\\neg Q)\\lor(\\neg Q\\to P)$.',
      'Substituindo as implicações, obtemos $(\\neg P\\lor\\neg Q)\\lor(Q\\lor P)$.',
      'Reorganizando, aparecem os pares $P\\lor\\neg P$ e $Q\\lor\\neg Q$, ambos sempre verdadeiros. Portanto, a expressão é uma tautologia. Alternativa E.'
    ],
    26014: [
      'Defina $A$: “não comparece”, $J$: “não justifica” e $M$: “paga a multa”. A frase é a condicional $(A\\land J)\\to M$.',
      'A contrapositiva de $X\\to Y$ é $\\neg Y\\to\\neg X$. Assim, obtemos $\\neg M\\to\\neg(A\\land J)$.',
      'Pela lei de De Morgan, $\\neg(A\\land J)\\equiv\\neg A\\lor\\neg J$. Isso significa “compareceu ou justificou a falta”. Alternativa E.'
    ],
    26015: [
      'Se $A$ é uma contradição, então $A=F$. A condicional $A\\to B$ fica $F\\to B$, que é sempre V. A primeira afirmação é verdadeira.',
      'Se $B$ é uma contradição, então $B=F$ e $A\\to B\\equiv\\neg A$. Para uma proposição $A$ variável, isso pode ser V ou F; portanto, é uma contingência. A segunda afirmação é verdadeira.',
      'Se $A$ é uma tautologia, $A=V$ e $A\\to B\\equiv B$. Como $B$ não foi definido como tautologia, não é correto afirmar que o resultado é sempre uma tautologia. A terceira é falsa.',
      'Se $B$ é uma tautologia, $B=V$ e $A\\to B$ é sempre V. Logo, é uma tautologia, não uma contingência. A quarta é falsa. Sequência: V, V, F, F. Alternativa D.'
    ],
    26016: [
      'Uma contradição precisa ser falsa para todas as combinações de valores de $P$ e $Q$.',
      'As alternativas B, D e E são tautologias, pois uma conjunção implica sua própria disjunção, e $P\\to(P\\lor Q)$ também é sempre verdadeira. A alternativa A simplifica para $Q$, portanto é contingente.',
      'Na alternativa C, como ela está impressa, tome $P=V,Q=V$: $(P\\lor Q)=V$ e $(\\neg P\\lor\\neg Q)=F$, então a bicondicional é F. Agora tome $P=V,Q=F$: os dois lados valem V, então a bicondicional é V.',
      'Logo, a alternativa C varia entre V e F e é uma contingência, não uma contradição. O gabarito da apostila indica C, mas a expressão impressa precisa de revisão editorial; não há alternativa que seja contradição exatamente como transcrita.'
    ],
    26017: [
      'Analise a alternativa B: $(p\\land r)\\to(\\neg q\\lor r)$.',
      'Quando o antecedente $p\\land r$ é verdadeiro, necessariamente $r$ é verdadeiro. Portanto, a disjunção $\\neg q\\lor r$ também é verdadeira, independentemente do valor de $q$.',
      'Quando o antecedente é falso, a implicação também é verdadeira. Assim, B é verdadeira em todas as linhas e é uma tautologia.'
    ],
    26018: [
      'Na alternativa B, a proposição é $(p\\land q)\\to(p\\leftrightarrow q)$.',
      'Se $p\\land q$ for verdadeira, então $p=V$ e $q=V$, fazendo $p\\leftrightarrow q$ ser verdadeira.',
      'Se $p\\land q$ for falsa, a condicional já é verdadeira. Portanto, a proposição é verdadeira em todas as possibilidades: alternativa B.'
    ],
    26019: [
      'As alternativas A, B, C e D são tautologias: respectivamente, usam a lei do terceiro excluído, uma implicação que só é ativada com $p=q=V$, e implicações em que o consequente contém o antecedente.',
      'Na alternativa E, considere $E=(p\\to q)\\land(p\\lor q)$. Para $p=F,q=F$, temos $p\\to q=V$, mas $p\\lor q=F$; logo, $E=F$.',
      'Para $p=F,q=V$, os dois fatores são V e $E=V$. Como a expressão pode ser V ou F, ela não é tautologia. Alternativa E.'
    ],
    26020: [
      'A primeira equivalência é a lei de De Morgan: $\\neg(p\\lor q)\\equiv\\neg p\\land\\neg q$. Portanto, é verdadeira.',
      'A segunda é a propriedade distributiva: $p\\land(q\\lor r)\\equiv(p\\land q)\\lor(p\\land r)$. Portanto, é verdadeira.',
      'A terceira não é uma equivalência geral. Por exemplo, com $p=V,q=V$, o lado esquerdo vale V e $\\neg p$ vale F.',
      'Na quarta, a absorção dá $p\\land(p\\lor q)\\equiv p$, e não $q$. Por exemplo, com $p=V,q=F$, o lado esquerdo é V e o direito é F. A sequência é V, V, F e F: alternativa A.'
    ]
  };

  for (const [id, steps] of Object.entries(solutions)) {
    const question = QUESTIONS.find(item => item.id === Number(id));
    if (question) {
      question.steps = steps;
      question.solution = 'Texto';
    }
  }

  const review = QUESTIONS.find(item => item.id === 26016);
  if (review) review.solutionNote = 'Conferência editorial: o gabarito da apostila indica C, mas a expressão da alternativa C, como está impressa, é contingente. A questão precisa ser conferida no original antes de ser tratada como gabarito definitivo.';
})();
