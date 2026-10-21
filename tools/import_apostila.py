import fitz,re,json,pathlib,sys,collections
from PIL import Image
PDF=pathlib.Path(sys.argv[1]); ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'; ASSETS=OUT/'apostila'; ASSETS.mkdir(exist_ok=True)
doc=fitz.open(PDF)
# First question page, answer-key page, topic, subtopic, as printed in the supplied PDF.
sections=[(16,18,'Noções de lógica','Proposições'),(19,23,'Conjuntos','Operações e diagramas de Venn'),(24,28,'Conjuntos','Conjuntos numéricos e intervalos'),(29,34,'Funções','Introdução às funções'),(35,38,'Funções','Composta e inversa'),(39,43,'Funções','Afim'),(44,48,'Funções','Quadrática'),(49,52,'Funções','Modular'),(53,57,'Funções','Exponencial'),(58,65,'Funções','Logarítmica'),(66,76,'Progressões aritméticas e geométricas','PA e PG'),(77,81,'Matrizes, determinantes e sistemas lineares','Matrizes'),(82,87,'Matrizes, determinantes e sistemas lineares','Determinantes'),(88,92,'Matrizes, determinantes e sistemas lineares','Sistemas lineares'),(93,102,'Análise combinatória','Contagem e combinações'),(103,106,'Análise combinatória','Binômio de Newton'),(107,116,'Probabilidade','Probabilidade'),(117,126,'Números complexos','Números complexos'),(127,131,'Polinômios','Polinômios'),(132,138,'Polinômios','Equações polinomiais'),(139,142,'Geometria plana','Ângulos'),(143,148,'Geometria plana','Triângulos'),(149,153,'Geometria plana','Polígonos'),(154,158,'Geometria plana','Circunferências'),(159,167,'Geometria plana','Áreas e perímetros'),(168,172,'Trigonometria','Triângulo e circunferência'),(173,175,'Trigonometria','Identidades e redução ao primeiro quadrante'),(176,179,'Trigonometria','Funções trigonométricas'),(180,183,'Trigonometria','Transformações trigonométricas'),(184,189,'Trigonometria','Equações e inequações'),(190,194,'Geometria espacial','Geometria de posição'),(195,198,'Geometria espacial','Poliedros'),(199,203,'Geometria espacial','Prismas'),(204,207,'Geometria espacial','Pirâmides'),(208,211,'Geometria espacial','Cilindros'),(212,216,'Geometria espacial','Cones'),(217,220,'Geometria espacial','Esferas'),(221,225,'Geometria espacial','Inscrição e circunscrição de sólidos'),(226,228,'Geometria analítica','Ponto'),(229,232,'Geometria analítica','Reta'),(233,236,'Geometria analítica','Distância entre ponto e reta'),(237,243,'Geometria analítica','Circunferência'),(244,250,'Geometria analítica','Cônicas'),(251,257,'Estatística','Estatística'),(258,263,'Matemática financeira','Juros e porcentagem'),(264,267,'Cálculo','Limites e continuidade'),(268,273,'Cálculo','Derivadas'),(274,278,'Cálculo','Integrais'),(279,282,'Vetores e geometria no espaço','Vetores')]

def lines(page,col):
 clip=fitz.Rect(32 if col==0 else 303,30,299 if col==0 else 565,814)
 data=page.get_text('dict',clip=clip)
 result=[]
 for block in data['blocks']:
  for line in block.get('lines',[]):
   text=''.join(s['text'] for s in line['spans']).strip()
   if text and abs(line.get('dir',(1,0))[1])<0.1:result.append((line['bbox'][1],line['bbox'][3],text))
 return sorted(result,key=lambda x:x[0])

