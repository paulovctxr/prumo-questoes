"""Register all original TAE exercises in the existing QUESTIONS collection.

Reads the prepared facsimile catalog and extracts only unambiguous printed
multiple-choice keys. Never turn an ungraded written answer into a wrong attempt.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import fitz


TOPIC_MAP = {
    '11': ('Conjuntos', 'Teoria dos conjuntos'),
    '37': ('Equações, inequações e sistemas', 'Módulo de um número real'),
    '48': ('Polinômios', 'Operações com polinômios'),
    '73': ('Álgebra e expressões algébricas', 'Produtos notáveis'),
    '89': ('Álgebra e expressões algébricas', 'Fatoração'),
    '106': ('Álgebra e expressões algébricas', 'Frações algébricas'),
    '126': ('Equações, inequações e sistemas', 'Equações do 1º grau'),
    '142': ('Funções', 'Afim'),
    '164': ('Equações, inequações e sistemas', 'Equações diofantinas'),
    '176': ('Matrizes, determinantes e sistemas lineares', 'Sistemas lineares'),
    '197': ('Álgebra e expressões algébricas', 'Desigualdades'),
    '216': ('Equações, inequações e sistemas', 'Inequações do 1º grau'),
    '231': ('Equações, inequações e sistemas', 'Equações do 2º grau'),
    '253': ('Equações, inequações e sistemas', 'Trinômio do 2º grau'),
    '272': ('Funções', 'Quadrática'),
    '309': ('Álgebra e expressões algébricas', 'Álgebra elementar'),
    '320': ('Equações, inequações e sistemas', 'Equações irracionais'),
    '336': ('Equações, inequações e sistemas', 'Inequações irracionais'),
    '348': ('Potenciação e radiciação', 'Radicais'),
    '360': ('Álgebra e expressões algébricas', 'Problemas de álgebra'),
}

# Option labels inside formulas or embedded images can disappear in PDF text
# extraction. Counts below were checked against the original exercise images.
ORIGINAL_CHOICE_COUNTS = {
    '48:13': 5, '142:10': 4, '176:19': 5, '197:1': 4, '197:3': 4,
    '231:33': 4, '272:22': 5, '272:27': 4, '272:29': 4,
    '272:30': 5, '309:23': 5, '360:9': 5, '360:29': 5,
}

DETAIL_FIELDS = ['text', 'steps', 'bookImages', 'bookAnswerImages', 'answerText', 'solutionNote']


def write_supabase_import(records, path):
    payload = json.dumps(records, ensure_ascii=False, separators=(',', ':'))
    if '$tae_payload$' in payload:
        raise ValueError('SQL payload delimiter occurs in source text.')
    prefix = '''-- Import the original exercises into the existing Supabase bank.
-- Run once in the project's SQL Editor. Re-running updates these same IDs.
-- No API key or other credential belongs in this file.
BEGIN;
CREATE TABLE IF NOT EXISTS public.questoes (
  id bigint PRIMARY KEY,
  enunciado text NOT NULL,
  alternativas jsonb NOT NULL DEFAULT '[]'::jsonb,
  gabarito integer CHECK (gabarito >= 0),
  assunto text, subassunto text, instituicao text, ano integer,
  dificuldade text CHECK (dificuldade IN ('fácil','média','difícil')),
  figura_url text, resolucao text, fonte text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.questoes ADD COLUMN IF NOT EXISTS dados_aplicacao jsonb;
ALTER TABLE public.questoes ADD COLUMN IF NOT EXISTS resumo_aplicacao jsonb;
ALTER TABLE public.questoes ALTER COLUMN gabarito DROP NOT NULL;
ALTER TABLE public.questoes ENABLE ROW LEVEL SECURITY;
GRANT SELECT ON public.questoes TO authenticated;
DO $tae_policy$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public'
      AND tablename = 'questoes' AND policyname = 'authenticated users read questions') THEN
    CREATE POLICY "authenticated users read questions" ON public.questoes
      FOR SELECT TO authenticated USING (true);
  END IF;
END $tae_policy$;

DO $tae_import$
DECLARE imported integer;
BEGIN
  WITH incoming AS (
    SELECT value AS item FROM jsonb_array_elements($tae_payload$'''
    suffix = '''$tae_payload$::jsonb)
  ), upserted AS (
    INSERT INTO public.questoes AS existing
      (id, enunciado, alternativas, gabarito, assunto, subassunto, instituicao,
       ano, dificuldade, figura_url, resolucao, fonte, dados_aplicacao, resumo_aplicacao)
    SELECT (item->>'id')::bigint, item->>'text', item->'options',
      (item->>'answer')::integer, item->>'topic', item->>'sub', item->>'institution',
      (item->>'year')::integer,
      CASE WHEN item->>'difficulty' IN ('Fácil','Média','Difícil')
        THEN lower(item->>'difficulty') ELSE NULL END,
      item->'bookImages'->0->>'src',
      (SELECT string_agg(step, E'\\n\\n' ORDER BY n)
       FROM jsonb_array_elements_text(item->'steps') WITH ORDINALITY AS s(step,n)),
      item->'source'->>'name', item,
      item - ARRAY['text','steps','bookImages','bookAnswerImages','answerText','solutionNote']::text[]
    FROM incoming
    ON CONFLICT (id) DO UPDATE SET
      enunciado=EXCLUDED.enunciado, alternativas=EXCLUDED.alternativas,
      gabarito=EXCLUDED.gabarito, assunto=EXCLUDED.assunto,
      subassunto=EXCLUDED.subassunto, instituicao=EXCLUDED.instituicao,
      ano=EXCLUDED.ano, dificuldade=EXCLUDED.dificuldade,
      figura_url=EXCLUDED.figura_url, resolucao=EXCLUDED.resolucao,
      fonte=EXCLUDED.fonte, dados_aplicacao=EXCLUDED.dados_aplicacao,
      resumo_aplicacao=EXCLUDED.resumo_aplicacao,
      updated_at=now()
    WHERE existing.fonte=EXCLUDED.fonte
    RETURNING 1
  )
  SELECT count(*) INTO imported FROM upserted;
  IF imported <> 712 THEN
    RAISE EXCEPTION 'Expected 712 original exercises, imported %. An ID belongs to another source; no changes were committed.', imported;
  END IF;
END $tae_import$;
COMMIT;
'''
    path.write_text(prefix + payload + suffix)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--catalog', type=Path, default=Path('dist/livro-algebra/catalog.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('dist/questoes-algebra'))
    parser.add_argument('--index-output', type=Path, default=Path('dist/questoes-algebra-index.json'))
    parser.add_argument('--sql-output', type=Path, default=Path('supabase/import_tae.sql'))
    args = parser.parse_args()
    book = json.loads(args.catalog.read_text())
    printed_keys = {}
    with fitz.open(args.pdf) as doc:
        for chapter in book['chapters']:
            text = '\n'.join(doc[image['page'] - 1].get_text(sort=True)
                             for image in chapter['answerImages'])
            pairs = re.findall(r'^\s*(\d{1,3})\s*(?:\)|[-–]|\s)\s*([a-eA-E])\s*$',
                               text, re.MULTILINE)
            chapter_keys = {}
            for number, letter in pairs:
                chapter_keys.setdefault(number, set()).add(letter.upper())
            for number, letters in chapter_keys.items():
                if len(letters) == 1:
                    printed_keys[f"{chapter['id']}:{number}"] = letters.pop()
    chapters = {chapter['id']: chapter for chapter in book['chapters']}
    records = []
    for question in book['questions']:
        chapter = chapters[question['chapter']]
        topic, sub = TOPIC_MAP[question['chapter']]
        labels = set(re.findall(r'(?<![A-Za-z0-9])([a-eA-E])\s*\)', question['searchText']))
        labels = {letter.upper() for letter in labels}
        count = max((ord(letter) - ord('A') + 1 for letter in labels), default=0)
        is_choice = {'A', 'B', 'C'} <= labels
        if question['id'] in ORIGINAL_CHOICE_COUNTS:
            count = ORIGINAL_CHOICE_COUNTS[question['id']]
            is_choice = True
        solution = question.get('solution', {})
        letter = printed_keys.get(question['id'])
        if solution:
            # Authored explanations may identify a corrected answer or a
            # defective original with more than one valid option.
            match = re.match(r'^([A-E])(?:\s*[—–-]|\s*$)', solution['answer'])
            letter = match[1] if match else None
        if not is_choice or (letter and ord(letter) - ord('A') >= count):
            letter = None
        source_label = re.match(r'^\s*\d+\)\s*\(([^)]+)\)', question['searchText'])
        exam = source_label[1].strip() if source_label else book['title']
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', source_label[1]) if source_label else None
        record = {
            'id': 1000000 + int(question['chapter']) * 1000 + question['number'],
            'topic': topic, 'sub': sub, 'difficulty': 'Não classificada',
            'text': question['searchText'],
            'options': [f'Alternativa {chr(65 + index)}' for index in range(count)] if is_choice else [],
            'answer': ord(letter) - ord('A') if letter else None,
            'steps': solution.get('steps', []),
            'type': 'Múltipla escolha' if is_choice else 'Discursiva',
            'institution': book['title'], 'exam': exam,
            'year': int(year_match[1]) if year_match else None,
            'solution': 'Texto' if solution.get('steps') else 'Gabarito',
            'solutionNote': solution.get('editorial_note', ''),
            'answerText': solution.get('answer', letter or ''),
            'bookOriginal': True, 'bookImages': question['images'],
            'bookAnswerImages': chapter['answerImages'],
            'source': {'name': book['title'], 'page': question['page'],
                       'number': question['number'], 'chapter': chapter['title'],
                       'publicationYear': book['year'], 'bookKey': question['id']},
        }
        version_data = json.dumps(record, ensure_ascii=False, sort_keys=True).encode()
        record['contentVersion'] = hashlib.sha256(version_data).hexdigest()[:16]
        records.append(record)
    ids = [question['id'] for question in records]
    if len(records) != 712 or len(set(ids)) != 712:
        raise ValueError('Expected 712 distinct original exercises.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for record in records:
        (args.output_dir / f"{record['id']}.json").write_text(
            json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n')
        summaries.append({key: value for key, value in record.items() if key not in DETAIL_FIELDS})
    args.index_output.write_text(json.dumps(summaries, ensure_ascii=False, separators=(',', ':')) + '\n')
    write_supabase_import(records, args.sql_output)
    print(json.dumps({'added': len(records), 'topics': len({q['topic'] for q in records}),
                      'multipleChoice': sum(q['type'] == 'Múltipla escolha' for q in records),
                      'autoGraded': sum(q['answer'] is not None for q in records),
                      'workedSolutions': sum(bool(q['steps']) for q in records)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
