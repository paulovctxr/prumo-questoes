"""Build the book collection from the supplied PDF and authored solutions.

Never invent answer keys or label a missing explanation as complete.
"""
import argparse
import json
import shutil
from pathlib import Path

import fitz
from PIL import Image

from inventory_tae import inventory


def load_solutions():
    result = {}
    for path in sorted(Path(__file__).parent.glob('tae-solutions*.json')):
        batch = json.loads(path.read_text())
        overlap = result.keys() & batch.keys()
        if overlap:
            raise ValueError(f'Duplicate solution keys in {path}: {sorted(overlap)}')
        for key, solution in batch.items():
            if not solution.get('answer') or not solution.get('steps'):
                raise ValueError(f'Incomplete solution: {key}')
        result.update(batch)
    return result


def export_image(page, rect, destination):
    """Rasterize original glyphs and diagrams, without math transcription."""
    # Tighten only empty borders; retain every intersecting original drawing.
    contents = []
    for block in page.get_text('blocks'):
        bounds = fitz.Rect(block[:4])
        if rect.intersects(bounds):
            contents.append(bounds & rect)
    for item in page.get_image_info():
        bounds = fitz.Rect(item['bbox'])
        if rect.intersects(bounds):
            contents.append(bounds & rect)
    for drawing in page.get_drawings():
        bounds = drawing['rect']
        if rect.intersects(bounds):
            contents.append(bounds & rect)
    if not contents:
        return None
    ink_top = min(r.y0 for r in contents)
    ink_bottom = max(r.y1 for r in contents)
    rect = fitz.Rect(rect.x0, max(rect.y0, ink_top - 3),
                     rect.x1, min(rect.y1, ink_bottom + 3))
    if rect.height <= 0:
        return None
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=rect, alpha=False)
    image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    image.save(destination, 'WEBP', lossless=True)
    return {'src': 'livro-algebra/' + destination.name,
            'width': pix.width, 'height': pix.height}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    book = inventory(args.pdf)
    solutions = load_solutions()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {'title': book['source']['title'], 'authors': book['source']['authors'],
                'year': book['source']['year'], 'sha256': book['source']['sha256'],
                'chapters': [], 'questions': []}
    seen_solutions = set()
    with fitz.open(args.pdf) as doc:
        for chapter in book['chapters']:
            chapter_id = str(chapter['first_page'])
            answer_images = []
            for page_number in chapter['answer_pages']:
                page = doc[page_number - 1]
                image = export_image(page, fitz.Rect(25, 45, page.rect.width - 25,
                                                     page.rect.height - 48),
                                     args.output / f'answers-{page_number}.webp')
                if image:
                    answer_images.append({'page': page_number, **image})
            manifest['chapters'].append({'id': chapter_id, 'title': chapter['title'],
                                         'answerImages': answer_images})
            for question in chapter['questions']:
                key = f"{chapter_id}:{question['number']}"
                images = []
                for segment_index, segment in enumerate(question['segments']):
                    page = doc[segment['page'] - 1]
                    image = export_image(page, fitz.Rect(segment['rect']),
                                         args.output / f'q-{chapter_id}-{question["number"]}-{segment_index}.webp')
                    if image:
                        images.append(image)
                if not images:
                    raise ValueError(f'No original image for {key}')
                record = {'id': key, 'chapter': chapter_id, 'number': question['number'],
                          'page': question['segments'][0]['page'], 'images': images,
                          'searchText': question['search_text']}
                if key in solutions:
                    record['solution'] = solutions[key]
                    seen_solutions.add(key)
                manifest['questions'].append(record)
    if seen_solutions != solutions.keys():
        raise ValueError(f'Solutions without source exercises: {solutions.keys() - seen_solutions}')
    manifest['total'] = len(manifest['questions'])
    manifest['completeSolutions'] = len(seen_solutions)
    shutil.copyfile(args.pdf, args.output / 'original.pdf')
    (args.output / 'catalog.json').write_text(json.dumps(manifest, ensure_ascii=False,
                                                       separators=(',', ':')) + '\n')
    print(json.dumps({'questions': manifest['total'],
                      'completeSolutions': manifest['completeSolutions'],
                      'remainingSolutions': manifest['total'] - len(seen_solutions),
                      'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
