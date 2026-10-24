# Portfolio deliverables

AeroPulse_Portfolio_Case_Study.pdf is a six-page case study based on preserved BTS analysis and actual dashboard/authoring-library screenshots. No native Power BI or Excel verification is claimed.

Rebuild from repository root with `python -m pip install -r requirements-report.txt` and `python scripts/build_case_study.py`. Install DejaVu Sans regular/bold fonts and set AEROPULSE_FONT_DIR to their folder on systems where /usr/share/fonts/truetype/dejavu is unavailable. PDF authoring dependencies are separate from application dependencies. Render using `pdftoppm -png` and visually review every page after edits. The source screenshot dates/scopes are labeled in the PDF; they are not fabricated native BI screenshots.

Resume bullets and 28 interview questions: docs/RESUME_AND_INTERVIEW.md. Remaining native execution: docs/NATIVE_BI_COMPLETION_HANDOFF.md. Tests and verification evidence: reports/session4/.
