"""Build the deliverable render gallery (HTML + JSON manifest + contact sheets) from the actual
rendered originals in evidence/current-production. Nothing here renders or invents imagery.
"""
import json, hashlib, struct
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / 'evidence/current-production'
design = json.loads((R / 'design/production-views.json').read_text())
frames = {f['id']: f for f in design['frames']}


def png_size(p):
    with p.open('rb') as f:
        head = f.read(24)
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


order = [f['building_id'] + '_exterior' for f in design['frames'] if f['kind'] == 'building'] + ['V01', 'V02', 'V03', 'V04']
order += [i for i in ('H01', 'H02', 'H03', 'H04', 'H05', 'H06') if (OUT / (i + '.png')).exists()]
order += sorted(p.stem for p in OUT.glob('*.png') if p.stem in frames and p.stem not in order)
rows = []
for vid in order:
    p = OUT / (vid + '.png')
    if not p.exists():
        continue
    meta = OUT / (vid + '.json')
    m = json.loads(meta.read_text()) if meta.exists() else {}
    f = frames.get(vid, {})
    rows.append({'view': vid, 'title': f.get('title', vid), 'image': str(p.relative_to(R)),
                 'bytes': p.stat().st_size, 'sha256': sha(p), 'dimensions': list(png_size(p)),
                 'samples': f.get('samples'), 'camera': f.get('position'), 'target': f.get('target'),
                 'lens_mm': f.get('lens_mm'), 'source_native_sha256': m.get('exact_saved_native_sha256'),
                 'inspection': 'opened individually; see evidence/production/R14-gallery-inspections.json'})

(R / 'evidence/production/R14-render-gallery-manifest.json').write_text(json.dumps(
    {'stage': 'ACTUAL_RENDERS_OF_CURRENT_EDITABLE_SOURCE - NOT INDEPENDENT ACCEPTANCE',
     'source_full_native_sha256': json.loads((R / 'evidence/production/R14-exterior-framed-town.json').read_text())['native_sha256'],
     'views': rows, 'count': len(rows)}, indent=2) + '\n')

groups = [('All twelve buildings', [r for r in rows if r['view'].endswith('_exterior')]),
          ('Whole village', [r for r in rows if r['view'].startswith('V')]),
          ('Street-level and hero views', [r for r in rows if r['view'].startswith('H')]),
          ('Floor plans, cutaways and interiors', [r for r in rows if '_L' in r['view']])]
html = ['''<!doctype html><html lang="en"><meta charset="utf-8"><title>Winterlichtplatz renders</title>
<style>body{background:#0d1117;color:#e6edf3;font:15px/1.5 system-ui,sans-serif;margin:0;padding:32px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:34px 0 12px;border-bottom:1px solid #30363d;padding-bottom:6px}
p.note{color:#9aa7b4;max-width:900px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:18px}
figure{margin:0;background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#000}figcaption{padding:9px 11px;font-size:13px;color:#c9d3de}
figcaption b{color:#fff;display:block;font-size:14px}code{color:#8b98a5;font-size:12px}</style>
<h1>Winterlichtplatz - rendered views of the current editable model</h1>
<p class="note">These are actual renders of the saved editable Blender source (SHA in the manifest), not concept art or generated images.
The model is an in-progress production asset: it is not photoreal, not code-compliant and not independently accepted.
People are licensed photographic scans (Digital Reality Lab HSRD-100, CC BY 4.0); brands are original fictional.</p>''']
for title, items in groups:
    if not items:
        continue
    html.append('<h2>' + title + '</h2><div class="grid">')
    for r in items:
        html.append('<figure><img src="%s.png" alt="%s"><figcaption><b>%s</b>%s &middot; %d&times;%d &middot; %d samples<br><code>%s</code></figcaption></figure>'
                    % (r['view'], r['title'], r['view'], r['title'], r['dimensions'][0], r['dimensions'][1],
                       r['samples'] or 0, r['sha256'][:16]))
    html.append('</div>')
html.append('</html>')
(R / 'renders' / 'gallery.html').write_text('\n'.join(html))

# self-contained copy: thumbnails embedded so it opens with no server and no network
import base64, io
from PIL import Image
embedded = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Winterlichtplatz renders</title>'
            '<style>body{background:#0d1117;color:#e6edf3;font:15px/1.5 system-ui,sans-serif;margin:0;padding:28px}'
            'h1{font-size:24px;margin:0 0 6px}h2{font-size:18px;margin:32px 0 12px;border-bottom:1px solid #30363d;padding-bottom:6px}'
            'p.note{color:#9aa7b4;max-width:900px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}'
            'figure{margin:0;background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden}'
            'figure img{width:100%;display:block}figcaption{padding:8px 10px;font-size:13px;color:#c9d3de}'
            'figcaption b{color:#fff;display:block;font-size:14px}</style>'
            '<h1>Winterlichtplatz &mdash; rendered views of the current editable model</h1>'
            '<p class="note">Actual renders of the saved editable Blender source. Working production asset: '
            'not photoreal, not code certification, not independently accepted. People are licensed photographic '
            'scans (HSRD-100, CC BY 4.0); all brands are original fictional ones.</p>']
for title, items in groups:
    if not items:
        continue
    embedded.append('<h2>' + title + '</h2><div class="grid">')
    for r in items:
        im = Image.open(R / r['image']).convert('RGB')
        im.thumbnail((900, 900))
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=82, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        embedded.append('<figure><img src="data:image/jpeg;base64,%s" alt="%s"><figcaption><b>%s</b>%s &middot; original %d&times;%d</figcaption></figure>'
                        % (b64, r['title'], r['view'], r['title'], r['dimensions'][0], r['dimensions'][1]))
    embedded.append('</div>')
embedded.append('</html>')
(R / 'renders' / 'Winterlichtplatz-renders-gallery.html').write_text('\n'.join(embedded))
print('GALLERY_WRITTEN', len(rows), 'views', flush=True)
for r in rows:
    print('GALLERY_ROW', r['view'], r['dimensions'], r['bytes'])
