"""Download reproducible Elexon snapshots; failures never generate synthetic data."""
import concurrent.futures, datetime as dt, gzip, hashlib, json, pathlib, time
from urllib.request import urlopen
from urllib.parse import urlencode
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://data.elexon.co.uk/bmrs/api/v1/datasets/'
def fetch(job):
    dataset,day=job
    end=day+dt.timedelta(days=1)
    params=({'publishDateTimeFrom':day.isoformat()+'T00:00:00Z','publishDateTimeTo':end.isoformat()+'T00:00:00Z'} if dataset=='WINDFOR' else {'settlementDateFrom':day.isoformat(),'settlementDateTo':day.isoformat(),'fuelType':'WIND'})
    url=BASE+dataset+'/stream?'+urlencode(params)
    for attempt in range(4):
        try:
            with urlopen(url,timeout=60) as response: rows=json.load(response)
            if not isinstance(rows,list): raise ValueError('Unexpected payload')
            if dataset=='FUELHH': rows=[r for r in rows if r.get('fuelType')=='WIND']
            return dataset,rows,url
        except Exception:
            if attempt==3: raise
            time.sleep(2**attempt)
def main():
    jobs=[('WINDFOR',dt.date(2025,12,31)+dt.timedelta(days=i)) for i in range(32)]
    jobs += [('FUELHH',dt.date(2026,1,2)+dt.timedelta(days=i)) for i in range(31)]
    data={'WINDFOR':[],'FUELHH':[]};urls=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for dataset,rows,url in pool.map(fetch,jobs):
            data[dataset].extend(rows);urls.append(url);print(dataset,len(rows),flush=True)
    # Exact duplicate removal; conflicting versions retained for explicit validation.
    for name,rows in data.items():
        unique={json.dumps(r,sort_keys=True):r for r in rows}
        data[name]=list(unique.values())
    content=json.dumps(data,separators=(',',':')).encode()
    path=ROOT/'data/snapshot.json.gz'
    with gzip.open(path,'wb') as f:f.write(content)
    meta={'source':'Elexon Insights API','retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'sha256':hashlib.sha256(content).hexdigest(),'counts':{k:len(v) for k,v in data.items()},'requests':urls}
    (ROOT/'data/provenance.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta['counts']))
if __name__=='__main__':main()
