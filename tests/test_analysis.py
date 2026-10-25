import math
from backend.analysis import Analysis,metrics

def f(p,v=100,t='2026-01-02T00:00:00Z'):
    return dict(startTime=t,publishTime=p,generation=v)
def a(t,v):return {**f('2026-01-03T00:00:00Z',v,t),'fuelType':'WIND'}
def test_cutoff_and_hourly_alignment():
    e=Analysis({'WINDFOR':[f('2026-01-01T08:00:00Z',100),f('2026-01-01T09:00:00Z',120),f('2026-01-01T09:01:00Z',900)],'FUELHH':[a('2026-01-02T00:00:00Z',60),a('2026-01-02T00:30:00Z',100)]})
    d=e.day('2026-01-01','09:00');r=d['rows'][0]
    assert r['forecast']==120 and r['actual']==80 and r['error']==40
    assert d['metrics']['count']==1 and len(d['rows'])==24
    assert d['metrics']['mae']==40

def test_missing_half_hour_not_zero_filled():
    e=Analysis({'WINDFOR':[f('2026-01-01T08:00:00Z')],'FUELHH':[a('2026-01-02T00:00:00Z',0)]})
    r=e.day('2026-01-01','09:00')['rows'][0]
    assert r['actual'] is None and r['error'] is None

def test_zero_is_valid():
    e=Analysis({'WINDFOR':[f('2026-01-01T08:00:00Z',0)],'FUELHH':[a('2026-01-02T00:00:00Z',0),a('2026-01-02T00:30:00Z',0)]})
    d=e.day('2026-01-01','09:00');assert d['metrics']['count']==1 and d['metrics']['mae']==0

def test_month_boundary():
    e=Analysis({'WINDFOR':[],'FUELHH':[]})
    assert e.day('2026-01-31','09:00')['deliveryDate']=='2026-02-01'
    assert e.month('09:00')['metrics']['expected']==744

def test_no_future_forecast_fallback():
    e=Analysis({'WINDFOR':[f('2026-01-01T10:00:00Z')],'FUELHH':[]})
    assert e.day('2026-01-01','09:00')['rows'][0]['forecast'] is None

def test_metrics_sign_and_magnitude():
    m=metrics([{'error':3},{'error':-4},{'error':None}])
    assert m['mae']==3.5 and m['bias']==-.5 and m['rmse']==math.sqrt(12.5)
    assert m['count']==2 and m['expected']==3

def test_duplicate_conflict_rejected():
    import pytest
    with pytest.raises(ValueError):Analysis({'WINDFOR':[f('2026-01-01T08:00:00Z',1),f('2026-01-01T08:00:00Z',2)],'FUELHH':[]})

def test_actual_revisions_use_latest():
    old=a('2026-01-02T00:00:00Z',20);new={**old,'generation':40,'publishTime':'2026-01-04T00:00:00Z'}
    e=Analysis({'WINDFOR':[],'FUELHH':[new,old,a('2026-01-02T00:30:00Z',60)]})
    assert e.day('2026-01-01','09:00')['rows'][0]['actual']==50
