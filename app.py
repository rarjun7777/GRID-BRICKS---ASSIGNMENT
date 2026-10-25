import csv,gzip,io,json,re
from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from backend.analysis import Analysis
ROOT=Path(__file__).resolve().parent
app=FastAPI(title='Winddesk API',version='1.0.0',description='January 2026 day-ahead wind forecast evaluation. MW; UTC; errors = forecast − actual.')
@lru_cache(maxsize=1)
def engine():
    try:
        with gzip.open(ROOT/'data/snapshot.json.gz','rt') as f:return Analysis(json.load(f))
    except (OSError,ValueError,KeyError) as e:raise HTTPException(503,'Snapshot unavailable or invalid. Run scripts/fetch_data.py.') from e

def validate(decision,cutoff):
    if not re.fullmatch(r'2026-01-(0[1-9]|[12][0-9]|3[01])',decision):raise HTTPException(422,'Decision date must be in January 2026.')
    if not re.fullmatch(r'([01][0-9]|2[0-3]):[0-5][0-9]',cutoff):raise HTTPException(422,'Cutoff must be HH:MM, UTC.')

@app.get('/api/health')
def health():
    engine();return {'status':'ok','source':'Elexon snapshot'}

@app.get('/api/dashboard')
@lru_cache(maxsize=256)
def dashboard(decision:str=Query('2026-01-14'),cutoff:str=Query('09:00')):
    validate(decision,cutoff)
    e=engine();day=e.day(decision,cutoff)
    return {'day':day,'month':e.month(cutoff),'provenance':json.loads((ROOT/'data/provenance.json').read_text()),
            'methodology':{'unit':'MW','timezone':'UTC (GMT in January)','alignment':'Hourly forecast vs mean of both half-hour actuals; incomplete pairs excluded.',
            'selection':'Latest publication at or before decision cutoff for each next-day hour.',
            'bias':'Positive = overestimated wind; negative = underestimated wind.',
            'scope':'National operational wind data; not client-specific procurement advice. Monthly metrics are retrospective.'}}

@app.get('/api/export')
def export(decision:str='2026-01-14',cutoff:str='09:00'):
    validate(decision,cutoff);rows=engine().day(decision,cutoff)['rows']
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=['startTime','hour','forecast','actual','publishTime','leadHours','error']);writer.writeheader();writer.writerows(rows)
    return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="winddesk-{decision}-{cutoff.replace(":","")}.csv"'})

if (ROOT/'public/assets').exists():app.mount('/assets',StaticFiles(directory=ROOT/'public/assets'),name='assets')
@app.get('/',include_in_schema=False)
def index():
    if not (ROOT/'public/index.html').exists():raise HTTPException(503,'Build frontend first: npm ci --prefix frontend && npm run build --prefix frontend')
    return FileResponse(ROOT/'public/index.html')
