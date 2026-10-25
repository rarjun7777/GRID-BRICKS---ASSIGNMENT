"""Pure historical analysis. Errors are forecast minus actual, in MW."""
import datetime as dt
import math
from collections import defaultdict
UTC=dt.timezone.utc

def timestamp(value):
    t=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('Timezone required')
    return t.astimezone(UTC)

def metrics(rows):
    errors=[r['error'] for r in rows if r['error'] is not None]
    n=len(errors)
    return {'count':n,'expected':len(rows),'coverage':n/len(rows)*100 if rows else 0,
            'mae':sum(abs(e) for e in errors)/n if n else None,
            'bias':sum(errors)/n if n else None,
            'rmse':math.sqrt(sum(e*e for e in errors)/n) if n else None,
            'maxOverestimate':max([0]+errors) if n else None}

class Analysis:
    def __init__(self,data):
        self.forecasts=defaultdict(list);self.actuals={}
        for r in data['WINDFOR']:
            t=timestamp(r['startTime']);p=timestamp(r['publishTime']);v=r.get('generation')
            if v is None or not math.isfinite(float(v)):continue
            self.forecasts[t].append((p,float(v)))
        for t,versions in self.forecasts.items():
            check={}
            for p,v in versions:
                if p in check and check[p]!=v:raise ValueError('Conflicting forecast versions')
                check[p]=v
            self.forecasts[t]=sorted(check.items())
        # Latest published outturn revision; actuals are retrospective truth, never a forecast input.
        for r in data['FUELHH']:
            if r.get('fuelType')!='WIND' or r.get('generation') is None:continue
            t=timestamp(r['startTime']);p=timestamp(r['publishTime']);v=float(r['generation'])
            if not math.isfinite(v):continue
            old=self.actuals.get(t)
            if old and old[0]==p and old[1]!=v:raise ValueError('Conflicting actual versions')
            if old is None or p>old[0]:self.actuals[t]=(p,v)

    def day(self,decision,cutoff):
        d=dt.date.fromisoformat(decision);clock=dt.time.fromisoformat(cutoff)
        limit=dt.datetime.combine(d,clock,tzinfo=UTC)
        delivery=d+dt.timedelta(days=1);rows=[]
        for hour in range(24):
            target=dt.datetime.combine(delivery,dt.time(hour),tzinfo=UTC)
            eligible=[(p,v) for p,v in self.forecasts.get(target,[]) if p<=limit]
            p,f=eligible[-1] if eligible else (None,None)
            halves=[self.actuals.get(target+dt.timedelta(minutes=m)) for m in (0,30)]
            actual=sum(x[1] for x in halves)/2 if all(x is not None for x in halves) else None
            rows.append({'startTime':target.isoformat(),'hour':f'{hour:02d}:00','forecast':f,'actual':actual,
                         'publishTime':p.isoformat() if p else None,'leadHours':(target-p).total_seconds()/3600 if p else None,
                         'error':f-actual if f is not None and actual is not None else None})
        return {'decisionDate':decision,'deliveryDate':delivery.isoformat(),'cutoff':limit.isoformat(),'rows':rows,'metrics':metrics(rows)}

    def month(self,cutoff):
        days=[self.day(f'2026-01-{d:02d}',cutoff) for d in range(1,32)]
        return {'days':[{'decisionDate':d['decisionDate'],'deliveryDate':d['deliveryDate'],**d['metrics']} for d in days],
                'metrics':metrics([r for d in days for r in d['rows']])}