def metadata(text):
 h=re.match(r'^\s*\d+\)\s*\(([^)]+)\)',text)
 origin=h.group(1).strip() if h else ''
 year=re.search(r'\b(19\d{2}|20\d{2})\b',origin)
 exam='Origem não identificada'
 for pattern,name in [(r'EsSA|\bESA\b','ESA'),(r'EEAr|EEAR','EEAR'),(r'EsPCEx','EsPCEx'),(r'EFOMM','EFOMM'),(r'EPCAR','EPCAR'),(r'\bAFA\b','AFA'),(r'\bIME\b','IME'),(r'\bITA\b','ITA'),(r'Escola Naval|\bEN\b','Escola Naval'),(r'Colégio Naval|\bCN\b','Colégio Naval'),(r'ENEM','ENEM')]:
  if re.search(pattern,origin,re.I):exam=name;break
 if exam=='Origem não identificada' and origin:
  exam=re.sub(r'\b(?:19|20)\d{2}\b.*','',origin).strip(' .–-') or 'Outras provas'
 return exam,int(year.group()) if year else None,origin

# Alternative counts checked against the rendered original for formulas whose
# isolated variables resemble option markers. Their images remain authoritative.
visually_checked={'029-012.webp':5,'058-040.webp':4,'058-043.webp':4,'058-073.webp':5,'077-006.webp':4,'077-017.webp':5,'088-006.webp':4,'103-027.webp':5,'143-043.webp':5,'226-017.webp':5,'226-021.webp':5,'233-021.webp':5,'237-028.webp':4}
records=[];pending=[];report=[]
for start,end,topic,sub in sections:
 units=[];key_unit=None;key_y=None
 for p in range(start-1,end):
  for col in range(2):
   ls=lines(doc[p],col); units.append((p,col,ls))
   if p==end-1:
    for y,y2,t in ls:
     if re.fullmatch(r'Gabarito',t,re.I):key_unit=len(units)-1;key_y=y;break
 if key_unit is None:
  pending.append({'section':sub,'reason':'Gabarito não localizado'});continue
 key_text='\n'.join(t for u,(_,_,ls) in enumerate(units) if u>=key_unit for y,y2,t in ls if u>key_unit or y>key_y)
 pairs=re.findall(r'(\d+)\)\s*([A-E])\b',key_text)
 keys={int(n):ord(a)-65 for n,a in pairs}
 starts=[]
 for u,(_,_,ls) in enumerate(units):
  if u>key_unit:break
  for y,y2,t in ls:
   if u==key_unit and y>=key_y:break
   m=re.match(r'^(\d+)\)\s*',t)
   if m:starts.append({'n':int(m.group(1)),'u':u,'y':y,'header':t})
 # Only sequential question headings, rejecting accidental numbered content.
 accepted=[];expect=1
 for item in starts:
  if item['n']==expect:accepted.append(item);expect+=1
 for i,q in enumerate(accepted):
  n=q['n'];cached=ASSETS/f'{start:03d}-{n:03d}.webp';nextq=accepted[i+1] if i+1<len(accepted) else {'u':key_unit,'y':key_y}
  chunks=[];texts=[];segments=[]
  for u in range(q['u'],nextq['u']+1):
   p,col,ls=units[u];top=q['y']-1 if u==q['u'] else 32;bottom=nextq['y']-1 if u==nextq['u'] else 813
   if bottom<=top+3:continue
   text='\n'.join(t for y,y2,t in ls if top<=y<bottom);texts.append(text)
   # Preserve original equations, figures and alternatives together as a legible facsimile.
   rect=fitz.Rect(33 if col==0 else 304,top,298 if col==0 else 564,bottom)
   segments.append({'page':p+1,'x':rect.x0,'y':rect.y0,'width':rect.width,'height':rect.height})
   if cached.exists():chunks.append(Image.new('RGB',(1,1),'white'))
   else:
    pix=doc[p].get_pixmap(matrix=fitz.Matrix(2,2),clip=rect,alpha=False)
    chunks.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
  # Remove trailing whitespace after the final content-bearing segment, without
  # shortening continuation columns that may end in a figure.
  while chunks and not texts[-1].strip():chunks.pop();texts.pop();segments.pop()
  if chunks:
   last_u=q['u']+len(chunks)-1
   p_last,col_last,ls_last=units[last_u]
   top_last=q['y']-1 if last_u==q['u'] else 32
   bottom_last=nextq['y']-1 if last_u==nextq['u'] else 813
   final_lines=[y2 for y,y2,t in ls_last if top_last<=y<bottom_last]
   if final_lines:
    height_keep=min(chunks[-1].height,max(1,int((max(final_lines)+5-top_last)*2)))
    segments[-1]['height']=min(segments[-1]['height'],max(final_lines)+5-top_last)
    chunks[-1]=chunks[-1].crop((0,0,chunks[-1].width,height_keep))
  text='\n'.join(texts);matches=list(re.finditer(r'(?:^|\n)[ \t]*([a-e])\)[ \t]*',text));letters=[m.group(1).lower() for m in matches]
  opts=[]
  for j,m in enumerate(matches):opts.append(text[m.end():matches[j+1].start() if j+1<len(matches) else len(text)].strip())
  reason=None
  if n not in keys:reason='Gabarito ausente ou não reconhecido'
  elif not (sorted(letters) in [list('abcd'),list('abcde')]):reason='Alternativas não identificadas com segurança'
  elif keys[n]>=len(opts):reason='Gabarito fora das alternativas'
  checked_count=visually_checked.get(f'{start:03d}-{n:03d}.webp')
  if reason and checked_count and n in keys and keys[n]<checked_count:
   opts=['Alternativa '+chr(65+j)+' — consulte a imagem original' for j in range(checked_count)]
   letters=list('abcde'[:checked_count]);reason=None
  if reason:
   review_dir=ROOT/'tools/pending-images';review_dir.mkdir(exist_ok=True)
   w=max(im.width for im in chunks);h=sum(im.height for im in chunks)+12*(len(chunks)-1)
   review=Image.new('RGB',(w,h),'white');yy=0
   for im in chunks:review.paste(im,(0,yy));yy+=im.height+12
   fn=f'{start:03d}-{n:03d}.webp';review.save(review_dir/fn,'WEBP',quality=88)
   pending.append({'section':sub,'number':n,'page':units[q['u']][0]+1,'reason':reason,'file':fn,'letters':letters,'text':text,'answer':keys.get(n)});continue
  width=max(im.width for im in chunks);height=sum(im.height for im in chunks)+12*(len(chunks)-1)
  canvas=Image.new('RGB',(width,height),'white');y=0
  for im in chunks:canvas.paste(im,(0,y));y+=im.height+12
  opts=[o for letter,o in sorted(zip(letters,opts))]
  filename=f'{start:03d}-{n:03d}.webp'
  if cached.exists():height=Image.open(cached).height
  else:canvas.save(ASSETS/filename,'WEBP',quality=85)
  exam,year,origin=metadata(q['header']);identifier=10000+start*1000+n
  stem=text[:matches[0].start()].strip()
  records.append({'id':identifier,'topic':topic,'sub':sub,'difficulty':'Não classificada','text':stem,'options':[o or 'Alternativa '+letters[j].upper() for j,o in enumerate(opts)],'answer':keys[n],'steps':[],'type':'Múltipla escolha','institution':exam if origin else 'Não identificada na apostila','exam':exam,'year':year,'solution':'Gabarito','image':'apostila/'+filename,'source':{'name':'Apostila de Matemática — Mateus Germano da Silva','page':units[q['u']][0]+1,'number':n,'keyPage':end,'origin':origin},'imageHeight':height,'segments':segments})
 report.append({'topic':topic,'sub':sub,'headings':len(accepted),'keys':len(keys),'imported':sum(r['source']['page']>=start and r['source']['page']<=end and r['sub']==sub for r in records),'expectedByKey':max(keys,default=0)})
print(json.dumps({'imported':len(records),'pending':len(pending),'sections':report},ensure_ascii=False,indent=2))
(OUT/'imported.js').write_text('const IMPORTED_QUESTIONS='+json.dumps(records,ensure_ascii=False)+';\nQUESTIONS.push(...IMPORTED_QUESTIONS);\nfor(const q of IMPORTED_QUESTIONS){let group=TOPICS.find(t=>t[0]===q.topic);if(!group){group=[q.topic,[]];TOPICS.push(group)}if(!group[1].includes(q.sub))group[1].push(q.sub)}\n')
(ROOT/'tools/import-review.json').write_text(json.dumps({'imported':len(records),'pending':pending,'sections':report},ensure_ascii=False,indent=2))
