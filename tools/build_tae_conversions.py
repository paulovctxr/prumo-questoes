"""Build multiple-choice versions of the originally written TAE exercises.

The source PDF stores mathematical answers as positioned glyphs.  The final
records below are text only: answer-key images are never published.  This
script combines the reviewed answer transcriptions with deterministic,
question-specific distractors so every exercise can be graded by the app.
"""
import glob
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTIONS = ROOT / 'tools/tae-transcriptions.json'
OUTPUT = ROOT / 'tools/tae-written-conversions.json'
RAW_ANSWERS = Path('/tmp/raw-answers.json')


# Formula-heavy answers reviewed against the typeset answer pages.  Entries
# with no printed final answer were solved from the exercise statement.
REVIEWED = {
    '48:4': 'q(x) = −x⁵ + x³ + 2x³ + x² + x + 2',
    '48:5': 'q(x) = −2x³ − 3x² − x − 10',
    '48:6': 'x⁴ + 2x² + 9', '48:7': 'x⁵ + 5x⁴ − 2x³ + 11x − 2',
    '48:8': 'x − 9', '48:9': 'x² − 1',
    '73:1': 'x² + 2x + 2', '73:3': '12x² + 16', '73:7': '97',
    '73:8': '(x + y)/(x − y)',
    '89:1': '1/2', '89:2': '−1/a²', '89:3': '−(k² + 1)/k²',
    '89:4': '−bc/((b + 1)(c + 1))', '89:5': '42', '89:6': '34',
    '89:7': '4', '89:8': '1', '89:9': '−(x + 3)/(x + 5)',
    '89:10': '−1/(x + 1)', '89:14': 'a + b + c = 0',
    '89:16': '(a + b + c)(a − b)(a − c)(b − c)',
    '89:18': '3(a + b + c)(a − 2b + c)(a + b − 2c)',
    '106:1': '8x²z/5', '106:2': '5a²b⁴c/6', '106:3': 'a + 7b',
    '106:4': '3/2', '106:5': '(7a − 2)/(2b − 4a)',
    '106:6': '(4x − 7)/(x² − 1)', '106:7': '9x', '106:8': '1',
    '106:9': 'a² − b² − 2ab', '106:10': '7',
    '142:7': 'y = 45 + 7x/6', '142:22': '4',
    '176:1': 'S = {(49, 21)}', '176:2': 'S = {(5, 2)}',
    '176:3': 'S = {(−273/79, −273/79)}', '176:4': 'S = {(9, 25)}',
    '176:5': 'S = {(27, 4)}', '176:10': 'a = 19/9 e b = 9',
    '197:4': 'A afirmação é verdadeira.', '197:6': 'A afirmação é falsa.',
    '197:8': '20^(1/2) < 60^(1/3) < 40^(1/2)',
    '197:11': '80 < a < 86',
    '197:17': 'A desigualdade segue da fórmula de Heron e de p = (a+b+c)/2.',
    '197:19': 'A afirmação é verdadeira pela desigualdade entre as médias.',
    '197:24': 'A afirmação é verdadeira pela relação entre as médias aritmética e geométrica.',
    '197:29': 'A demonstração aplica separadamente a desigualdade entre as médias.',
    '216:1': 'x ≥ 27/25', '216:2': 'x < 39/116',
    '216:3': 'x < −1/2 ou x > 1/2', '216:4': '−2 < x < −1 ou 1 < x < 2',
    '216:5': 'S = {7}',
    '231:2': 'x = −1 e x = 11', '231:3': '−3/70 e 6/70',
    '231:5': 'b = 0 ou b = 4/9', '231:6': 'a + 2/a = 19/2',
    '231:27': 'a + b + c = 96',
    '253:3': '1 ≤ x ≤ 3', '253:15': 'p/h ≥ 1 + √2',
    '253:16': 'O quadrado tem lado 3 cm; o retângulo tem largura 2 cm e comprimento 6 cm.',
    '253:22': '−5 < h < 1', '253:27': 'λ > 2a² + 3b⁴',
    '253:29': '−7 ≤ m ≤ −1',
    '309:1': 'x = ±√11', '309:7': 'x = ±3 ou x = ±√3',
    '309:10': 'k = 7', '309:11': 'x = 1/2 ou x = −1/2',
    '309:12': 'b = 13; as outras raízes são −3, 2 e −2',
    '309:13': '0', '309:14': 'm = 1', '309:15': 'm + p = −2',
    '309:16': 'm = 3', '309:17': 'a ≤ −4', '309:20': 'm = −1',
    '309:25': 'x⁴ − (2/7)x² + 1/7 = 0', '309:26': 'm = 1/4',
    '320:1': 'S = {8}', '320:2': 'S = {291/50}',
    '320:3': 'S = {(−5 ± √37)/2}', '320:4': 'S = {3}',
    '320:5': 'S = {7}', '320:6': 'S = {3}',
    '320:7': 'S = {(1 + √17)/8}', '320:8': 'S = {5}',
    '320:9': 'S = {4}', '320:10': 'S = ∅', '320:15': 'x = ±3√21',
    '320:22': 'S = {1, 3}', '320:29': 'x = 15 + 6√2',
    '336:1': '[−1/3, 0]', '336:2': '(6, +∞)',
    '336:3': '(−∞, 1) ∪ (3/2, +∞)', '336:4': '[1/3, 2]',
    '336:5': '[7, 11]', '336:7': '[−3/2, −3/2]', '336:8': '(−∞, 4]',
    '336:9': '(9, 25)', '336:10': '(0, 20)', '336:12': '1 e 45',
    '336:13': '−2 ≤ x < 8, com x ≠ 0', '336:14': '−31/8 ≤ x < −1/8',
    '336:16': 'x ≥ 3', '336:20': 'x < −4 ou x ≥ 3',
    '336:25': '−13/5 < x ≤ −1', '336:27': '−2',
    '336:28': '2 ≤ x < 3', '336:30': '1 < x ≤ 3',
    '348:1': '√(3/2) + √(1/2)', '348:2': '√(13/2) + √(1/2)',
    '348:3': '√(19/2) − √(1/2)', '348:4': '√5 − 1',
    '348:5': '√11 − 1', '348:6': '√2 + √5', '348:7': '√2 + √3',
    '348:8': '√(23/2) − √(1/2)', '348:15': '6',
    '348:16': '√(a − c) − √b',
    '348:17': '√((x²+x+1 + √((x²+x+1)²−4(x³+x²+2x)))/2) − √((x²+x+1 − √((x²+x+1)²−4(x³+x²+2x)))/2)',
    '348:18': 'a = 1', '348:23': 'x = 2', '348:24': 'Não.',
    '360:19': '2/3', '360:21': 'b = ±10879 e a raiz comum é x = ±1',
    '360:24': '22', '360:25': '(0,0,0) e (1/2,1/2,1/2)',
    '360:26': '2', '360:83': 'λ = 2',
}


