import fitz,json,re,copy,pathlib,sys,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'dist';pages=OUT/'digital-pages';questions=OUT/'digital-questions';pages.mkdir(exist_ok=True);questions.mkdir(exist_ok=True)
S='http://www.w3.org/2000/svg';X='http://www.w3.org/1999/xlink';ET.register_namespace('',S);ET.register_namespace('xlink',X)
doc=fitz.open(sys.argv[1]);data=(OUT/'imported.js').read_text();records=json.loads(data.split('const IMPORTED_QUESTIONS=')[1].split(';\nQUESTIONS.push')[0]);cache={};stats={'questions':0,'selectableCharacters':0,'pages':0}
def numeric(s):return [float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',s or '')]
def load(p):
 if p in cache:return cache[p]
 svg=ET.fromstring(doc[p-1].get_svg_image(text_as_path=False));texts=[copy.deepcopy(t) for t in svg.iter('{'+S+'}text')]
 # Source typography remains text. Only geometric marks and original figures
 # are shared as vector/background elements; no complete question bitmap.
 for parent in svg.iter():
  for child in list(parent):
   if child.tag=='{'+S+'}text':parent.remove(child)
 g=ET.Element('{'+S+'}g',{'id':'graphics'})
 for child in list(svg):
  if child.tag!='{'+S+'}defs':svg.remove(child);g.append(child)
 svg.append(g)
 ET.ElementTree(svg).write(pages/f'p{p:03d}.svg',encoding='unicode')
 cache[p]=texts;stats['pages']+=1;return texts
for q in records:
 height=sum(s['height'] for s in q['segments'])+6*(len(q['segments'])-1);width=max(s['width'] for s in q['segments'])
 root=ET.Element('{'+S+'}svg',{'viewBox':f'0 0 {width} {height}','width':str(width),'height':str(height),'class':'native-question','role':'group','aria-label':f"Questão {q['source']['number']} digitalizada, {q['topic']}",'data-native-text':'true'})
 offset=0;characters=0
 for seg in q['segments']:
  p=seg['page'];x0,y0,w,h=seg['x'],seg['y'],seg['width'],seg['height'];texts=load(p)
  part=ET.SubElement(root,'{'+S+'}svg',{'x':'0','y':str(offset),'width':str(w),'height':str(h),'viewBox':f'{x0} {y0} {w} {h}','overflow':'hidden'})
  ET.SubElement(part,'{'+S+'}use',{'{'+X+'}href':f'../digital-pages/p{p:03d}.svg#graphics','class':'native-figures','aria-hidden':'true'})
  # The question text and alternatives are rendered by the app as selectable HTML.
  # Keep this asset limited to the visual material that cannot be transcribed safely:
  # charts, diagrams, matrices and other figures.
  for original in []:
   t=ET.Element(original.tag,dict(original.attrib));m=numeric(original.get('transform'));a,b,c,d,e,f=m if len(m)==6 else [1,0,0,1,0,0]
   family=(t.get('font-family') or '').lower()
   if 'times' in family: t.set('font-family','Times New Roman, Liberation Serif, serif')
   elif 'cambria' in family: t.set('font-family','Cambria Math, STIX Two Math, serif')
   elif 'arial' in family: t.set('font-family','Arial, Liberation Sans, sans-serif')
   elif 'symbol' in family: t.set('font-family','Symbol, serif')
   for span in original:
    if span.tag!='{'+S+'}tspan':continue
    xs=numeric(span.get('x'));ys=numeric(span.get('y'));value=span.text or ''
    if not xs or not ys or not value:continue
    chosen=[];positions=[];ypositions=[]
    for i,ch in enumerate(value):
     xx=xs[min(i,len(xs)-1)];yy=ys[min(i,len(ys)-1)];tx=a*xx+c*yy+e;ty=b*xx+d*yy+f
     if x0-.5<=tx<=x0+w+.5 and y0<=ty<=y0+h:
      chosen.append(ch);positions.append(xx);ypositions.append(yy)
    if chosen:
     new=ET.SubElement(t,span.tag,{**span.attrib,'x':' '.join(map(str,positions)),'y':' '.join(map(str,ypositions))});new.text=''.join(chosen);characters+=len(chosen)
   if len(t):part.append(t)
  offset+=h+6
 if not q.get('text'):raise RuntimeError(f"Empty question text {q['id']}")
 ET.ElementTree(root).write(questions/f"{q['id']}.svg",encoding='unicode')
 q['digital']='digital-questions/'+str(q['id'])+'.svg';q['digitalWidth']=width;q['digitalHeight']=height
 stats['questions']+=1;stats['selectableCharacters']+=characters
(OUT/'imported.js').write_text('const IMPORTED_QUESTIONS='+json.dumps(records,ensure_ascii=False)+';\nQUESTIONS.push(...IMPORTED_QUESTIONS);\nfor(const q of IMPORTED_QUESTIONS){let group=TOPICS.find(t=>t[0]===q.topic);if(!group){group=[q.topic,[]];TOPICS.push(group)}if(!group[1].includes(q.sub))group[1].push(q.sub)}\n')
(ROOT/'tools/digitalization-report.json').write_text(json.dumps(stats,indent=2));print(stats)
