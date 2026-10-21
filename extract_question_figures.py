import fitz, io, json, pathlib, glob
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
FIGURES = OUT / 'question-figures'
FIGURES.mkdir(exist_ok=True)
for stale in FIGURES.glob('*.png'):
    stale.unlink()
pdf_path = glob.glob('/workspace/scratch/112d1cfd4470/upload/*.pdf')
if not pdf_path:
    raise SystemExit('PDF da apostila não encontrado')
doc = fitz.open(pdf_path[0])
# Strip the separate PDF content stream used only for the apostila's diagonal
# watermark. Embedded figures are extracted directly below; this also keeps
# the fallback renderer free of background text.
for page in doc:
    for xref in page.get_contents() or []:
        stream = doc.xref_stream(xref) or b''
        if b'/X' in stream and b' Do' in stream and b'BT' not in stream and len(stream) < 500:
            doc.update_stream(xref, b'')
source = (OUT / 'imported.js').read_text()
records = json.loads(source.split('const IMPORTED_QUESTIONS=')[1].split(';\nQUESTIONS.push')[0])

for q in records:
    q.pop('figure', None)
    q.pop('figureWidth', None)
    q.pop('figureHeight', None)
    pieces = []
    for seg in q.get('segments', []):
        page = doc[seg['page'] - 1]
        box = fitz.Rect(seg['x'], seg['y'], seg['x'] + seg['width'], seg['y'] + seg['height'])
        candidates = []
        for image in page.get_images(full=True):
            xref = image[0]
            name = image[7] or ''
            image_width, image_height = image[2], image[3]
            rects = page.get_image_rects(xref)
            for rect in rects:
                overlap = rect & box
                if overlap.is_empty or overlap.get_area() < rect.get_area() * 0.55:
                    continue
                # X37/X59/... are the full-page watermark, not a question figure.
                # The PDF watermark is stored as long, shallow raster strips
                # (often red/gray text), even when its object name is not X*.
                aspect = max(image_width, image_height) / max(1, min(image_width, image_height))
                if name.startswith('X') or aspect > 4 or rect.get_area() > page.rect.get_area() * 0.25:
                    continue
                candidates.append((xref, rect & box))
        if not candidates:
            continue
        seen = set()
        for xref, candidate in candidates:
            # A page render also paints the apostila's watermark layer. Extract
            # the embedded figure itself so that the crop keeps a plain white
            # background and does not inherit text from behind the question.
            key = (xref, round(candidate.x0, 2), round(candidate.y0, 2), round(candidate.x1, 2), round(candidate.y1, 2))
            if key in seen:
                continue
            seen.add(key)
            try:
                raw = doc.extract_image(xref)['image']
                image = Image.open(io.BytesIO(raw))
                if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                    rgba = image.convert('RGBA')
                    background = Image.new('RGBA', rgba.size, 'white')
                    background.alpha_composite(rgba)
                    image = background.convert('RGB')
                else:
                    image = image.convert('RGB')
                pieces.append(image)
            except Exception:
                # Keep a safe fallback for unusual/vector-like image objects.
                crop = (candidate + (-2, -2, 2, 2)) & page.rect
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=crop, alpha=False)
                pieces.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    if not pieces:
        continue
    width = max(piece.width for piece in pieces)
    height = sum(piece.height for piece in pieces) + max(0, len(pieces) - 1) * 18
    output = Image.new('RGB', (width, height), 'white')
    y = 0
    for piece in pieces:
        output.paste(piece, (0, y))
        y += piece.height + 18
    target = FIGURES / f"{q['id']}.png"
    output.save(target, optimize=True)
    q['figure'] = f'question-figures/{q["id"]}.png'
    q['figureWidth'] = output.width
    q['figureHeight'] = output.height

(OUT / 'imported.js').write_text(
    'const IMPORTED_QUESTIONS=' + json.dumps(records, ensure_ascii=False) +
    ';\nQUESTIONS.push(...IMPORTED_QUESTIONS);\nfor(const q of IMPORTED_QUESTIONS){let group=TOPICS.find(t=>t[0]===q.topic);if(!group){group=[q.topic,[]];TOPICS.push(group)}if(!group[1].includes(q.sub))group[1].push(q.sub)}\n'
)
print({'questions': len(records), 'figures': sum(1 for q in records if q.get('figure'))})