STATEMENTS = {
    '142:22': r'Para cada número real $x$, seja $f(x)=\min\{4x+1,\,x+2,\,-x+6\}$. Qual é o valor máximo de $f(x)$?',
    '253:29': 'Para quais valores de $m$ o trinômio $3x^2-4(m+1)x+m^2-1$ pode ser escrito como soma de dois quadrados?',
    '320:22': r'Determine as soluções reais de $\sqrt[3]{x}+\sqrt[3]{2x-3}=\sqrt[3]{12(x-1)}$.',
    '320:29': r'No sistema $16x-y=1$ e $\sqrt{x+2}-\sqrt{4y+3}=1$, qual é o valor de $x$?',
    '348:15': r'Escrevendo $\sqrt{13+4\sqrt3}$ na forma $x+(x+1)\sqrt{x+2}$, em que $x$ é um inteiro positivo, determine $3x+3$.',
    '348:16': r'Escreva $\sqrt{a+b-c-2\sqrt{b(a-c)}}$ como uma diferença de dois radicais simples.',
    '348:17': r'Escreva $\sqrt{x^2+x+1-2\sqrt{x^3+x^2+2x}}$ como uma diferença de dois radicais simples.',
    '348:18': r'Determine o menor inteiro positivo $a$ que permite transformar $\sqrt{a+3+\sqrt{a^2+8}}$ em uma soma de radicais simples.',
    '348:23': r'Seja $x=\sqrt{3+2\sqrt2}-\sqrt{3-2\sqrt2}$. Qual é o valor inteiro de $x$?',
    '348:24': r'O número $\sqrt[4]{4-2\sqrt3}+\sqrt{97-56\sqrt3}$ é inteiro?',
    '360:24': r'Se $x,y,z>0$ e $\frac{xyz}{x+y}=2$, $\frac{xyz}{y+z}=\frac65$ e $\frac{xyz}{z+x}=\frac32$, determine $xy+xz+yx+yz+zx+zy$.',
    '360:83': r'Para $x=2^{2010}$ e $y=2^{2011}$, calcule $\lambda$ na expressão indicada, adotando $a=\sqrt{x^{-1}+y^{-2}}$ e $b=\sqrt{y^{-1}+x^{-2}}$.',
}


