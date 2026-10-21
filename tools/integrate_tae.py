"""Register the text-only TAE transcriptions in the shared question bank."""
import argparse
import hashlib
import json
import re
from pathlib import Path


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

CHAPTER_TITLES = {
    '11': 'Fundamentos da teoria dos conjuntos',
    '37': 'Módulo de um número real', '48': 'Polinômios',
    '73': 'Produtos notáveis', '89': 'Fatoração', '106': 'Frações algébricas',
    '126': 'Equação do primeiro grau', '142': 'Função do primeiro grau',
    '164': 'Equações diofantinas lineares',
    '176': 'Sistemas de equações do primeiro grau',
    '197': 'Desigualdades elementares', '216': 'Inequações do primeiro grau',
    '231': 'Equação do segundo grau', '253': 'Trinômio do segundo grau',
    '272': 'Função do segundo grau', '309': 'Tópicos de álgebra elementar',
    '320': 'Equação irracional', '336': 'Inequação irracional',
    '348': 'Transformação de expressões', '360': 'Miscelânea de questões',
}

DETAIL_FIELDS = ['text', 'steps', 'answerText', 'solutionNote', 'figure']
BOOK_NAME = 'Tópicos de Álgebra Elementar'


def load_solutions():
    result = {}
    for path in sorted(Path(__file__).parent.glob('tae-solutions*.json')):
        batch = json.loads(path.read_text())
        overlap = result.keys() & batch.keys()
        if overlap:
            raise ValueError(f'Duplicate solution keys in {path}: {sorted(overlap)}')
        result.update(batch)
    return result


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
      item->'figure'->>'src',
      (SELECT string_agg(step, E'\\n\\n' ORDER BY n)
       FROM jsonb_array_elements_text(item->'steps') WITH ORDINALITY AS s(step,n)),
      item->'source'->>'name', item,
      item - ARRAY['text','steps','answerText','solutionNote','figure']::text[]
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
    parser.add_argument('--transcriptions', type=Path,
                        default=Path('tools/tae-transcriptions.json'))
    parser.add_argument('--figures', type=Path, default=Path('tools/tae-figures.json'))
    parser.add_argument('--conversions', type=Path,
                        default=Path('tools/tae-written-conversions.json'))
    parser.add_argument('--editorial-overrides', type=Path,
                        default=Path('tools/tae-editorial-overrides.json'))
    parser.add_argument('--answer-keys', type=Path,
                        default=Path('tools/tae-answer-keys.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('dist/questoes-algebra'))
    parser.add_argument('--index-output', type=Path, default=Path('dist/questoes-algebra-index.json'))
    parser.add_argument('--sql-output', type=Path, default=Path('supabase/import_tae.sql'))
    args = parser.parse_args()
    transcriptions = json.loads(args.transcriptions.read_text())
    figures = json.loads(args.figures.read_text())
    conversions = json.loads(args.conversions.read_text())
    editorial_overrides = json.loads(args.editorial_overrides.read_text())
    answer_keys = json.loads(args.answer_keys.read_text())
    solutions = load_solutions()
    records = []
    for key, transcription in transcriptions.items():
        chapter_id, number_text = key.split(':')
        number = int(number_text)
        topic, sub = TOPIC_MAP[chapter_id]
        conversion = conversions.get(key, {})
        editorial = editorial_overrides.get(key, {})
        options = conversion.get('options', editorial.get('options', transcription['options']))
        is_choice = bool(options)
        solution = solutions.get(key, {})
        letter = None
        if solution:
            match = re.match(r'^([A-E])(?:\s*[—–-]|\s*$)', solution['answer'])
            letter = match[1] if match else None
        if not is_choice or (letter and ord(letter) - ord('A') >= len(options)):
            letter = None
        answer = conversion.get('answer', answer_keys.get(key,
                                ord(letter) - ord('A') if letter else None))
        steps = conversion.get('steps', solution.get('steps', []))
        record = {
            'id': 1000000 + int(chapter_id) * 1000 + number,
            'topic': topic, 'sub': sub, 'difficulty': 'Difícil',
            'text': conversion.get('text', editorial.get('text', transcription['text'])), 'options': options,
            'answer': answer,
            'steps': steps,
            'type': 'Múltipla escolha' if is_choice else 'Discursiva',
            'institution': BOOK_NAME, 'exam': BOOK_NAME,
            'year': 2026,
            'solution': 'Texto' if steps else 'Pendente',
            'solutionNote': solution.get('editorial_note', ''),
            'answerText': conversion.get('answerText', solution.get('answer', '')),
            'bookOriginal': True, 'transcribed': True,
            'source': {'name': BOOK_NAME, 'page': transcription['page'],
                       'number': number, 'chapter': CHAPTER_TITLES[chapter_id],
                       'publicationYear': 2021, 'bookKey': key},
        }
        if key in figures:
            record['figure'] = figures[key]
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
