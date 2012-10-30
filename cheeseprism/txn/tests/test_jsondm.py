from functools import wraps
from path import path
import json
import transaction

def coro(func):
    @wraps(func)
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

@coro
def appender(outlist):
    while True:
        payload = (yield)
        outlist.append(json.dumps(payload))

def makeone_json(sender):
    from cheeseprism.txn import datamanager
    t = transaction.get()
    dm = datamanager.JSON(sender)
    t.join(dm)
    return t, dm

def makeone_file(fp):
    from cheeseprism.txn import datamanager
    t = transaction.get()
    dm = datamanager.JSONFile(fp)
    t.join(dm)
    return t, dm

def test_jsondm():
    outlist = []
    sender = appender(outlist).send
    txn, dm = makeone_json(sender)
    dm['entry_one'] = 1
    dm['entry_two'] = dict(hello='world')
    txn.commit()
    assert len(outlist) == 1
    results = json.loads(outlist[0])
    assert 'entry_one' in results

def test_jsonfiledm_create():
    txn, dm = makeone_file('tmp.json')
    dm['entry_one'] = 1
    dm['entry_two'] = dict(hello='world')
    txn.commit()
    assert dm.filepath.exists()
    with open(dm.filepath) as stream:
        data = json.load(stream)
    assert 'entry_one' in data

def test_exists():
    fp = path('tmp.json')
    fp.write_text('{}')
    txn, dm = makeone_file(fp)
    dm['entry_one'] = 1
    dm['entry_two'] = dict(hello='world')
    txn.commit()
    assert dm.filepath.exists()
    with open(dm.filepath) as stream:
        data = json.load(stream)
    assert 'entry_one' in data
    fp.remove()


