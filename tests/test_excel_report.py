"""Read-only ZIP/XML checks; workbook authoring remains in artifact-tool JS."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'reports/session3/excel'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

def inspect_export():
    with zipfile.ZipFile(OUTPUT / 'AeroPulse_Airline_Operations_Business_Report.xlsx') as z:
        book = ET.fromstring(z.read('xl/workbook.xml'))
        names = [e.attrib['name'] for e in book.findall('m:sheets/m:sheet', NS)]
        sheets = [ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')) for i in range(1, 9)]
        def cell(index, address):
            return sheets[index].find(f'.//m:c[@r="{address}"]', NS)
        def number(index, address):
            return float(cell(index, address).find('m:v', NS).text)
        errors = [c.attrib['r'] for s in sheets for c in s.findall('.//m:c', NS) if c.attrib.get('t') == 'e']
        assert not errors
        assert len(names) == 8
        assert number(0, 'B9') == 1645503
        assert number(0, 'B10') == 1611046
        assert abs(number(0, 'B18') - 1293780 / 1611046) < 1e-12
        for r in range(6, 20):
            expected = (number(1, f'C{r}') - number(1, f'D{r}')) / number(1, f'C{r}')
            assert abs(number(1, f'F{r}') - expected) < 1e-12
        validations = sheets[0].findall('m:dataValidations/m:dataValidation', NS)
        assert {v.attrib['sqref'] for v in validations} == {'B5', 'B6'}
        charts = []
        for f in z.namelist():
            if '/charts/chart' not in f or not f.endswith('.xml'):
                continue
            chart = ET.fromstring(z.read(f))
            refs = [x.text for x in chart.findall('.//c:f', NS)]
            assert len(refs) == 2 and all('!' in x for x in refs)
            colors = [x.attrib['val'] for x in chart.findall('.//c:ser//a:srgbClr', NS)]
            assert '087E8B' in colors
            charts.append({'part': f, 'references': refs,
                           'cache_point_counts': [int(x.attrib['val']) for x in chart.findall('.//c:ptCount', NS)]})
        assert len(charts) == 7
        assert charts[0]['references'] == ["'Executive'!$D$10:$D$12", "'Executive'!$E$10:$E$12"]
        assert any("'Severity'!$B$6:$B$10" in c['references'] for c in charts)
        return {'passed': True, 'sheets': names, 'charts': charts,
                'cached_formula_errors': errors, 'validated_controls': ['B5', 'B6'],
                'native_excel_tested': False,
                'limitation': 'Chart source references are present; chart caches are empty. Native Excel open/refresh/render has not been tested.'}

def test_excel_export():
    assert inspect_export()['passed']

if __name__ == '__main__':
    result = inspect_export()
    (OUTPUT / 'EXCEL_XML_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'sheets': len(result['sheets']), 'charts': len(result['charts'])}))
