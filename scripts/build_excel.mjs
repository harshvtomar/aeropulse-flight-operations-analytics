/** Reproducible artifact-tool workbook. Run as documented in docs/EXCEL_REPORT.md. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(process.argv[2]||process.cwd());
const out=path.join(root,'reports/session3/excel');
await fs.mkdir(path.join(out,'previews'),{recursive:true});
const inputs=[];
async function csv(file){
 const text=await fs.readFile(path.join(root,file),'utf8');
 inputs.push({file,sha256:crypto.createHash('sha256').update(text).digest('hex')});
 // Source exports contain no embedded newlines; honor quoted commas/escaped quotes.
 const lines=text.trim().split(/\r?\n/).map(l=>{const a=[];let v='',q=false;for(let i=0;i<l.length;i++){const c=l[i];if(c==='"'){if(q&&l[i+1]==='"'){v+='"';i++;}else q=!q;}else if(c===','&&!q){a.push(v);v='';}else v+=c;}a.push(v);return a;});
 const h=lines.shift();return lines.map(a=>Object.fromEntries(h.map((k,i)=>[k,a[i]===''?null:(/^-?\d+(\.\d+)?$/.test(a[i])?Number(a[i]):a[i])])));
}
const daily=await csv('data/bi/agg_daily_airline.csv'), dim=await csv('data/bi/dim_airlines.csv');
const airports=await csv('reports/session2/sql/16_airport_concentration.csv');
const routes=await csv('reports/session2/sql/15_route_concentration.csv');
const severity=await csv('reports/session2/sql/13_delay_severity.csv');
const causes=await csv('data/bi/agg_delay_causes.csv'), cancellations=await csv('data/bi/agg_cancellations.csv');
const codes=Object.fromEntries(dim.map(d=>[d.airline_id,d.airline_code]));
const measures=['reported_flights','eligible_arrivals','on_time_arrivals','late_arrivals','cancellations','diversions','eligible_delay_minutes','late_delay_minutes'];
const groups=new Map();for(const d of daily){const m=String(d.date_key).slice(0,4)+'-'+String(d.date_key).slice(4,6),key=m+'|'+d.airline_id;if(!groups.has(key))groups.set(key,{month:m,code:codes[d.airline_id],id:d.airline_id,...Object.fromEntries(measures.map(k=>[k,0]))});const x=groups.get(key);for(const k of measures)x[k]+=d[k];}
const monthly=[...groups.values()].sort((a,b)=>a.month.localeCompare(b.month)||a.code.localeCompare(b.code));
const totals=Object.fromEntries(measures.map(k=>[k,daily.reduce((s,d)=>s+d[k],0)]));
const wb=Workbook.create();
const names=['Executive','Airlines','Airports','Routes','Severity','Disruptions','Monthly source','Methodology'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const blue='#153451',teal='#087E8B',gray='#EAF0F5';
function setup(n,title,scope,width=12,rows=38){const s=sheets[n];s.showGridLines=false;s.getRangeByIndexes(0,0,rows,width).format={font:{name:'Arial',size:11,color:'#223448'},rowHeight:24,columnWidth:15,verticalAlignment:'center'};s.getRange('A:A').format.columnWidth=27;s.getRange('A2').values=[[title]];s.getRange('A2').format.font={name:'Arial',size:17,bold:true,color:blue};s.getRange('A3').values=[[scope]];s.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#52687A'};s.tabColor=blue;return s;}
function header(s,r,labels){s.getRangeByIndexes(r-1,0,1,labels.length).values=[labels];s.getRangeByIndexes(r-1,0,1,labels.length).format={fill:blue,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:38,wrapText:true,horizontalAlignment:'center'};}
function table(s,r,labels,rows,name){header(s,r,labels);s.getRangeByIndexes(r,0,rows.length,labels.length).values=rows;s.getRangeByIndexes(r,1,rows.length,labels.length-1).setNumberFormat('#,##0');s.tables.add(`A${r}:${col(labels.length)}${r+rows.length}`,true,name);s.freezePanes.freezeRows(r);}
function col(n){let t='';while(n){n--;t=String.fromCharCode(65+n%26)+t;n=Math.floor(n/26);}return t;}
function formula(s,cell,f){s.getRange(cell).formulas=[[f]];}
function ratio(s,cell,num,den){formula(s,cell,`=IF(${den}=0,"n.a.",(${num})/(${den}))`);s.getRange(cell).setNumberFormat('0.0%');}
function chart(s,cat,val,title,pos=['H6','M21'],fmt='#,##0',type='bar'){const c=s.charts.add(type,[s.getRange(cat),s.getRange(val)]);c.title=title;c.hasLegend=false;c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=14;c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:11}};c.yAxis={numberFormatCode:fmt,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:11}};c.setPosition(...pos);c.series.items[0].fill=teal;if(type==='line')c.series.items[0].line={fill:teal,style:'solid',width:2};return c;}
const src=setup('Monthly source','Airline-month source','BTS accepted flights aggregated from daily airline export. January–March 2025.',10,49);
table(src,5,['Month','Carrier','Reported','Eligible','On time','Late','Cancelled','Diverted','Signed delay min','Late delay min'],monthly.map(d=>[d.month,d.code,...measures.map(k=>d[k])]),'MonthlyInputs');
src.getRange('A49').values=[['Source: BTS Reporting Carrier On-Time Performance. Source fingerprints and refresh details: Methodology.']];
const end=5+monthly.length;
const ex=setup('Executive','AeroPulse airline operations','January–March 2025. Select a carrier and month for this sheet only.',13,39);
ex.getRange('A5:B6').values=[['Carrier','All'],['Month','All']];ex.getRange('B5:B6').format.fill='#FFF1BF';
ex.getRange('B5').dataValidation={rule:{type:'list',values:['All',...dim.map(d=>d.airline_code).sort()]}};
ex.getRange('B6').dataValidation={rule:{type:'list',values:['All','2025-01','2025-02','2025-03']}};
ex.getRange('D5').values=[['Amber cells are editable. Other sheets show fixed Q1 results.']];
header(ex,8,['Metric','Selected value']);
const labels=['Reported flights','Eligible arrivals','On-time arrivals','Late arrivals','Cancellations','Diversions','Signed delay minutes','Late delay minutes'];
for(let i=0;i<8;i++){const r=9+i,c=col(i+3);ex.getRange(`A${r}`).values=[[labels[i]]];formula(ex,`B${r}`,`=SUMIFS('Monthly source'!$${c}$6:$${c}$${end},'Monthly source'!$B$6:$B$${end},IF($B$5="All","*",$B$5),'Monthly source'!$A$6:$A$${end},IF($B$6="All","*",$B$6))`);}
ex.getRange('B9:B16').setNumberFormat('#,##0');
const rs=[['On-time arrival rate','B11','B10'],['Late arrival rate','B12','B10'],['Cancellation rate','B13','B9'],['Diversion rate','B14','B9']];
rs.forEach(([l,n,d],i)=>{ex.getRange(`A${18+i}`).values=[[l]];ratio(ex,`B${18+i}`,n,d);});
ex.getRange('A23').values=[['Mean arrival delay (min)']];formula(ex,'B23','=IF(B10=0,"n.a.",B15/B10)');ex.getRange('B23').setNumberFormat('0.0');
ex.getRange('D9:E12').values=[['Month','On-time rate'],['Jan 2025',null],['Feb 2025',null],['Mar 2025',null]];
for(let i=0;i<3;i++){const r=10+i,m=`2025-0${i+1}`;const su=c=>`SUMIFS('Monthly source'!$${c}$6:$${c}$${end},'Monthly source'!$B$6:$B$${end},IF($B$5="All","*",$B$5),'Monthly source'!$A$6:$A$${end},"${m}")`;formula(ex,`E${r}`,`=IF(${su('D')}=0,"n.a.",${su('E')}/${su('D')})`);}ex.getRange('E10:E12').setNumberFormat('0.0%');chart(ex,'D9:D12','E9:E12','Selected carrier: Q1 monthly on-time rate',['D14','M26'],'0%','line');
ex.getRange('A27').values=[['Operational priorities for Q1']];ex.getRange('A27').format.font={bold:true,color:blue};
ex.getRange('A29').values=[['1. Review DFW recovery capacity: it contributes the most late arrivals (15,484).']];
ex.getRange('A31').values=[['2. Investigate long delays: the 120+ minute band is 14.4% of late flights but 47.8% of late minutes.']];
ex.getRange('A33').values=[['3. Examine carrier and late-aircraft allocations before interventions; reported causes are not causal proof.']];
ex.getRange('A35').values=[['4. Review weather cancellation contingencies with station teams. Use exposure-matched rates and volumes.']];
ex.getRange('A37').values=[['Rates use matching totals. Eligible: noncancelled, nondiverted, known arrival delay. On time: delay <15 min.']];
const air=setup('Airlines','Airline performance','Fixed Q1 2025. Raw operating rates reflect different route and schedule mixes.',13,26);
const airs=dim.map(d=>({code:d.airline_code,...Object.fromEntries(measures.map(k=>[k,monthly.filter(x=>x.code===d.airline_code).reduce((s,x)=>s+x[k],0)]))})).sort((a,b)=>b.late_arrivals-a.late_arrivals);
table(air,5,['Carrier','Reported','Eligible','Late','Cancelled','On-time rate','Cancel rate'],airs.map(d=>[d.code,d.reported_flights,d.eligible_arrivals,d.late_arrivals,d.cancellations,null,null]),'AirlineResults');
airs.forEach((d,i)=>{const r=i+6;ratio(air,`F${r}`,`C${r}-D${r}`,`C${r}`);ratio(air,`G${r}`,`E${r}`,`B${r}`);});chart(air,'A5:A19','D5:D19','Late arrivals by carrier',['I5','N23']);
function concentration(n,title,data,isRoute){const s=setup(n,title,`Fixed Q1 2025. Top 20 by late-flight contribution${isRoute?'; directed routes with ≥1,000 eligible arrivals.':'; destination airports.'}`,14,29);table(s,5,[isRoute?'Directed route':'Destination','Reported','Eligible','Late','Cancelled','Late rate','Network late share'],data.map(d=>[isRoute?`${d.Origin} → ${d.Dest}`:d.Dest,d.reported_flights,d.eligible_flights,d.delayed_flights,d.cancelled_flights,null,null]),n+'Results');data.forEach((d,i)=>{const r=i+6;ratio(s,`F${r}`,`D${r}`,`C${r}`);ratio(s,`G${r}`,`D${r}`,String(totals.late_arrivals));});chart(s,'A5:A15','D5:D15','Top 10 late-flight contributions',['I5','N24']);return s;}
concentration('Airports','Airport delay concentration',airports.slice(0,20),false);
concentration('Routes','Route delay concentration',routes.filter(d=>d.eligible_flights>=1000).slice(0,20),true);
const sev=setup('Severity','Arrival delay severity','Fixed Q1 2025. Eligible flights only. Negative arrival delays remain signed.',13,30);
table(sev,5,['Arrival delay','Flights','Signed minutes','Eligible share','Late-flight share','Late-minute share'],severity.map(d=>[d.severity.replace(/^\d /,''),d.flights,d.signed_arrival_minutes,null,null,null]),'SeverityResults');
severity.forEach((d,i)=>{const r=i+6;ratio(sev,`D${r}`,`B${r}`,'SUM($B$6:$B$10)');if(i){ratio(sev,`E${r}`,`B${r}`,'SUM($B$7:$B$10)');ratio(sev,`F${r}`,`C${r}`,'SUM($C$7:$C$10)');}else{sev.getRange(`E${r}:F${r}`).values=[['n.a.','n.a.']];}});chart(sev,'A6:A10','B6:B10','Flights by severity',['H5','M22']);
sev.getRange('A25').values=[['120+ minute flights account for almost half of all late-arrival minutes.']];
const dis=setup('Disruptions','Cancellations and reported causes','Fixed Q1 2025. Cancellation reasons and delay-minute allocations are different populations.',13,39);
const reasons={A:'Carrier',B:'Weather',C:'National airspace',D:'Security',UNKNOWN:'Unknown'};
const cancel=Object.entries(reasons).map(([k,v])=>[v,cancellations.filter(d=>d.cancellation_code===k).reduce((s,d)=>s+d.cancellations,0),null]);
table(dis,5,['Cancellation reason','Cancelled flights','Reason share'],cancel,'CancellationReasons');for(let r=6;r<=10;r++)ratio(dis,`C${r}`,`B${r}`,'SUM($B$6:$B$10)');
const cats=[...new Set(causes.map(d=>d.reported_cause))].map(c=>{const a=causes.filter(d=>d.reported_cause===c);return[c,a.reduce((s,d)=>s+(d.reported_minutes??0),0),a.reduce((s,d)=>s+d.late_records_with_value,0),a.reduce((s,d)=>s+d.late_arrivals,0),null,null];}).sort((a,b)=>b[1]-a[1]);
table(dis,15,['Reported cause','Reported minutes','Late rows reported','Late arrivals','Coverage','Minute share'],cats,'ReportedCauses');
for(let r=16;r<=20;r++){ratio(dis,`E${r}`,`C${r}`,`D${r}`);ratio(dis,`F${r}`,`B${r}`,'SUM($B$16:$B$20)');}
chart(dis,'A5:A10','B5:B10','Cancellation reasons',['H5','M18']);chart(dis,'A15:A20','B15:B20','Reported delay minutes',['H20','M35']);
dis.getRange('A23').values=[['Coverage counts nonmissing cause values, including reported zeros.']];
dis.getRange('A25').values=[['The late-arrival denominator repeats by cause. Do not sum it across categories.']];
dis.getRange('A27').values=[['Missing cause values are not evidence of zero delay. Allocations do not establish causality.']];
const method=setup('Methodology','Methodology and refresh','Scope, sources and interpretation',9,37);
const notes=[['Coverage','BTS Reporting Carrier On-Time Performance, January–March 2025.'],['Population','1,645,503 accepted source records. No sampling or duplicate-looking row collapse.'],['Eligibility','Cancelled=0, Diverted=0, and a nonmissing signed arrival delay.'],['On time / late','On time: arrival delay <15 minutes. Late: arrival delay ≥15 minutes.'],['Rates','Ratios of matching summed counts. No averaging of row percentages.'],['Cancellations','Cancelled / all reported flights. Reason shares use cancelled flights only.'],['Controls','Executive B5 and B6 change its selected KPIs. Its trend uses carrier only and always shows all three months.'],['Fixed views','Airline, airport, route, severity and disruption views always show Q1, independent of Executive controls.'],['Rankings','Airport: top 20 destination contributions. Route: top 20 contributions among routes ≥1,000 eligible arrivals.'],['Comparison','Raw rates describe operations, not causal carrier quality. Route mix, schedules and disruption exposure differ.'],['Source grain','Monthly source aggregates the daily airline export to 42 month/carrier rows.'],['Other inputs','Session 2 SQL concentration/severity outputs and BI cancellation/cause exports.'],['Refresh','Rebuild canonical warehouse and BI/Session 2 exports, then run scripts/build_excel.mjs per EXCEL_REPORT.md.'],['Validation','Formula recalculation and input changes tested in artifact-tool. Native Excel application testing not performed.'],['Publisher','US DOT Bureau of Transportation Statistics. Accessed 22 October 2026.'],['Official source','https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFD']];
notes.forEach(([a,b],i)=>{const r=i+5;method.getRange(`A${r}:B${r}`).values=[[a,b]];method.getRange(`A${r}`).format.font={bold:true,color:blue};});method.getRange('B:B').format.columnWidth=112;method.getRange('B5:B20').format.wrapText=true;method.getRange('A5:B20').format.rowHeight=38;
method.getRange('A23').values=[['Source CSV SHA-256 fingerprints']];for(let i=0;i<inputs.length;i++)method.getRange(`A${25+i}:B${25+i}`).values=[[path.basename(inputs[i].file),inputs[i].sha256]];method.getRange('A25:A31').format.columnWidth=32;
sev.getRange('E6:F6').format.horizontalAlignment='right';
wb.recalculate();
const rateChecks=[];
for(let i=0;i<airs.length;i++){const r=6+i,actual=air.getRange(`F${r}`).values[0][0],expected=airs[i].on_time_arrivals/airs[i].eligible_arrivals;if(Math.abs(actual-expected)>1e-12)throw Error(`Airline rate mismatch: ${airs[i].code}`);rateChecks.push({carrier:airs[i].code,expected,actual,passed:true});}
if(cancel.reduce((s,r)=>s+r[1],0)!==totals.cancellations)throw Error('Cancellation reconciliation');
if(severity.reduce((s,r)=>s+r.flights,0)!==totals.eligible_arrivals)throw Error('Severity reconciliation');
if(airports.reduce((s,r)=>s+r.delayed_flights,0)!==totals.late_arrivals)throw Error('Airport reconciliation');
if(routes.reduce((s,r)=>s+r.delayed_flights,0)!==totals.late_arrivals)throw Error('Route reconciliation');
const controls=[];
for(const [carrier,month] of [['All','All'],['WN','2025-02'],['AA','2025-03'],['INVALID','2025-01'],['','All']]){ex.getRange('B5:B6').values=[[carrier],[month]];wb.recalculate();const selected=monthly.filter(d=>(carrier==='All'||d.code===carrier)&&(month==='All'||d.month===month));const expected=Object.fromEntries(measures.map(k=>[k,selected.reduce((s,d)=>s+d[k],0)]));const observed=ex.getRange('B9:B16').values.map(r=>r[0]);for(let i=0;i<8;i++)if(observed[i]!==expected[measures[i]])throw Error(`Control mismatch ${carrier} ${month} ${measures[i]}: ${observed[i]}`);const rate=ex.getRange('B18').values[0][0],want=expected.eligible_arrivals?expected.on_time_arrivals/expected.eligible_arrivals:'n.a.';if(typeof want==='number'?Math.abs(rate-want)>1e-12:rate!==want)throw Error('Rate mismatch');controls.push({carrier,month,reported:observed[0],on_time_rate:rate,passed:true});}
ex.getRange('B5:B6').values=[['All'],['All']];wb.recalculate();
const inspect=await wb.inspect({kind:'table',range:'Executive!A8:B23',include:'values,formulas',tableMaxRows:16,tableMaxCols:2,maxChars:10000});
await fs.writeFile(path.join(out,'formula_inspection.ndjson'),inspect.ndjson);
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Formula error scan'});
await fs.writeFile(path.join(out,'formula_error_scan.ndjson'),err.ndjson);
const chartBindings=[];for(const n of names)for(const c of sheets[n].charts.items)chartBindings.push({sheet:n,series:c.series.items.map(s=>({formula:s.formula,categories:s.categoryFormula}))});
for(const n of names){const ranges={Executive:'A1:M38',Airlines:'A1:N25',Airports:'A1:N28',Routes:'A1:N28',Severity:'A1:M28',Disruptions:'A1:M37','Monthly source':'A1:J22',Methodology:'A1:B32'};const blob=await wb.render({sheetName:n,range:ranges[n],scale:1,format:'png'});await fs.writeFile(path.join(out,'previews',n.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'AeroPulse_Airline_Operations_Business_Report.xlsx'));
await fs.writeFile(path.join(out,'EXCEL_VALIDATION.json'),JSON.stringify({engine:'@oai/artifact-tool',native_excel_tested:false,source_rows:totals.reported_flights,monthly_rows:monthly.length,totals,control_tests:controls,airline_rate_checks:rateChecks,source_reconciliations:['cancellations','severity','airport late flights','route late flights'],chartBindings,rendered_sheets:names,inputs},null,2)+'\n');
console.log(JSON.stringify({output:out,sheets:names.length,charts:chartBindings.length,controls:controls.length}));
