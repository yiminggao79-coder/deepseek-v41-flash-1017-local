#!/usr/bin/env python3
"""Offline preparation helpers. Standard library only. No download/build/install path."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ENGINE_COMMIT = '2076412598e99127ea2554467b2b7530856895d3'


def load_manifest():
    return json.loads((ROOT / 'manifests/model.json').read_text())


def inspect(manifest, roots, hash_files=False):
    """Find exact shard basenames across mounts; ambiguous matches fail closed."""
    roots = [Path(p).resolve(strict=True) for p in roots]
    names = {Path(f['path']).name for f in manifest['files']}
    candidates = {n: set() for n in names}
    for root in roots:
        if not root.is_dir():
            raise ValueError('Input root must be a directory: ' + str(root))
        for parent, _, files in os.walk(root, followlinks=False):
            for name in names.intersection(files):
                path = Path(parent) / name
                if path.is_file():
                    candidates[name].add(path.resolve())
    rows, found = [], {}
    for f in manifest['files']:
        name = Path(f['path']).name
        paths = sorted(candidates[name])
        row = {'name': name, 'expected_bytes': f['size']}
        if len(paths) != 1:
            row['status'] = 'missing' if not paths else 'ambiguous'
            row['candidates'] = [str(p) for p in paths]
        else:
            path = paths[0]
            row.update(path=str(path), actual_bytes=path.stat().st_size)
            row['status'] = 'size_ok' if row['actual_bytes'] == f['size'] else 'size_mismatch'
            if row['status'] == 'size_ok' and hash_files:
                h = hashlib.sha256()
                with path.open('rb') as stream:
                    for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                        h.update(chunk)
                row['sha256'] = h.hexdigest()
                row['status'] = 'hash_ok' if h.hexdigest() == f['sha256'] else 'hash_mismatch'
            if row['status'] in ('size_ok', 'hash_ok'):
                found[name] = path
        rows.append(row)
    report = {'ok': len(found) == len(manifest['files']), 'hashes_checked': hash_files,
              'required_model_bytes': manifest['total_bytes'], 'files': rows,
              'note': 'Size checks alone do not establish integrity or model compatibility.'}
    return report, found


def resources(roots):
    disks = []
    for path in roots:
        p = Path(path).resolve()
        usage = shutil.disk_usage(p)
        disks.append({'path': str(p), 'free_bytes': usage.free, 'total_bytes': usage.total})
    memory = {}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, value = line.split(':', 1)
            if key in ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'):
                memory[key + '_bytes'] = int(value.split()[0]) * 1024
    except (OSError, ValueError):
        memory['status'] = 'unavailable'
    return {'disks': disks, 'linux_memory': memory,
            'warning': 'Informational only. Host RAM may exceed container limits. mmap does not make insufficient RAM/VRAM fast; disk-backed paging may be unusably slow.'}


def make_view(found, destination):
    """Create a NEW directory containing symlinks only; never copy weights."""
    if not found:
        raise ValueError('No verified shard paths')
    destination = Path(destination).absolute()
    if os.path.lexists(destination):
        raise FileExistsError(str(destination))
    # Reserve directory atomically; concurrent creators cannot be overwritten.
    destination.mkdir(parents=False, exist_ok=False)
    created = []
    try:
        for name, source in found.items():
            if Path(name).name != name:
                raise ValueError('Invalid shard basename')
            target = destination / name
            target.symlink_to(Path(source).resolve(strict=True))
            created.append(target)
    except BaseException:
        for target in created:
            target.unlink()
        destination.rmdir()
        raise


def server_command(binary, model, context, threads, port):
    return [str(binary), '--model', str(model), '--ctx-size', str(context),
            '--threads', str(threads), '--gpu-layers', '0', '--cpu-moe',
            '--host', '127.0.0.1', '--port', str(port), '--jinja']


def run_bounded(command, seconds):
    """POSIX process group cleanup scoped to the process created here."""
    if os.name != 'posix':
        raise ValueError('Bounded launch supports POSIX/Linux only')
    child = subprocess.Popen(command, start_new_session=True)
    try:
        return child.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        print('Time limit reached; stopping owned server process.', file=sys.stderr)
        return 124
    except KeyboardInterrupt:
        return 130
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('preflight', 'view'):
        p = sub.add_parser(name)
        p.add_argument('--root', type=Path, action='append', required=True,
                       help='Existing mounted directory; repeat for split datasets')
        p.add_argument('--sha256', action='store_true', help='Read every model byte; expensive')
        if name == 'view':
            p.add_argument('--output', type=Path, required=True, help='New directory under an existing writable parent')
    p = sub.add_parser('launch')
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--view', type=Path, required=True)
    p.add_argument('--context', type=positive, default=2048)
    p.add_argument('--threads', type=positive, default=2)
    p.add_argument('--port', type=positive, default=8080)
    p.add_argument('--timeout', type=positive, default=600)
    p.add_argument('--execute', action='store_true', help='Explicitly opt in to running an already built binary')
    args = parser.parse_args(argv)
    m = load_manifest()
    if args.command in ('preflight', 'view'):
        report, found = inspect(m, args.root, args.sha256)
        report['resources'] = resources(args.root + [Path.cwd()])
        print(json.dumps(report, indent=2))
        if not report['ok']:
            return 2
        if args.command == 'view':
            make_view(found, args.output)
        return 0
    if args.port > 65535:
        parser.error('port must be <= 65535')
    model = args.view / Path(m['files'][0]['path']).name
    command = server_command(args.binary, model, args.context, args.threads, args.port)
    print(shlex.join(command), flush=True)
    if not args.execute:
        print('DRY RUN ONLY. No binary executed, no model loaded.')
        return 0
    report, _ = inspect(m, [args.view], False)
    if not report['ok']:
        print(json.dumps(report, indent=2))
        return 2
    if not args.binary.is_file() or not os.access(args.binary, os.X_OK):
        raise ValueError('An existing executable llama-server is required')
    return run_bounded(command, args.timeout)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