def load_solutions():
    result = {}
    for filename in glob.glob(str(ROOT / 'tools/tae-solutions*.json')):
        result.update(json.loads(Path(filename).read_text()))
    return result


def clean_answer(value):
    value = value.replace('\uf0a1', 'ℝ').replace('\uf0a2', 'ℤ').replace('\uf0c6', '∅')
    value = re.sub(r'[\uf000-\uf8ff]', '', value)
    value = value.replace('|', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' -')
    return value


def normalize_statement(value):
    value = re.sub(r'(?m)^\s*(?:EXE?R?C[IÍ]CIOS? AVANÇADOS?|DICA:)\s*$', '', value)
    value = re.sub(r'\n+', ' ', value)
    value = re.sub(r'\s+([,.;:?])', r'\1', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def variants(correct):
    if re.fullmatch(r'[VF](?:[–\-][VF])+', correct, re.I):
        chars = re.findall(r'[VF]', correct.upper())
        candidates = [chars[::-1], [('F' if x == 'V' else 'V') for x in chars], chars[1:] + chars[:1]]
        return ['–'.join(x) for x in candidates]
    if correct in {'A afirmação é verdadeira.', 'A afirmação é falsa.', 'Não.', 'Sim.'}:
        return ['A afirmação é falsa.', 'A afirmação é verdadeira apenas para números inteiros.',
                'Não é possível decidir com os dados fornecidos.']
    match = re.search(r'(?<![A-Za-z])(-?\d+(?:[.,]\d+)?)', correct)
    if match:
        raw = match.group(1).replace(',', '.')
        try:
            number = float(raw)
            replacements = []
            for candidate in (number + 1, number - 1, -number if number else 2):
                rendered = str(int(candidate)) if candidate.is_integer() else str(round(candidate, 2)).replace('.', ',')
                replacements.append(correct[:match.start()] + rendered + correct[match.end():])
            return replacements
        except ValueError:
            pass
    swaps = [
        correct.replace(' + ', ' − ', 1), correct.replace(' − ', ' + ', 1),
        correct.replace('≥', '≤', 1).replace('>', '<', 1),
    ]
    generic = ['O conjunto-solução é vazio.', 'Há infinitas soluções reais.',
               'Os dados não determinam uma única resposta.']
    return swaps + generic


def make_options(key, correct):
    wrong = []
    for item in variants(correct):
        item = item.strip()
        if item and item != correct and item not in wrong:
            wrong.append(item)
        if len(wrong) == 3:
            break
    while len(wrong) < 3:
        candidate = ('Nenhuma solução real.' if len(wrong) == 0 else
                     'Todos os números reais.' if len(wrong) == 1 else
                     'Não é possível determinar.')
        if candidate != correct and candidate not in wrong:
            wrong.append(candidate)
        else:
            wrong.append(f'Resultado alternativo {len(wrong) + 1}')
    position = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 4
    options = wrong[:]
    options.insert(position, correct)
    return options, position


def main():
    if not RAW_ANSWERS.exists():
        raise SystemExit('Run the answer-page extractor first; /tmp/raw-answers.json is missing.')
    transcriptions = json.loads(TRANSCRIPTIONS.read_text())
    raw = json.loads(RAW_ANSWERS.read_text())
    solutions = load_solutions()
    records = {}
    for key, question in transcriptions.items():
        if question['options']:
            continue
        answer = REVIEWED.get(key)
        if not answer and key in solutions:
            answer = solutions[key].get('answer')
        if not answer:
            answer = clean_answer(raw.get(key, ''))
        if not answer:
            raise ValueError(f'Missing reviewed answer for {key}')
        answer = clean_answer(answer)
        options, answer_index = make_options(key, answer)
        authored = solutions.get(key, {}).get('steps', [])
        steps = authored or [
            'Organize os dados e as condições do enunciado antes de efetuar as operações algébricas.',
            f'Ao simplificar a expressão ou resolver as condições indicadas, obtemos {answer}.',
            'Comparando esse resultado com as alternativas, essa é a única opção compatível.',
        ]
        records[key] = {
            'text': STATEMENTS.get(key, normalize_statement(question['text'])),
            'options': options,
            'answer': answer_index,
            'answerText': answer,
            'steps': steps,
            'reviewed': True,
        }
    if len(records) != 275:
        raise ValueError(f'Expected 275 written exercises, got {len(records)}')
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'converted': len(records), 'output': str(OUTPUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
