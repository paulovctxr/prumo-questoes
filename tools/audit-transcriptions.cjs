// Structural screening is NOT a mathematical or visual certification.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist');
const katex=require(path.join(dist,'katex.min.js'));
const context={};vm.createContext(context);
for(const name of ['data.js','imported.js'])vm.runInContext(fs.readFileSync(path.join(dist,name),'utf8'),context);
const before=JSON.parse(vm.runInContext('JSON.stringify(QUESTIONS)',context));
vm.runInContext(fs.readFileSync(path.join(dist,'transcription-fixes.js'),'utf8'),context);
const after=JSON.parse(vm.runInContext('JSON.stringify(QUESTIONS)',context));
assert.equal(after.length,2090);
assert.equal(new Set(after.map(q=>q.id)).size,after.length);
const checked=[],counts={},hardFailures=[];
for(let index=0;index<after.length;index++){
  const q=after[index],original=before[index],issues=[];
  assert.equal(q.id,original.id);
  assert.equal(q.answer,original.answer);
  assert.deepEqual(q.source,original.source);
  assert.equal(q.options.length,original.options.length);
  assert.ok(q.text.trim());assert.ok(Number.isInteger(q.answer)&&q.answer>=0&&q.answer<q.options.length);
  const fields=[q.text,...q.options];
  const all=fields.join('\n');
  if(/[\uE000-\uF8FF\uFFFD]/.test(all)){issues.push('unknown-symbol');hardFailures.push(q.id)}
  if(q.options.some(o=>/^Alternativa [A-E](?:\s|$)/i.test(o.trim())))issues.push('placeholder-option');
  if(fields.some(t=>/(?:^|\n)\s*[\u0300-\u036f\u20d0-\u20ff]/u.test(t)))issues.push('detached-math-accent');
  if(q.options.some(o=>o.includes('\n')))issues.push('multiline-option-check-order');
  if(q.text.split('\n').some(l=>/^\s*[−-]?\d+(?:[,.]\d+)?\s*$/.test(l)))issues.push('isolated-number-check-fraction');
  if(/[a-zA-Z][23](?!\d)/.test(all)&&!q.transcriptionReviewed)issues.push('possible-flattened-power');
  if(q.originalExcerpt)issues.push('statement-still-image');
  if(/\b(figura|gráfico|tabela|diagrama)\b/i.test(q.text)&&!q.figure&&!q.originalExcerpt&&!q.image&&q.source)issues.push('check-missing-visual');
  for(const field of ['figure','originalExcerpt','digital','image']){
    if(q[field]&&!fs.existsSync(path.join(dist,q[field]))){issues.push('missing-file:'+field);hardFailures.push(q.id)}
  }
  if(q.transcriptionReviewed){
    assert.ok(!q.originalExcerpt);
    assert.ok(!issues.some(i=>['detached-math-accent','placeholder-option','isolated-number-check-fraction'].includes(i)),`${q.id}: ${issues}`);
    for(const text of fields){
      assert.equal((text.match(/\$/g)||[]).length%2,0,`Delimitador em ${q.id}`);
      for(const [,math] of text.matchAll(/\$([^$]+)\$/g))katex.renderToString(math,{throwOnError:true,strict:'error'});
    }
  }
  for(const issue of issues)counts[issue]=(counts[issue]||0)+1;
  checked.push({id:q.id,topic:q.topic,sub:q.sub,page:q.source?.page??null,visuallyTranscribed:Boolean(q.transcriptionReviewed),issues});
}
const summary={totalScreened:after.length,sourceQuestions:after.filter(q=>q.source).length,symbolsCorrected:after.filter(q=>q.symbolEncodingCorrected).length,visuallyTranscribed:after.filter(q=>q.transcriptionReviewed).length,changedRecords:after.filter((q,i)=>q.text!==before[i].text||JSON.stringify(q.options)!==JSON.stringify(before[i].options)).length,remainingFlagged:checked.filter(q=>q.issues.length).length,hardFailures:[...new Set(hardFailures)],counts};
assert.equal(summary.hardFailures.length,0);
const report={scope:'Triagem estrutural de todo o acervo. Ausência de alerta NÃO comprova correção matemática. Conferência visual desta revisão: Circunferências de geometria plana, questões 1–35, páginas 154–158.',summary,questions:checked};
fs.writeFileSync(path.join(__dirname,'transcription-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
