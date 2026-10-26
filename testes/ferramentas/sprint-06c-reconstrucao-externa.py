"""Verify externally rebuilt artifacts against the preserved 06B source baseline."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tarfile
import tomllib
import zipfile

DOCS=Path(__file__).resolve().parents[2];ROOT=DOCS.parent
prior=json.loads((DOCS/'testes/sprint-06b-evidencias.json').read_text())
current=json.loads((DOCS/'testes/sprint-06c-evidencias.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
# No source, artifact, or installed composition input has changed since the successful tests.
for field in ['source_files_sha256','artifact_sha256']:
    for path,digest in current[field].items():assert sha(ROOT/path)==digest,(field,path)
proof=[]
for project,package in [('cripto-core','cripto_core'),('cripto-bot','cripto_bot')]:
    source={p.removeprefix(project+'/src/'):h for p,h in prior['source_files_sha256'].items() if p.startswith(project+'/src/')}
    wheel=ROOT/project/f'dist/06a-final/{package}-0.1.0-py3-none-any.whl'
    with zipfile.ZipFile(wheel) as z:
        inventory={p for p in z.namelist() if p.startswith(package+'/') and not p.endswith('/')}
        assert inventory==set(source),(project,'inventory')
        for path,digest in source.items():assert hashlib.sha256(z.read(path)).hexdigest()==digest,(project,path)
    sdist=ROOT/project/f'dist/06a-final/{package}-0.1.0.tar.gz'
    with tarfile.open(sdist) as t:
        members={p.name.split('/',1)[1]:p for p in t.getmembers() if p.isfile() and '/' in p.name}
        inventory={p.removeprefix('src/') for p in members if p.startswith('src/'+package+'/')}
        assert inventory==set(source),(project,'sdist inventory')
        for path,digest in source.items():
            f=t.extractfile(members['src/'+path]);assert f
            assert hashlib.sha256(f.read()).hexdigest()==digest,(project,path)
        for name in ['pyproject.toml','README.md']:
            f=t.extractfile(members[name]);assert f
            assert hashlib.sha256(f.read()).hexdigest()==prior['source_files_sha256'][project+'/'+name],(project,name)
    proof.append({'project':project,'source_files_equal_to_06b_baseline':len(source),'sdist_readme_manifest_equal':True,'wheel_sha256':sha(wheel),'sdist_sha256':sha(sdist),'historical_release_identity':'External rebuild; current bot artifact under 06a-final contains 06B source, not the original 06A release. Historical hashes remain authoritative for the old release.'})
core_sha=sha(ROOT/'cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl')
for project in ['cripto-bot','cripto-analytics']:
    lock=tomllib.loads((ROOT/project/'uv.lock').read_text())
    core=next(p for p in lock['package'] if p['name']=='cripto-core')
    assert core['wheels'][0]['hash']=='sha256:'+core_sha,(project,'core lock hash')
result={'status':'VERIFIED_EXTERNAL_REBUILD','verified_at':datetime.now(timezone.utc).isoformat(),'user_confirmation':'Sim, houve reconstrução externa','scope':'Resolve 06C artifact provenance using current verified test composition; do not claim original 06A artifacts remain available or rewrite old evidence.','baseline_source':'docs/testes/sprint-06b-evidencias.json','rebuilt_artifacts':proof,'prior_vs_current_sha256':current['prior_artifact_mismatches'],'current_source_hashes_reverified':len(current['source_files_sha256']),'tested_artifact_hashes_reverified':len(current['artifact_sha256']),'consumer_core_lock_hashes_match':True,'runtime_changed_after_tests':False,'old_artifacts_restored_or_deleted':False,'historical_evidence_modified':False,'additional_runtime_tests':'Not rerun: tested sources/artifacts unchanged; checks limited to rebuilt content, source inventory, controls and lock identity.'}
(DOCS/'testes/sprint-06c-reconstrucao-externa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'rebuilt_artifacts':proof,'tested_sources_unchanged':len(current['source_files_sha256'])},ensure_ascii=False))
