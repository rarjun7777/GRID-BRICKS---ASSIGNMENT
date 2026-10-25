import csv,io,datetime as dt,gzip,hashlib,json
from fastapi.testclient import TestClient
from app import app,ROOT,engine
client=TestClient(app)
def test_real_snapshot_and_boundary():
    r=client.get('/api/dashboard?decision=2026-01-31&cutoff=09:00');assert r.status_code==200
    d=r.json();assert d['day']['deliveryDate']=='2026-02-01'
    assert d['month']['metrics']['expected']==744
    assert d['month']['metrics']['count']==744
    assert all(x['publishTime']<=d['day']['cutoff'] for x in d['day']['rows'] if x['publishTime'])

def test_input_validation():
    for query in ['decision=2026-02-01','cutoff=24:00','decision=garbage','cutoff=9:00','decision=2026-01-00']:
        assert client.get('/api/dashboard?'+query).status_code==422

def test_csv():
    r=client.get('/api/export?decision=2026-01-14&cutoff=09:00')
    assert r.status_code==200 and 'attachment' in r.headers['content-disposition']
    rows=list(csv.DictReader(io.StringIO(r.text)));assert len(rows)==24
    assert float(rows[0]['forecast'])-float(rows[0]['actual'])==float(rows[0]['error'])

def test_snapshot_integrity():
    raw=gzip.decompress((ROOT/'data/snapshot.json.gz').read_bytes())
    provenance=json.loads((ROOT/'data/provenance.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==provenance['sha256']

def test_all_cutoffs_have_no_leakage():
    e=engine()
    for cutoff in ['00:00','09:00','12:30','23:59']:
        for day in range(1,32):
            d=e.day(f'2026-01-{day:02d}',cutoff)
            for r in d['rows']:
                if r['publishTime']:assert dt.datetime.fromisoformat(r['publishTime'])<=dt.datetime.fromisoformat(d['cutoff'])

def test_frontend_and_health():
    assert client.get('/').status_code==200
    assert 'winddesk' in client.get('/').text.lower()
    assert client.get('/api/health').json()['status']=='ok'
