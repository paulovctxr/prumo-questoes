(function () {
  const novos = [
    ['Conjuntos','Teoria dos conjuntos','Difícil','Se n(A)=18, n(B)=23 e n(A∪B)=31, quantos subconjuntos próprios não vazios possui A∩B?', ['31','63','127','255','511'], 1, ['n(A∩B)=18+23−31=10. O número de subconjuntos próprios não vazios é $2^{10}-2=1022$.'], 'PRUMO — questão inédita'],
    ['Polinômios','Identidades algébricas','Difícil','Se x+y=5 e xy=3, qual é o valor de $x^4+y^4$?', ['529','553','601','625','697'], 1, ['x²+y²=25−6=19; x⁴+y⁴=19²−2·9=343.'], 'PRUMO — questão inédita'],
    ['Polinômios','Divisão polinomial','Difícil','O resto da divisão de $P(x)=x^5-2x^3+ax+b$ por $x^2-1$ é $3x-4$. Determine $a+b$.', ['−9','−7','−5','−3','1'], 2, ['Como $x^2=1$, $P(x)\\equiv(a-1)x+b$. Logo $a=4$ e $b=-4$.'], 'PRUMO — questão inédita'],
    ['Equações','Equação do 1º grau','Difícil','A soma das raízes reais de |2x−3|+|x+1|=7 é:', ['−1','0','1','2','3'], 3, ['Quebrando em x<−1, −1≤x≤3/2 e x>3/2, obtêm-se x=−5/3 e x=3; soma 4/3.'], 'PRUMO — questão inédita'],
    ['Funções','Função composta','Difícil','Se f(x)=x²−2x e g(x)=1/(x−1), o domínio de f∘g é:', ['R','R\{0}','R\{1}','R\{2}','R\{1,2}'], 4, ['É preciso x≠1 e g(x)≠1; portanto x≠1 e x≠2.'], 'PRUMO — questão inédita'],
    ['Funções','Função quadrática','Difícil','O menor valor de x²−(m+2)x+m, para m real, é igual a −9. O número de valores possíveis de m é:', ['0','1','2','3','infinitos'], 2, ['O mínimo é −(m+2)²/4+m=−9; daí m²−4m−32=0, com duas raízes.'], 'PRUMO — questão inédita'],
    ['Progressões','Progressão aritmética','Difícil','Em uma PA, a soma dos n primeiros termos é $S_n=3n^2-n$. O 20º termo é:', ['109','111','113','115','117'], 3, ['$a_n=S_n-S_{n-1}=6n-4$; $a_{20}=116$.'], 'PRUMO — questão inédita'],
    ['Progressões','Progressão geométrica','Difícil','Uma PG positiva tem $a_2+a_4=30$ e $a_3=12$. A razão é:', ['1/3','1/2','2','3','4'], 3, ['$a_2=a_3/q$ e $a_4=12q$; então 12(q+1/q)=30, logo q=2 ou 1/2.'], 'PRUMO — questão inédita'],
    ['Inequações','Inequação racional','Difícil','O conjunto solução de (x−2)/(x²−5x+6)≤0 é:', ['(−∞,2)','(2,3)','[2,3)','(−∞,2)∪(2,3)','[2,3]'], 3, ['Fatorando o denominador, o sinal dá (−∞,2)∪(2,3); x=2 é permitido e x=3 proibido.'], 'PRUMO — questão inédita'],
    ['Radicais','Equação irracional','Difícil','A soma das raízes reais de √(x+4)=x−2 é:', ['2','3','4','5','6'], 3, ['Exige x≥2; elevando ao quadrado, x+4=x²−4x+4, então x(x−5)=0. Só x=5 serve.'], 'PRUMO — questão inédita'],
    ['Logaritmos','Equações logarítmicas','Difícil','Se $\\log_2(x-1)+\\log_2(x+3)=3$, então x é:', ['−1+2√3','−1+2√2','1+2√2','3','5'], 2, ['(x−1)(x+3)=8; x²+2x−11=0. A raiz admissível é −1+2√3.'], 'PRUMO — questão inédita'],
    ['Exponenciais','Equações exponenciais','Difícil','O número de soluções reais de $4^x-5\\cdot 2^x+4=0$ é:', ['0','1','2','3','4'], 2, ['Pondo $t=2^x>0$: t²−5t+4=0, t=1 ou 4; logo duas soluções.'], 'PRUMO — questão inédita'],
    ['Combinatória','Princípio multiplicativo','Difícil','Quantas senhas de 6 caracteres distintos, formadas por 4 letras e 2 algarismos, podem ser feitas usando 8 letras e 5 algarismos?', ['67200','100800','201600','403200','806400'], 3, ['Escolha e ordene: C(8,4)C(5,2)·6!=403200.'], 'PRUMO — questão inédita'],
    ['Binômio de Newton','Coeficientes','Difícil','O coeficiente de $x^4$ em $(1+x)^6(1-x)^4$ é:', ['−20','−10','0','10','20'], 2, ['Somam-se $C(6,k)C(4,4-k)(-1)^{4-k}$; o resultado é 0.'], 'PRUMO — questão inédita'],
    ['Matrizes','Determinantes','Difícil','Se A é 3×3, det(A)=−2 e $B=2A^{T}$, então det(B) vale:', ['−4','−8','−16','−32','32'], 3, ['$\\det(2A^{T})=2^3\\det(A)=8(-2)=-16$.'], 'PRUMO — questão inédita'],
    ['Sistemas','Sistemas lineares','Difícil','Para qual valor de k o sistema x+y+z=1, x+2y+3z=2, x+3y+kz=4 não possui solução?', ['0','1','2','3','4'], 3, ['Subtraindo as duas primeiras: y+2z=1; da terceira menos a primeira: 2y+(k−1)z=3. Incompatível quando k=−3.'], 'PRUMO — questão inédita'],
    ['Números complexos','Forma algébrica','Difícil','Se z=(1+i)/(1−i), então $z^8$ é:', ['−1','i','1−i','1','−i'], 3, ['z=i; portanto $z^8=i^8=1$.'], 'PRUMO — questão inédita'],
    ['Módulo','Equações modulares','Difícil','Quantas soluções inteiras possui |x−1|+|x−5|=10?', ['0','1','2','3','4'], 2, ['Fora do intervalo, a soma é 2x−6 ou 14−2x; resultam x=8 e x=−2.'], 'PRUMO — questão inédita'],
    ['Sequências','Recorrências','Difícil','Defina $a_1=1$ e $a_{n+1}=2a_n+3$. O valor de $a_5$ é:', ['31','43','47','49','63'], 3, ['$a_2=5$, $a_3=13$, $a_4=29$, $a_5=61$.'], 'PRUMO — questão inédita'],
    ['Inequações','Inequação polinomial','Difícil','O número de inteiros x que satisfazem (x−1)(x−2)(x−4)<0 e −3≤x≤6 é:', ['1','2','3','4','5'], 2, ['O sinal é negativo em (−∞,1)∪(2,4). Inteiros no intervalo: −3,−2,−1,0 e 3, total 5.'], 'PRUMO — questão inédita']
  ];
  const base = QUESTIONS.length;
  novos.forEach((q, i) => QUESTIONS.push({id: 900000 + i, topic:q[0], sub:q[1], difficulty:q[2], text:q[3], options:q[4], answer:q[5], steps:q[6], type:'Múltipla escolha', institution:"Inéditas d'Aba Azul", exam:"Inéditas d'Aba Azul", year:2026, solution:'Texto', originalExcerpt:null}));
  if (typeof render === 'function') render();
})();
