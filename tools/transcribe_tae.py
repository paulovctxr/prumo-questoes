"""Convert the prepared PDF text into editable bank records.

This is a migration helper.  It reads the previously inventoried catalog and
the existing detail records (only to learn which exercises are multiple
choice), then writes a text-only transcription source.  No page image or
printed answer page is copied to the result.
"""
import argparse
import json
import re
from pathlib import Path


GLYPHS = {
    '\uf0a1': 'ℝ', '\uf0a2': 'ℤ', '\uf0a5': 'ℕ', '\uf0c6': '∅',
    '\uf8f1': '', '\uf8f4': '', '\uf8ee': '[', '\uf8f9': ']', '\uf8ef': '',
    '\uf8f0': '', '\uf8fa': '', '\uf8fb': '',
    '\uf8eb': '(', '\uf8ec': '', '\uf8ed': '', '\uf8f6': ')',
    '\uf8f7': '', '\uf8f8': '', '\uf8f2': '{', '\uf8f3': '',
    '\uf8fc': '{', '\uf8fd': '', '\uf8fe': '}', '\uf055': '∪',
    '\uf056': '⊙', '\uf057': '⊗', '\uf04c': '…', '\uf0a4': 'ℚ',
}
SUPERSCRIPT = str.maketrans('0123456789-+', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺')
LABEL = re.compile(r'(?im)(?<![\w])\(?([a-e])\)\s*')


MANUAL = {
    '48:13': {
        'text': 'Sabendo que $a$, $p$ e $q$ são constantes diferentes de zero, para que $x^3+px+q$ seja divisível por $(x-a)^2$, devemos verificar qual relação?',
        'options': ['$\\frac{p^3}{4}-\\frac{q^2}{27}=0$', '$\\frac{p^3}{4}+\\frac{q^2}{27}=0$', '$\\frac{p^2}{27}+\\frac{q^3}{4}=0$', '$\\frac{p^2}{27}-\\frac{q^3}{4}=0$', '$\\frac{p^3}{27}+\\frac{q^2}{4}=0$'],
    },
    '142:10': {
        'text': 'O salário de Ana é R$ 1.200,00 mais uma comissão de 30% do valor de suas vendas. Qual função representa o salário $S$ de Ana em função do valor $x$ dos produtos vendidos?',
        'options': ['$S(x)=1200x$', '$S(x)=\\frac{3}{10}\\cdot1200+x$', '$S(x)=\\frac{3}{10}x+1200$', '$S(x)=(1200+x)\\cdot\\frac{3}{10}$'],
    },
    '176:19': {
        'text': 'Se o sistema $\\frac{xy}{x+y}=a$, $\\frac{xz}{x+z}=b$ e $\\frac{yz}{y+z}=c$, com $abc\\ne0$, tiver solução, qual será o valor de $x$?',
        'options': ['$\\frac{abc}{ab+bc+ca}$', '$\\frac{2abc}{ab+bc+ca}$', '$\\frac{2abc}{ab+ac-bc}$', '$\\frac{2abc}{ab+bc-ac}$', '$\\frac{2abc}{ac+bc-ab}$'],
    },
    '197:1': {
        'text': 'Se $x+2\\ge x^2+3$, com $x\\in\\mathbb{R}_+$, é correto afirmar que:',
        'options': ['$\\frac1{x+2}\\ge\\frac1{x^2+3}$', '$\\frac1{x+2}\\le\\frac1{x^2-3}$', '$x<1$', 'Nenhuma das respostas anteriores.'],
    },
    '197:3': {
        'text': 'Das afirmações abaixo, qual é certamente verdadeira?',
        'options': ['$\\frac{3+5+8}{3}\\ge\\sqrt[3]{3\\cdot5\\cdot8}$', '$\\frac{3+5+7}{3}\\le\\sqrt[3]{3\\cdot5\\cdot7}$', '$\\frac{3+5+7}{3}>\\sqrt[3]{3\\cdot5\\cdot7}$', '$\\frac{3+5+7}{3}<\\sqrt[3]{3\\cdot5\\cdot7}$'],
    },
    '231:33': {
        'text': '(EPCAR 2021) Sejam $a$ e $b$, com $\\{a,b\\}\\subset\\mathbb{R}$, as raízes da equação $x^2+2\\sqrt3x+1=0$. A expressão $\\left[\\left(\\frac1{a+b}\\right)^{-ab}\\right]^{a^2+b^2}$ é igual a:',
        'options': ['$12^2$', '$12^3$', '$12^5$', '$12^4$'],
    },
    '272:22': {
        'text': 'Sejam $a$, $b$ e $c$ constantes reais, com $a\\ne0$, formando, nessa ordem, uma progressão aritmética. A soma das raízes de $ax^2+bx+c=0$ é $-\\sqrt2$. Qual relação entre $b$ e $c$ é válida?',
        'options': ['$c=\\frac{b}{\\sqrt2}(\\sqrt2-1)$', '$c=b(2-\\sqrt2)$', '$c=b(\\sqrt2-1)$', '$c=b\\sqrt2$', '$c=\\frac b2(4-\\sqrt2)$'],
    },
    '272:27': {
        'text': 'Um professor elaborou com seus alunos o projeto de uma pista virtual para o percurso de aviões. A figura mostra a vista frontal da pista em um plano cartesiano, composta por três percursos em linha reta, $AB$, $OG$ e $LM$, e por duas curvas parabólicas: de $B$ até $O$, com vértice em $C$, e de $G$ até $L$, com vértice em $N$. Sabe-se que $DO=2$ e $F$ é ponto médio de $DO$; $EF=4$, $OH=2$, $GH=6$, $JL=2$, $AO=OL=5$ e $LM=2$. Os segmentos $CD$ e $KN$ são eixos de simetria das parábolas. Calcule $AB+DC+OS+OJ$.',
        'options': ['$\\frac{26}{3}$', '$\\frac{28}{3}$', '$\\frac{29}{3}$', '$\\frac{32}{3}$'],
    },
    '272:29': {
        'text': 'A figura apresenta medidas fictícias da aproximação de um saltador em relação ao solo. Considere que sua trajetória possa ser modelada por $f(x)=ax^2+bx+c$, cujo eixo das abscissas coincide com a Avenida Nações Unidas e cujo eixo das ordenadas contém o ponto da trajetória mais próximo da avenida. De acordo com as medidas indicadas na figura, qual é o coeficiente de $x^2$?',
        'options': ['$\\frac{22}{1521}$', '$\\frac{2}{117}$', '$\\frac{13}{1521}$', '$\\frac{13}{117}$'],
    },
    '272:30': {
        'text': 'Nos gráficos estão desenhadas uma parábola e uma reta que representam as funções reais $f(x)=ax^2+bx+c$ e $g(x)=dx+e$, respectivamente. Analisando os gráficos, qual afirmação é necessariamente verdadeira?',
        'options': ['$(a+e)c\\ge b$', '$-\\frac ed<-b$', '$abc+\\frac ed>0$', '$(-b+a)e>ac$'],
    },
    '309:23': {
        'text': 'O conjunto das soluções reais da equação $x^6-7x^2+\\sqrt6=0$ é igual a:',
        'options': ['$\\left\\{\\pm\\sqrt6,\\;\\pm\\sqrt{\\frac{\\sqrt{10}-\\sqrt6}{2}}\\right\\}$', '$\\left\\{\\pm\\sqrt[4]6,\\;\\pm\\sqrt{\\frac{\\sqrt{10}-\\sqrt6}{2}}\\right\\}$', '$\\left\\{\\pm\\sqrt[4]6,\\;\\pm\\sqrt{\\frac{\\sqrt{10}+\\sqrt6}{2}}\\right\\}$', '$\\left\\{\\pm\\sqrt6,\\;\\pm\\sqrt{\\frac{\\sqrt{10}+\\sqrt6}{2}}\\right\\}$', '$\\left\\{\\pm\\sqrt6,\\;\\pm\\sqrt[4]6\\right\\}$'],
    },
    '360:9': {
        'text': 'Sabendo que $a$, $p$ e $q$ são constantes diferentes de zero, para que $x^3+px+q$ seja divisível por $(x-a)^2$, devemos verificar qual relação?',
        'options': ['$\\frac{p^3}{4}-\\frac{q^2}{27}=0$', '$\\frac{p^3}{4}+\\frac{q^2}{27}=0$', '$\\frac{p^2}{27}+\\frac{q^3}{4}=0$', '$\\frac{p^2}{27}-\\frac{q^3}{4}=0$', '$\\frac{p^3}{27}+\\frac{q^2}{4}=0$'],
    },
    '360:16': {
        'text': 'Uma máquina mostra um número inteiro $x$ e tem duas teclas. A tecla A substitui o número por $2x+1$; a tecla B o substitui por $3x-1$. Se o visor mostra 5, qual é o maior número de dois algarismos que pode ser obtido ao apertar uma sequência dessas teclas?',
        'options': ['85', '87', '92', '95', '96'],
    },
    '360:29': {
        'text': 'Se $\\frac xa+\\frac yb+\\frac zc=1$ e $\\frac ax+\\frac by+\\frac cz=0$, qual é o valor de $\\frac{x^2}{a^2}+\\frac{y^2}{b^2}+\\frac{z^2}{c^2}$?',
        'options': ['0', '1', '2', '3', 'Nenhuma das respostas anteriores.'],
    },
    '106:11': {
        'text': 'Se $x$ e $y$ são números reais tais que $\\frac{x^2+y^2}{x^2-y^2}+\\frac{x^2-y^2}{x^2+y^2}=k$, calcule $\\frac{x^8+y^8}{x^8-y^8}+\\frac{x^8-y^8}{x^8+y^8}$.',
        'options': ['$\\frac{k^4+24k^2+16}{4k^3+16k}$', '$\\frac{k^4-24k^2-16}{4k^3-16k}$', '$\\frac{k^4+24k^2-16}{4k^3-16k}$', '$\\frac{k^4+24k^2-16}{4k^3+16k}$', '$\\frac{k^4-24k^2+16}{4k^3+16k}$'],
    },
    '106:15': {
        'text': 'Sendo $ab=cd$, racionalize o denominador de $\\frac1{\\sqrt a+\\sqrt b+\\sqrt c+\\sqrt d}$.',
        'options': ['$\\sqrt{abcd}$', '$a+b+c-d$', '$\\frac{\\sqrt a+\\sqrt b-\\sqrt c-\\sqrt d}{a+b-c-d}$', '$\\frac{\\sqrt a+\\sqrt b+\\sqrt c-\\sqrt d}{a+b-c+d}$', '$1$'],
    },
    '106:18': {
        'text': 'Desenvolva $\\frac{bc}{a(a^2-b^2)(a^2-c^2)}+\\frac{ac}{b(b^2-a^2)(b^2-c^2)}+\\frac{ab}{c(c^2-a^2)(c^2-b^2)}$.',
        'options': ['$abc$', '$\\frac1{abc}$', '$a^2b^2c^2$', '$\\frac1{a^2b^2c^2}$', '$ab-bc+ac$'],
    },
    '106:22': {
        'text': 'Se $\\frac{y}{x-z}=\\frac{x+y}{z}=\\frac{x}{y}$, para $x\\ne y\\ne z\\in\\mathbb{Z}_+^*$, qual é o valor de $\\frac xy$?',
        'options': ['$\\frac12$', '$\\frac35$', '$\\frac23$', '$\\frac53$', '$2$'],
    },
    '106:24': {
        'text': 'Simplifique $\\frac{\\sqrt{(\\frac{a+b}{2\\sqrt{ab}}-1)^{-1}}+\\sqrt{(\\frac{a+b}{2\\sqrt{ab}}+1)^{-1}}}{\\sqrt{(\\frac{a+b}{2\\sqrt{ab}}-1)^{-1}}-\\sqrt{(\\frac{a+b}{2\\sqrt{ab}}+1)^{-1}}}$, onde $0<b<a$.',
        'options': ['$\\frac{\\sqrt a}{b}$', '$\\frac{\\sqrt b}{a}$', '$\\frac{\\sqrt{ab}}a$', '$\\frac{\\sqrt{ab}}b$', '$ab$'],
    },
    '106:25': {
        'text': 'A expressão $\\frac{\\left[(\\sqrt[4]a+\\sqrt[4]b)^2-(\\sqrt[4]a-\\sqrt[4]b)^2\\right]^2-(16a+4b)}{4a-b}+\\frac{10\\sqrt a-3\\sqrt b}{2\\sqrt a+\\sqrt b}$ é equivalente a:',
        'options': ['$a-b$', '$a+b$', '$\\frac{\\sqrt b}{a}$', '$\\frac{\\sqrt a}{b}$', '$1$'],
    },
    '11:22': {
        'text': 'Sejam $U$ o conjunto das brasileiras, $A$ o conjunto das cariocas, $B$ o conjunto das morenas e $C$ o conjunto das mulheres de olhos azuis. Qual diagrama representa as mulheres morenas ou de olhos azuis que não são cariocas, reunidas com as mulheres cariocas que não são morenas nem têm olhos azuis?',
        'options': ['Diagrama A', 'Diagrama B', 'Diagrama C', 'Diagrama D', 'Diagrama E'],
    },
    '126:22': {
        'text': 'Para os racionais $x$ e $y$, define-se $x*y=2x+3y-8xy$. Determine o racional $a$ para o qual não existe racional $b$ tal que $a*b=0$.',
        'options': ['$\\frac18$', '$\\frac14$', '$\\frac38$', '$\\frac12$', '$\\frac32$'],
    },
    '126:24': {
        'text': 'Qual é a maior raiz de $(4x^2-9)-2(2x-3)+x(2x-3)=0$?',
        'options': ['$\\frac12$', '$2$', '$\\frac32$', '$\\frac13$', '$\\frac23$'],
    },
    '176:13': {
        'text': 'Ao resolvermos $\\frac2{x+y}+\\frac3{2x-y}=\\frac75$, encontramos como solução o par ordenado $(a,b)$. Qual é o valor de $2a+4b$?',
        'options': ['$12$', '$0$', '$\\frac13$', '$\\frac{20}3$', 'Nenhuma das respostas anteriores.'],
    },
    '197:20': {
        'text': 'Sendo $x$ real, qual é o valor mínimo de $\\frac{x+2}{\\sqrt{x^2+1}}$?',
        'options': ['$1$', '$\\frac32$', '$2$', '$\\frac52$', '$3$'],
    },
    '197:22': {
        'text': 'Se $0<x<1$, qual é o valor máximo de $x\\sqrt{1-x^2}$?',
        'options': ['$0$', '$1$', '$\\frac12$', '$\\frac14$', '$\\frac18$'],
    },
    '197:26': {
        'text': 'Se $5\\le a\\le10$ e $20\\le b\\le30$, qual é o valor máximo de $\\frac ab$?',
        'options': ['$\\frac15$', '$\\frac14$', '$\\frac13$', '$\\frac12$', '$\\frac23$'],
    },
    '216:20': {
        'text': 'Qual é o intervalo-solução de $(x+3)(x+2)(x-3)>(x+2)(x-1)(x+4)$?',
        'options': [']$-\\infty,-\\frac53$[', ']$-\\infty,-1$[', ']$-2,-\\frac53$[', ']$-\\frac53,+\\infty$[', ']$-1,2$['],
    },
    '272:16': {
        'text': 'Na figura, estão representados um sistema de eixos com origem $O$, o gráfico de $f(x)=ax^2+bx+c$ e o quadrado $OMNP$, com 16 unidades de área. O gráfico passa por $P$, por $N$ e pelo encontro das diagonais do quadrado. Calcule $a+b+c$.',
        'options': ['$\\frac12$', '$\\frac32$', '$\\frac52$', '$\\frac{\\sqrt2}{2}$', '$\\frac{5\\sqrt2}{2}$'],
    },
    '320:26': {
        'text': 'Os números reais positivos $a$ e $b$ satisfazem $a\\sqrt{a^2+2b^2}=b\\sqrt{9a^2-b^2}$. Qual é um valor possível para $\\frac ab$?',
        'options': ['$\\frac{5+2\\sqrt5}{2}$', '$\\frac{5+\\sqrt3}{2}$', '$\\frac{3+2\\sqrt3}{2}$', '$\\frac{3+\\sqrt3}{2}$', '$\\frac{3+\\sqrt5}{2}$'],
    },
    '360:27': {
        'text': 'Dois números reais não nulos $a$ e $b$ satisfazem $ab=a-b$. Qual dos valores abaixo pode ser igual a $\\frac ab-\\frac ba$?',
        'options': ['$-2$', '$-\\frac12$', '$\\frac13$', '$\\frac12$', '$2$'],
    },
    '360:49': {
        'text': 'A menor raiz de $ax^2+bx+c=0$, com $abc\\ne0$, é a média geométrica entre $m$ e a maior raiz. A maior raiz é a média geométrica entre $n$ e a menor raiz. Qual expressão representa $m+n$?',
        'options': ['$\\frac{3abc-b^3}{a^2c}$', '$\\frac{3abc+b^3}{a^2c}$', '$\\frac{3abc-b^3}{c^2a}$', '$\\frac{abc+b^3}{c^2a}$', '$\\frac{abc-b^3}{a^2c}$'],
    },
    '37:11': {
        'text': 'Se $\\sqrt{x^2+x+y}=10$ e $x+\\sqrt{y^2-y}=12$, qual é o valor de $x+y$?',
        'options': ['$-2$', '$2$', '$\\frac{18}{5}$', '$\\frac23$', '$22$'],
    },
    '37:24': {
        'text': 'Qual é o conjunto-solução de $\\left|\\frac{2x+1}{x-3}\\right|>3$?',
        'options': [']$\\frac85,3$[ $\\cup$ ]$3,+\\infty$[', ']$3,10$[ $\\cup$ ]$10,+\\infty$[', ']$-\\infty,\\frac85$[ $\\cup$ ]$3,10$[', ']$\\frac85,3$[ $\\cup$ ]$3,10$[', ']$\\frac85,3$[ $\\cup$ ]$10,+\\infty$['],
    },
    '73:12': {
        'text': 'Sejam $a$, $b$ e $c$ reais não nulos tais que $\\frac1{ab}+\\frac1{bc}+\\frac1{ac}=p$, $\\frac ab+\\frac ba+\\frac ac+\\frac ca+\\frac bc+\\frac cb=q$ e $ab+ac+bc=r$. A expressão $q^2+6q$ é sempre igual a:',
        'options': ['$\\frac{p^2r^2+9}{4}$', '$\\frac{p^2r^2-9p}{12}$', '$p^2r^2-9$', '$\\frac{p^2r^2-10}{4r}$', '$p^2r^2-12p$'],
    },
    '73:24': {
        'text': 'Se $(a^2+b^2)^3=(a^3+b^3)^2$ e $ab\\ne0$, qual é o valor de $\\frac ab+\\frac ba$?',
        'options': ['$1$', '$2$', '$\\frac12$', '$\\frac23$', '$\\frac32$'],
    },
    '89:29': {
        'text': 'Sendo $a$ e $b$ números reais e $a^4+2a^3b-3a^2b^2-4ab^3-b^4=0$, qual é um possível valor de $\\frac ab$?',
        'options': ['$\\frac{3-\\sqrt5}{2}$', '$\\frac{\\sqrt5-1}{2}$', '$-\\frac{\\sqrt5+1}{2}$', '$\\frac{\\sqrt5-3}{2}$', '$\\frac{\\sqrt5+3}{2}$'],
    },
    '272:32': {
        'text': '(CN 2019) As equações $ax+b=0$ e $ax^2+bx+c=0$, onde $a$, $b$ e $c$ são reais e $a\\ne0$, possuem uma única raiz comum. Sabendo que $m$ e $n$ são as raízes da equação do segundo grau, determine $m^{2018}+n^{2018}$.',
        'options': ['$\\left(\\frac cb\\right)^{2018}$', '$\\left(\\frac{ab}{c}\\right)^{2018}$', '$\\left(\\frac ca\\right)^{2018}$', '$\\left(\\frac{bc}{a}\\right)^{2018}$', '$\\left(\\frac ba\\right)^{2018}$'],
    },
}


def clean(value):
    for old, new in GLYPHS.items():
        value = value.replace(old, new)
    value = value.replace('\u2013', '−').replace('\u2014', '−')
    # In this PDF, isolated digits after a lower-case algebraic letter are
    # superscripts whose baselines were lost by text extraction.
    value = re.sub(r'\b([a-z])\s+(\d{1,4})\b',
                   lambda m: m[1] + m[2].translate(SUPERSCRIPT), value)
    value = re.sub(r'[ \t]+', ' ', value)
    value = re.sub(r' *\n *', '\n', value)
    value = re.sub(r'\n{3,}', '\n\n', value)
    return value.strip(' \n\t.;')


def option_sequence(text, count):
    matches = list(LABEL.finditer(text))
    candidates = []
    for index, match in enumerate(matches):
        if match[1].upper() != 'A':
            continue
        sequence = [match]
        for following in matches[index + 1:]:
            expected = chr(ord('A') + len(sequence))
            if following[1].upper() == expected:
                sequence.append(following)
                if len(sequence) == count:
                    candidates.append(sequence)
                    break
    return max(candidates, key=lambda sequence: sequence[0].start(), default=[])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=Path('dist/livro-algebra/catalog.json'))
    parser.add_argument('--details', type=Path, default=Path('dist/questoes-algebra'))
    parser.add_argument('--output', type=Path, default=Path('tools/tae-transcriptions.json'))
    args = parser.parse_args()
    if args.catalog.exists():
        catalog = json.loads(args.catalog.read_text())
        transcriptions = {}
        for question in catalog['questions']:
            key = question['id']
            detail_id = 1000000 + int(question['chapter']) * 1000 + question['number']
            detail = json.loads((args.details / f'{detail_id}.json').read_text())
            if key in MANUAL:
                transcriptions[key] = {**MANUAL[key], 'page': question['page']}
                continue
            raw = question['searchText']
            count = len(detail['options'])
            sequence = option_sequence(raw, count) if count else []
            if count and len(sequence) != count:
                raise ValueError(f'Alternatives require manual transcription: {key}')
            statement_end = sequence[0].start() if sequence else len(raw)
            statement = re.sub(r'^\s*\d+\s*\)\s*', '', raw[:statement_end], count=1)
            options = []
            for index, marker in enumerate(sequence):
                end = sequence[index + 1].start() if index + 1 < len(sequence) else len(raw)
                options.append(clean(raw[marker.end():end]))
            statement = re.sub(r'\n?\s*(EXERC[ÍI]CIOS AVANÇADOS|CAIU NOS ÚLTIMOS CONCURSOS).*$',
                               '', statement, flags=re.I | re.S)
            transcriptions[key] = {'text': clean(statement), 'options': options,
                                   'page': question['page']}
    else:
        # After the one-time migration, the editable transcription file is
        # authoritative. This branch applies later manual reviews without
        # requiring the removed full-page assets.
        transcriptions = json.loads(args.output.read_text())
        for key, reviewed in MANUAL.items():
            transcriptions[key] = {**reviewed, 'page': transcriptions[key]['page']}
        for item in transcriptions.values():
            item['text'] = clean(item['text'])
            item['options'] = [clean(option) for option in item['options']]
    if len(transcriptions) != 712 or any(not item['text'] for item in transcriptions.values()):
        raise ValueError('Expected 712 non-empty textual transcriptions.')
    args.output.write_text(json.dumps(transcriptions, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'transcribed': len(transcriptions),
                      'withAlternatives': sum(bool(x['options']) for x in transcriptions.values()),
                      'manualMathReviews': len(MANUAL)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
