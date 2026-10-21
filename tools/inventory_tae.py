"""Inventory the supplied Tópicos de Álgebra Elementar PDF without publishing.

Usage: python3 tools/inventory_tae.py BOOK.pdf --output /tmp/tae-inventory.json
Coordinates refer to the original PDF and preserve exact question facsimiles.
Detection is provisional: sequence warnings require visual review.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import fitz


CHAPTERS = [
    (11, 'Fundamentos da teoria dos conjuntos'),
    (37, 'Módulo de um número real'),
    (48, 'Polinômios'),
    (73, 'Produtos notáveis'),
    (89, 'Fatoração'),
    (106, 'Frações algébricas'),
    (126, 'Equação do primeiro grau'),
    (142, 'Função do primeiro grau'),
    (164, 'Equações diofantinas lineares'),
    (176, 'Sistemas de equações do primeiro grau'),
    (197, 'Desigualdades elementares'),
    (216, 'Inequações do primeiro grau'),
    (231, 'Equação do segundo grau'),
    (253, 'Trinômio do segundo grau'),
    (272, 'Função do segundo grau'),
    (309, 'Tópicos de álgebra elementar'),
    (320, 'Equação irracional'),
    (336, 'Inequação irracional'),
    (348, 'Transformação de expressões'),
    (360, 'Miscelânea de questões'),
]


def body_lines(page):
    result = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            text = ''.join(span['text'] for span in line['spans']).strip()
            x0, y0, x1, y1 = line['bbox']
            if text and 45 < y0 < page.rect.height - 48:
                block_top = block['bbox'][1]
                result.append({'text': text, 'bbox': [x0, y0, x1, y1],
                               'top': block_top if 0 <= y0 - block_top < 30 else y0})
    return sorted(result, key=lambda item: (item['bbox'][1], item['bbox'][0]))


def inventory(pdf):
    chapters = []
    with fitz.open(pdf) as doc:
        if len(doc) != 400:
            raise ValueError('Expected the supplied 400-page edition; verify chapter offsets.')
        for index, (start, title) in enumerate(CHAPTERS):
            end = CHAPTERS[index + 1][0] if index + 1 < len(CHAPTERS) else 399
            phase = 'theory'
            starts = []
            answer_pages = []
            answer_end = None
            warnings = []
            for page_number in range(start, end):
                page = doc[page_number - 1]
                lines = body_lines(page)
                for line in lines:
                    text = line['text']
                    # In this edition, exercises 1–10 precede the printed
                    # introductory-exercises heading in the Diophantine chapter.
                    if start == 164 and page_number == 168 and re.match(r'^1\)\s*Em um torneio', text):
                        phase = 'questions'
                    if re.search(r'RESPOSTAS?\s+DOS\s+EXERC', text, re.I):
                        phase = 'answers'
                        answer_end = (page_number, line['bbox'][1])
                    elif re.search(r'EXERC[ÍI]CIOS|MISCEL[ÂA]NEA\s+DE\s+QUEST', text, re.I):
                        if phase != 'answers':
                            phase = 'questions'
                    if phase == 'answers':
                        if page_number not in answer_pages and page_number != 398:
                            answer_pages.append(page_number)
                        continue
                    if phase != 'questions':
                        continue
                    match = re.match(r'^(\d{1,3})\s*\)', text)
                    # Subparts inside a question must not start a new record.
                    if not match or line['bbox'][0] > 105:
                        continue
                    number = int(match[1])
                    expected = starts[-1]['number'] + 1 if starts else 1
                    if number != expected:
                        if number >= expected:
                            warnings.append({'page': page_number, 'expected': expected,
                                             'detected': number, 'text': text})
                        continue
                    starts.append({'number': number, 'page': page_number,
                                   'top': max(45, line['top'] - 2)})
            questions = []
            for question_index, question in enumerate(starts):
                if question_index + 1 < len(starts):
                    following = starts[question_index + 1]
                    stop_page, stop_y = following['page'], following['top']
                elif answer_end:
                    stop_page, stop_y = answer_end
                else:
                    stop_page, stop_y = end - 1, doc[end - 2].rect.height - 48
                segments = []
                text = []
                for page_number in range(question['page'], stop_page + 1):
                    page = doc[page_number - 1]
                    top = question['top'] if page_number == question['page'] else 45
                    bottom = stop_y if page_number == stop_page else page.rect.height - 48
                    if bottom <= top:
                        continue
                    rect = fitz.Rect(25, top, page.rect.width - 25, bottom)
                    segment_text = page.get_text(clip=rect, sort=True)
                    if not segment_text.strip():
                        visuals = [fitz.Rect(item['bbox']) for item in page.get_image_info()]
                        visuals.extend(item['rect'] for item in page.get_drawings())
                        if not any(rect.intersects(bounds) for bounds in visuals):
                            continue
                    segments.append({'page': page_number, 'rect': list(rect)})
                    text.append(segment_text)
                questions.append({'number': question['number'], 'segments': segments,
                                  'search_text': '\n'.join(text),
                                  'status': 'requires_visual_review',
                                  'solution_status': 'not_reviewed'})
            chapters.append({'title': title, 'first_page': start, 'last_page': end - 1,
                             'answer_pages': answer_pages, 'questions': questions,
                             'sequence_warnings': warnings})
    return {'source': {'title': 'Tópicos de Álgebra Elementar', 'year': 2021,
                       'authors': ['Bruno Pedra', 'Ivan Monteiro', 'Alex Ricardo'],
                       'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest()},
            'publication_status': 'not_published',
            'notes': ['Search text is not a reliable mathematical transcription.',
                      'Use PDF segments to preserve original layout and notation.',
                      'An answer key is not a complete solution.'],
            'chapters': chapters}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--facsimile-pdf', type=Path,
                        help='Export the original exercise regions, preserving vectors and fonts.')
    args = parser.parse_args()
    result = inventory(args.pdf)
    if args.facsimile_pdf:
        with fitz.open(args.pdf) as source, fitz.open() as output:
            toc = []
            for chapter in result['chapters']:
                if chapter['questions']:
                    toc.append([1, chapter['title'], len(output) + 1])
                for question in chapter['questions']:
                    question['facsimile_pages'] = []
                    for segment in question['segments']:
                        clip = fitz.Rect(segment['rect'])
                        page = output.new_page(width=clip.width, height=clip.height)
                        page.show_pdf_page(page.rect, source, segment['page'] - 1,
                                           clip=clip)
                        question['facsimile_pages'].append(len(output))
            output.set_toc(toc)
            output.set_metadata({'title': 'Exercícios originais — extração para revisão',
                                 'subject': 'Origem: Tópicos de Álgebra Elementar (2021). '
                                            'Não inclui resoluções elaboradas.'})
            output.save(args.facsimile_pdf, garbage=4, deflate=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'chapter': c['title'], 'detected': len(c['questions']),
                       'warnings': len(c['sequence_warnings']),
                       'answer_pages': c['answer_pages']}
                      for c in result['chapters']], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
