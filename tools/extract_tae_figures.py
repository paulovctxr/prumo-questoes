"""Export only indispensable graphs, diagrams and visual tables from the PDF."""
import argparse
import json
from pathlib import Path

import fitz
from PIL import Image


# page number and a tight rectangle around the visual information only.
CROPS = {
    '11:22': (27, (64, 160, 370, 516)),
    '142:14': (153, (52, 43, 324, 211)),
    '142:15': (153, (86, 416, 340, 547)),
    '142:25': (157, (52, 226, 181, 543)),
    '142:29': (159, (52, 104, 281, 313)),
    '142:31': (160, (38, 177, 280, 363)),
    '142:32': (161, (52, 86, 343, 242)),
    '176:31': (193, (52, 147, 347, 233)),
    '216:32': (227, (52, 417, 254, 547)),
    '272:11': (293, (52, 167, 280, 324)),
    '272:13': (294, (38, 99, 185, 242)),
    '272:16': (295, (52, 252, 182, 374)),
    '272:27': (300, (38, 42, 359, 254)),
    '272:28': (301, (52, 52, 373, 331)),
    '272:29': (303, (52, 76, 370, 267)),
    '272:30': (303, (52, 382, 377, 542)),
    '272:31': (305, (52, 144, 366, 271)),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path,
                        default=Path('dist/questoes-algebra-figuras'))
    parser.add_argument('--manifest', type=Path,
                        default=Path('tools/tae-figures.json'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with fitz.open(args.pdf) as document:
        for key, (page_number, coordinates) in CROPS.items():
            chapter, number = key.split(':')
            question_id = 1000000 + int(chapter) * 1000 + int(number)
            pixmap = document[page_number - 1].get_pixmap(
                matrix=fitz.Matrix(2.5, 2.5), clip=fitz.Rect(coordinates), alpha=False)
            destination = args.output / f'{question_id}.webp'
            Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples).save(
                destination, 'WEBP', lossless=True)
            manifest[key] = {
                'src': f'questoes-algebra-figuras/{destination.name}',
                'width': pixmap.width, 'height': pixmap.height,
                'alt': 'Gráfico, diagrama ou tabela necessário para resolver a questão.',
            }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'figures': len(manifest), 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
