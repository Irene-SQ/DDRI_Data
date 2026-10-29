"""Package indexed SDF directories and upload verified, resumable release assets."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import tarfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Irene-SQ/DDRI_Data'
TAG = 'processed-sdf-v1'
LIMIT = 1024**3
LOCK = threading.Lock()


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True, timeout=3600)


def assets(release_id):
    pages = json.loads(gh('api', '--paginate', '--slurp',
                         f'repos/{REPO}/releases/{release_id}/assets?per_page=100'))
    return {asset['name']: asset for page in pages for asset in page}


def upload(path, release_id):
    digest = sha(path)
    for attempt in range(4):
        remote = assets(release_id).get(path.name)
        if remote:
            if remote.get('digest') == 'sha256:' + digest and remote['size'] == path.stat().st_size:
                return digest
            raise RuntimeError(f'Existing release asset differs: {path.name}')
        try:
            gh('release', 'upload', TAG, str(path), '--repo', REPO)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt == 3:
                raise
        time.sleep(2)
    remote = assets(release_id).get(path.name)
    if not remote or remote.get('digest') != 'sha256:' + digest or remote['size'] != path.stat().st_size:
        raise RuntimeError(f'Remote verification failed: {path.name}')
    return digest


class HashReader:
    def __init__(self, stream):
        self.stream = stream
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        data = self.stream.read(size)
        self.digest.update(data)
        return data


def plan(source):
    with (ROOT/'SDF_DATA/metadata/files.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    summary = json.loads((ROOT/'SDF_DATA/metadata/dataset_summary.json').read_text())
    parts = []
    for directory in summary['directories']:
        name = directory['directory']
        selected = [r for r in rows if Path(r['path']).parts[0] == name]
        current, size, number = [], 0, 1
        for row in selected:
            relative = Path(row['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe source path')
            path = source/relative
            if path.is_symlink() or not path.is_file() or path.stat().st_size != int(row['bytes']):
                raise ValueError(f'Source/inventory disagreement: {relative}')
            if current and size + int(row['bytes']) > LIMIT:
                parts.append(dict(name=f'SDF_DATA.{name}.part{number:03d}.tar.gz', directory=name, members=current))
                current, size, number = [], 0, number+1
            current.append(row)
            size += int(row['bytes'])
        parts.append(dict(name=f'SDF_DATA.{name}.part{number:03d}.tar.gz', directory=name, members=current))
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--cache', type=Path, default=ROOT/'.upload-cache')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    parts = plan(source)
    print(f'{len(parts)} independent archives; {sum(len(p["members"]) for p in parts)} files', flush=True)
    if args.plan:
        return
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    release = json.loads(gh('api', f'repos/{REPO}/releases/tags/{TAG}'))
    if not release['draft']:
        raise RuntimeError('The target release must be a draft during upload.')
    state = dict(phase='uploading', total_parts=len(parts), verified=[], active={}, failed=[])
    dump(cache/'status.json', state)

    def process(part):
        name = part['name']
        archive = cache/name
        record_path = cache/(name+'.json')
        plan_hash = hashlib.sha256(json.dumps(part, sort_keys=True).encode()).hexdigest()
        with LOCK:
            state['active'][name] = 'packaging'
            dump(cache/'status.json', state)
        record = json.loads(record_path.read_text()) if record_path.exists() else None
        if record and record['plan_sha256'] != plan_hash:
            raise RuntimeError(f'Archive plan changed: {name}')
        remote = assets(release['id']).get(name)
        if record and remote and remote.get('digest') == 'sha256:'+record['sha256'] and remote['size'] == record['bytes']:
            pass
        else:
            if not record or not archive.exists():
                per_file = []
                temporary = archive.with_suffix('.building')
                with temporary.open('wb') as output:
                    with gzip.GzipFile(filename='', mode='wb', fileobj=output, compresslevel=1, mtime=0) as zipped:
                        with tarfile.open(fileobj=zipped, mode='w|') as tar:
                            folder = tarfile.TarInfo('SDF_DATA/'+part['directory'])
                            folder.type = tarfile.DIRTYPE
                            folder.mode = 0o755
                            tar.addfile(folder)
                            for row in part['members']:
                                path = source/row['path']
                                before = path.stat()
                                assert before.st_size == int(row['bytes'])
                                info = tar.gettarinfo(str(path), arcname='SDF_DATA/'+row['path'])
                                info.mtime = 0
                                info.uid = info.gid = 0
                                info.uname = info.gname = ''
                                info.mode = 0o644
                                with path.open('rb') as stream:
                                    reader = HashReader(stream)
                                    tar.addfile(info, reader)
                                after = path.stat()
                                assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
                                per_file.append(dict(path='SDF_DATA/'+row['path'], sha256=reader.digest.hexdigest()))
                temporary.replace(archive)
                record = dict(name=name, directory=part['directory'], bytes=archive.stat().st_size,
                              sha256=sha(archive), files=len(per_file), plan_sha256=plan_hash, file_checksums=per_file)
                assert record['bytes'] < 2*1024**3
                dump(record_path, record)
            with LOCK:
                state['active'][name] = 'uploading'
                dump(cache/'status.json', state)
            assert upload(archive, release['id']) == record['sha256']
        archive.unlink(missing_ok=True)
        with LOCK:
            state['verified'].append(name)
            state['active'].pop(name, None)
            dump(cache/'status.json', state)
            print(f'Verified {len(state["verified"])}/{len(parts)}: {name}', flush=True)
        return record

    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(process, part): part['name'] for part in parts}
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as exc:
                with LOCK:
                    state['failed'].append(dict(name=futures[future], error=repr(exc)))
                    dump(cache/'status.json', state)
    if state['failed']:
        state['phase'] = 'incomplete'
        dump(cache/'status.json', state)
        raise RuntimeError('Some archives failed; inspect status.json before resuming.')
    records.sort(key=lambda r:r['name'])
    manifest = cache/'SDF_DATA.release_manifest.json'
    dump(manifest, dict(repo=REPO, tag=TAG, archives=[{k:v for k,v in r.items() if k not in ('file_checksums','plan_sha256')} for r in records]))
    file_hashes = cache/'SDF_DATA.files.sha256'
    file_hashes.write_text(''.join(f"{item['sha256']}  {item['path']}\n" for r in records for item in r['file_checksums']))
    sums = cache/'SDF_DATA.SHA256SUMS'
    sums.write_text(''.join(f"{r['sha256']}  {r['name']}\n" for r in records)
                    +f'{sha(manifest)}  {manifest.name}\n'+f'{sha(file_hashes)}  {file_hashes.name}\n')
    for path in (manifest, file_hashes, sums):
        upload(path, release['id'])
    if args.publish:
        gh('release', 'edit', TAG, '--repo', REPO, '--draft=false')
    state['phase'] = 'published' if args.publish else 'verified_draft'
    state['compressed_bytes'] = sum(r['bytes'] for r in records)
    dump(cache/'status.json', state)
    print('COMPLETE', json.dumps(state), flush=True)


if __name__ == '__main__':
    main()
