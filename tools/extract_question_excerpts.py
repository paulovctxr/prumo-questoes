import fitz, json, pathlib, glob, re
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
EXCERPTS = OUT / 'question-excerpts'
EXCERPTS.mkdir(exist_ok=True)
pdf_path = glob.glob('/workspace/scratch/112d1cfd4470/upload/*.pdf')
if not pdf_path:
    raise SystemExit('PDF da apostila não encontrado')
doc = fitz.open(pdf_path[0])
# Each page has a separate, tiny content stream that paints the apostila's
# diagonal watermark image (named X0, X1, ...). Removing only those streams
# keeps all original text, formulas and figures intact while giving the crop a
# clean background.
for page in doc:
    for xref in page.get_contents() or []:
        stream = doc.xref_stream(xref) or b''
        if re.search(rb'/X\d+\s+Do', stream) and b'BT' not in stream and len(stream) < 500:
            doc.update_stream(xref, b'')
source = (OUT / 'imported.js').read_text()
records = json.loads(source.split('const IMPORTED_QUESTIONS=')[1].split(';\nQUESTIONS.push')[0])

def needs_excerpt(text):
    lines = text.splitlines()
    standalone_numbers = sum(bool(re.fullmatch(r'\s*[−\-]?\d+(?:[,.]\d+)?\s*', line)) for line in lines)
    short_lines = sum(bool(line.strip()) and len(line.strip()) <= 2 for line in lines)
    broken_formula = any(token in text for token in ('A = [', '] , x = [', 'xT. x.', '] e B =', 'o valor do determinante de 2.'))
    return standalone_numbers >= 3 or short_lines >= 4 or broken_formula

def redact_source_prefix(piece, page, rect, scale, q):
    """Hide the printed question number and exam/year from the source crop.

    The same information is now shown in PRUMO's question header. We redact
    only the leading marker, preserving the original formulas and statement
    that motivated using this excerpt in the first place.
    """
    exam = str(q.get('exam') or q.get('institution') or '').strip().lower()
    year = str(q.get('year') or '').strip()
    lines = []
    for block in page.get_text('dict').get('blocks', []):
        for line in block.get('lines', []):
            spans = [span for span in line.get('spans', []) if fitz.Rect(span['bbox']).intersects(rect)]
            if spans:
                lines.append(spans)
    lines.sort(key=lambda spans: min(span['bbox'][1] for span in spans))
    if not lines:
        return piece
    first = lines[0]
    line_text = ''.join(span.get('text', '') for span in first)
    marker = re.match(r'\s*\d+\)\s*\(([^)\n]+)\)', line_text)
    if not marker:
        return piece
    label = marker.group(1).lower()
    if not ((exam and exam in label) or (year and year in label)):
        return piece
    end_index = marker.end()
    cursor = 0
    draw = ImageDraw.Draw(piece)
    for span in first:
        text = span.get('text', '')
        start, end = cursor, cursor + len(text)
        if start < end_index:
            bbox = span['bbox']
            x0 = max(0, round((bbox[0] - rect.x0) * scale) - 1)
            y0 = max(0, round((bbox[1] - rect.y0) * scale) - 1)
            y1 = min(piece.height, round((bbox[3] - rect.y0) * scale) + 1)
            if end <= end_index or not text or not text[end_index - start:].strip():
                x1 = min(piece.width, round((bbox[2] - rect.x0) * scale) + 1)
            else:
                fraction = (end_index - start) / max(1, len(text))
                x1 = min(piece.width, round((bbox[0] + (bbox[2] - bbox[0]) * fraction - rect.x0) * scale) + 1)
            draw.rectangle((x0, y0, x1, y1), fill='white')
        cursor = end
    return piece

reviewed = 0
for q in records:
    q.pop('originalExcerpt', None)
    q.pop('originalExcerptWidth', None)
    q.pop('originalExcerptHeight', None)
    if not needs_excerpt(q.get('text', '')):
        continue
    pieces = []
    for segment in q.get('segments', []):
        page = doc[segment['page'] - 1]
        rect = fitz.Rect(segment['x'], segment['y'], segment['x'] + segment['width'], segment['y'] + segment['height'])
        # Keep the original statement/formula, but leave alternatives to the
        # selectable answer buttons rendered by PRUMO.
        first_option_y = None
        for block in page.get_text('dict').get('blocks', []):
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = (span.get('text') or '').strip().lower()
                    bbox = fitz.Rect(span['bbox'])
                    if bbox.intersects(rect) and bbox.x0 <= rect.x0 + 45 and re.match(r'^a[\).]', text):
                        first_option_y = bbox.y0 if first_option_y is None else min(first_option_y, bbox.y0)
        if first_option_y is not None:
            rect.y1 = max(rect.y0 + 8, first_option_y - 2)
        scale = 2.5
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=rect, alpha=False)
        piece = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        pieces.append(redact_source_prefix(piece, page, rect, scale, q))
    if not pieces:
        continue
    width = max(piece.width for piece in pieces)
    height = sum(piece.height for piece in pieces) + max(0, len(pieces) - 1) * 24
    output = Image.new('RGB', (width, height), 'white')
    y = 0
    for piece in pieces:
        output.paste(piece, (0, y))
        y += piece.height + 24
    target = EXCERPTS / f"{q['id']}.png"
    output.save(target, optimize=True)
    q['originalExcerpt'] = f'question-excerpts/{q["id"]}.png'
    q['originalExcerptWidth'] = output.width
    q['originalExcerptHeight'] = output.height
    reviewed += 1

(OUT / 'imported.js').write_text(
    'const IMPORTED_QUESTIONS=' + json.dumps(records, ensure_ascii=False) +
    ';\nQUESTIONS.push(...IMPORTED_QUESTIONS);\nfor(const q of IMPORTED_QUESTIONS){let group=TOPICS.find(t=>t[0]===q.topic);if(!group){group=[q.topic,[]];TOPICS.push(group)}if(!group[1].includes(q.sub))group[1].push(q.sub)}\n'
)
print({'reviewed': reviewed})
