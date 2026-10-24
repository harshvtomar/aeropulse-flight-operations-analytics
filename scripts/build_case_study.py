"""Build the portfolio PDF from preserved evidence; requires reportlab 4.4.9."""
from pathlib import Path
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT_DIR=Path(os.environ.get("AEROPULSE_FONT_DIR", "/usr/share/fonts/truetype/dejavu"))
pdfmetrics.registerFont(TTFont("AeroSans", str(FONT_DIR/"DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("AeroSans-Bold", str(FONT_DIR/"DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("AeroSans", normal="AeroSans", bold="AeroSans-Bold", italic="AeroSans", boldItalic="AeroSans-Bold")
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/final/AeroPulse_Portfolio_Case_Study.pdf'
NAVY=colors.HexColor('#17334F'); TEAL=colors.HexColor('#087E8B'); GRAY=colors.HexColor('#536477')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleA',fontName='AeroSans-Bold',fontSize=29,leading=33,textColor=NAVY,spaceAfter=13))
styles.add(ParagraphStyle(name='SectionA',fontName='AeroSans-Bold',fontSize=21,leading=25,textColor=NAVY,spaceAfter=15))
styles.add(ParagraphStyle(name='BodyA',fontName='AeroSans',fontSize=10.5,leading=15.2,textColor=NAVY,spaceAfter=10))
styles.add(ParagraphStyle(name='SmallA',fontName='AeroSans',fontSize=8.3,leading=11.6,textColor=GRAY,spaceAfter=8))
styles.add(ParagraphStyle(name='KickerA',fontName='AeroSans-Bold',fontSize=9,leading=12,textColor=TEAL,spaceAfter=12))
story=[]
def p(text,style='BodyA'):story.append(Paragraph(text,styles[style]))
def title(k,t):p(k,'KickerA');p(t,'SectionA')
def pic(path,maxh):
 img=ImageReader(str(ROOT/path)); w,h=img.getSize(); scale=min(507/w,maxh/h);story.append(Image(str(ROOT/path),w*scale,h*scale));story.append(Spacer(1,10))
def table(rows,widths):
 data=[[Paragraph(str(c),styles['SmallA']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F2F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#DAE3EA'))]));story.append(t);story.append(Spacer(1,12))
def page():story.append(PageBreak())
def footer(c,d):
 c.setStrokeColor(colors.HexColor('#DAE3EA'));c.line(44,39,551,39);c.setFont('AeroSans',8);c.setFillColor(GRAY);c.drawString(44,25,'AEROPULSE INTELLIGENCE | Harsh Vardhan Tomar | Independent portfolio study');c.drawRightString(551,25,str(d.page))

p('OPERATIONS ANALYTICS / Q1 2025','KickerA');p('AeroPulse Intelligence','TitleA');p('Airline Operations, Flight Delay &amp; Network Performance','BodyA')
p('Where should airline operations teams investigate recurring disruption? AeroPulse turns authentic government flight records into reproducible SQL analysis and a public, interactive reporting product. It emphasizes defensible denominators, source traceability and cautious interpretation.')
table([['1,645,503 flights','80.3068% on time','1.8620% cancelled'],['Complete imported quarter','1,611,046 eligible arrivals','All reported flights denominator']],[169,169,169])
pic('reports/session3/screenshots/executive.jpg',330)
p('Actual deployed Streamlit dashboard captured during Session 3 live QA. Seven pages cover executive, airline, airport, route, delay, cancellation/cause and business-insight analysis.','SmallA')
p('<link href="https://aeropulse-flight-operations-analytics.streamlit.app/" color="#087E8B">Open live dashboard</link> | <link href="https://github.com/harshvtomar/aeropulse-flight-operations-analytics" color="#087E8B">Explore code and verification</link>')
p('Status: Streamlit and analytical pipeline implemented; Excel report generated and library/XML checked. Native Microsoft Excel verification and native Power BI report creation/execution remain pending.','SmallA')
page()
title('01 / TRUSTED FOUNDATION','From source records to analytical decisions')
p('<b>Business problem.</b> Raw delay rankings can confuse high traffic with poor reliability, and inconsistent denominators can label cancellations as on time. The project makes these choices explicit before recommending investigation.')
p('<b>Government source.</b> US DOT / Bureau of Transportation Statistics, Reporting Carrier On-Time Performance, January 1-March 31, 2025. All eligible source archives were processed: 14 reporting carriers, 333 airports and 90 calendar dates. Reporting and marketing-carrier datasets are not mixed.')
table([['Stage','Implementation and control'],['Acquire / import','Official monthly ZIP/CSV; SHA-256 manifests; incremental, idempotent imports; revised fingerprints require review.'],['Validate','Schema, parsing, dates, airport codes, statuses, distances, missing fields and duplicate candidates. Raw archives remain intact.'],['Store / model','Monthly Parquet and DuckDB fact/dimensions/audit tables; original source-row identity retained. Six role-aware dimensions in the BI export model.'],['Analyze / reconcile','22 SQL analyses using CTEs, conditional aggregation, joins and windows; independent Python reconciliation.'],['Deliver','Complete minimal 6.8 MB Parquet for Streamlit filters; Excel management report; Power Query/DAX preparation.']],[106,401])
p('<b>Measured quality:</b> 1,645,503 source rows and 1,645,503 accepted rows; zero quarantined rows and zero duplicate candidates in this snapshot. Checks remain active. Five arrival and seven departure extreme warnings resolve to seven unique records, which are preserved.')
p('<b>Identity and statuses:</b> one accepted source row is one fact. Archive checksum and source row provide lineage. Cancelled and diverted flags are independent; neither qualifies a flight for normal arrival analysis. Negative delays preserve early arrival.')
p('Evidence: docs/DATA_PROVENANCE.md; docs/METHODOLOGY.md; reports/DATA_QUALITY_REPORT.md; reports/EXTREME_DELAY_INVESTIGATION.md. Official source: transtats.bts.gov.','SmallA')
page()
title('02 / OPERATIONAL FINDINGS','Prioritize severity, then recurrence')
pic('reports/session2/figures/01_delay_severity.png',240)
p('<b>Severe delays dominate minutes.</b> The 45,759 eligible arrivals delayed at least 120 minutes are 14.42% of delayed arrivals, yet account for 47.75% of their 22,733,373 reported delay minutes. This supports targeted investigation of recurring severe disruptions.')
p('<b>Volume is not reliability.</b> The ten largest destination contributors account for 33.78% of delayed arrivals. DFW contributes 15,484 late arrivals among 72,008 eligible arrivals (21.50% delayed); report counts and rates together.')
p('<b>Recurring signals:</b> 24 destination airports exceed the same-month network delay rate in all three months while retaining at least 1,000 eligible arrivals each month. High-volume examples include ORD, DCA, MCO, MIA and FLL. This is a screening flag, not airport responsibility.')
p('<b>Reported allocations:</b> all 317,266 eligible late arrivals have all five cause fields; total allocated minutes reconcile to late-arrival minutes. Late-arriving aircraft is the largest allocated category. Missing values are never substituted with zero, and reported categories do not independently establish root causes.')
p('Evidence: reports/EXECUTIVE_BUSINESS_INSIGHTS.md; reports/DELAY_CAUSE_ANALYSIS.md; SQL analyses 13, 15-16, 20 and 22. All figures are calculated from authentic records.','SmallA')
page()
title('03 / STATISTICAL DISCIPLINE','Uncertainty and like-for-like comparisons')
table([['Metric','Observed','Day-cluster 95% interval'],['On-time arrival rate','80.3068%','78.3751-82.1702%'],['Cancellation rate','1.8620%','1.3571-2.4335%']],[190,110,207])
p('These are model-based stability summaries. The observed quarter is fully counted. The procedure uses 2,000 seeded whole-day resamples stratified by month, retaining within-day co-movement. It does not fully model cross-day storm persistence or future quarters.')
pic('reports/session2/figures/04_raw_adjusted_comparisons.png',235)
p('<b>Mix matters:</b> AA minus DL on-time performance is -1.87 percentage points across their full networks, +0.84 on overlapping cells and +1.40 after pooled common-support weighting. The retained common population is only 28,510 AA and 25,239 DL eligible flights (12.85% and 11.02%).')
p('Only four of 91 carrier pairs pass the support screens. Pair-specific directed-route / six-hour-block / month references cannot form one adjusted leaderboard. No adjusted confidence interval or causal airline superiority is claimed.')
p('Evidence: reports/STATISTICAL_ANALYSIS.md; reports/MIX_ADJUSTMENT_ANALYSIS.md; docs/STATISTICAL_METHODS.md. Raw and adjusted studies are explicitly separate in the dashboard.','SmallA')
page()
title('04 / PRODUCT AND VERIFICATION','A usable product with auditable measures')
p('<b>Interactive contract:</b> month, airline, origin, destination, directed route, scheduled departure hour and severity filters query the complete fact. Ratios are recomputed from counts; empty populations return explicit states. Minimum-volume screens affect rankings only. CSV downloads include filter context.')
table([['Verification layer','Actual evidence'],['Local automated regression','197 passed: 189 fixtures and 8 genuine-data integrations. Hosted CI deliberately runs fixtures only.'],['Independent reconciliation','Session 2: 286,717 numeric comparisons and 21,390 labels. Deployment: 26 checks and 144 filtered KPI comparisons; all retained records checked in both directions.'],['Public application','Seven pages verified in Chrome; canonical cards, principal filters, reset and downloads; desktop and 390-pixel mobile review.'],['Excel workbook','Eight sheets, seven chart definitions, formula-driven carrier/month controls. Library recalculation and saved XML checked; native chart refresh still pending.'],['Power BI preparation','Seven typed tables, six relationships, DAX and three reference populations prepared. No executed native report or DAX result is claimed.']],[135,372])
pic('reports/session3/excel/previews/Executive.png',200)
p('Excel Executive sheet rendered by the authoring library, not Microsoft Excel. Original chart caches are empty; native open/recalculate/refresh/save/reopen checks remain required.','SmallA')
p('Evidence: reports/session4/ test logs; reports/session3/DATA_PACKAGE_VALIDATION.json; docs/EXCEL_REPORT.md; docs/POWER_BI_SESSION3.md.','SmallA')
page()
title('05 / DECISIONS AND LIMITS','An investigation agenda, not a causal verdict')
table([['Priority','Recommended next investigation','Guardrail'],['1','Recurring 120+ minute delays on high-volume routes and destinations','Display sample sizes, rates and contribution; review event logs.'],['2','Repeated monthly airport gaps by carrier and hour','Separate traffic mix and period shocks from persistent patterns.'],['3','Overlapping airline route/schedule cells','Retain common-support counts; avoid whole-network superiority claims.'],['4','Cancelled extreme-delay source record','Keep original row; seek operational timeline evidence.']],[48,246,213])
p('<b>Scope limitations.</b> One quarter of domestic reporting-carrier operations does not represent all US aviation or full-year seasonality. Minimum samples do not establish significance. Reported delay categories are allocations. Statistical intervals depend on resampling assumptions, and pair-specific adjustment leaves unmeasured factors unresolved.')
p('<b>Delivery limitations.</b> Free hosting can have cold starts. Browser checks cover representative desktop/mobile behavior, not exhaustive accessibility or load certification. Native Excel and Windows Power BI verification are pending because no accessible native execution surface was available. No savings, revenue lift or operational intervention effect is invented.')
p('<b>Next execution:</b> open and verify Excel; use the existing Power BI package on supported Windows, compare all 33 reference values, test relationships/slicers/drill-through/reset, then save and reopen the genuine native report. Do not rebuild the analytical foundation.')
p('Evidence and reproduction','KickerA')
p('<link href="https://github.com/harshvtomar/aeropulse-flight-operations-analytics" color="#087E8B">Repository: github.com/harshvtomar/aeropulse-flight-operations-analytics</link><br/>README provides local commands and current CI. docs/NATIVE_BI_COMPLETION_HANDOFF.md specifies remaining native checks. docs/RESUME_AND_INTERVIEW.md contains truthful resume bullets and 28 interview questions. Source URLs and checksums are recorded in docs/DATA_PROVENANCE.md.','SmallA')
p('Prepared 24 October 2026. Session 4 review builds on verified Session 3 commit fe0915b494d2a9f766b5acee56bbc382a7a2463b. This case study documents an independent portfolio project, with no employer/client involvement or government endorsement asserted.','SmallA')
OUT.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(OUT),pagesize=(595,842),rightMargin=44,leftMargin=44,topMargin=46,bottomMargin=54,title='AeroPulse Intelligence - Portfolio Case Study',author='Harsh Vardhan Tomar').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
