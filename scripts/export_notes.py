"""Export only the approved research folder; never modify the Obsidian source."""
import argparse
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/Users/dongkseo/Documents/Obsidian Vault/research')
DEFAULT_EXCLUDES = {'non-research-links.md', 'speechify-library.md'}


def sanitize_note(text: str) -> str:
    output = []
    fence = None
    hidden_depth = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            if hidden_depth is None:
                output.append(line)
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)', line) if fence is None else None
        if heading:
            depth = len(heading.group(1))
            if hidden_depth is not None and depth <= hidden_depth:
                hidden_depth = None
            title = heading.group(2)
            if '활용 아이디어' in title or re.match(r'^(?:\d+\.\s*)?우리 맥락\s*#*$', title):
                hidden_depth = depth if hidden_depth is None else min(depth, hidden_depth)
        if hidden_depth is None:
            if fence is None:
                parts = re.split(r'(`+[^`]*`+)', line)
                for i in range(0, len(parts), 2):
                    part = re.sub(r'\[\[INDEX(?=[#|\]])', '[[research-index', parts[i]).replace('인포뱅크', '소속 조직')
                    # Currency delimiters must not consume genuine formulae such as $1+T$.
                    parts[i] = re.sub(r'(?<![\\\w])\$(\d+(?:\.\d+)?)(?=M\b|/|[\s,;)]|$)', r'\\$\1', part)
                line = ''.join(parts)
            output.append(line)
    return ''.join(output)


def export_notes(source: Path, destination: Path) -> dict:
    if source.is_symlink() or destination.is_symlink():
        raise ValueError('Source and destination must not be symbolic links')
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if not source.is_dir() or source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate directories')
    # Reject links before making any changes, including links to other vault folders.
    files = sorted(source.rglob('*'))
    if any(path.is_symlink() for path in files):
        raise ValueError('Symbolic links are not publishable')
    excluded = set(DEFAULT_EXCLUDES)
    rules = ROOT/'publish-excludes.txt'
    if rules.exists():
        excluded.update(line.strip() for line in rules.read_text().splitlines() if line.strip() and not line.startswith('#'))
    report = {'exported': [], 'excluded': [], 'sanitized': []}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.publish-', dir=destination.parent) as temp:
        staging = Path(temp)/'content'; staging.mkdir()
        for path in files:
            if not path.is_file() or path.suffix != '.md':
                continue
            relative = path.relative_to(source)
            if path.name in excluded or relative.as_posix() in excluded or any(part.startswith('.') for part in relative.parts):
                report['excluded'].append(relative.as_posix()); continue
            original = path.read_text()
            content = sanitize_note(original)
            if path.name in ('INDEX.md', 'READING-GUIDE.md'):
                content = ''.join(line for line in content.splitlines(keepends=True) if not any(Path(name).stem in line for name in excluded))
            published = Path('research-index.md') if relative == Path('INDEX.md') else relative
            target = staging/published; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            report['exported'].append(relative.as_posix())
            if original != content:
                report['sanitized'].append(relative.as_posix())
        categories = sorted({Path(name).parts[0] for name in report['exported'] if len(Path(name).parts) > 1})
        home = '---\ntitle: Donggyun의 지식베이스\n---\n\n[[research-index|전체 자료]] · [[READING-GUIDE|읽기 가이드]]\n\n'
        home += '\n'.join(f'- [[{category}/|{category}]]' for category in categories)+'\n'
        (staging/'index.md').write_text(home)
        # Keep the previous successful export if writing/validation above failed.
        backup = Path(temp)/'previous'
        if destination.exists():
            destination.rename(backup)
        try:
            staging.rename(destination)
        except OSError:
            if backup.exists(): backup.rename(destination)
            raise
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args()
    report = export_notes(args.source, ROOT/'content')
    local = ROOT/'.local'; local.mkdir(exist_ok=True)
    (local/'export-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Exported {len(report['exported'])} notes; excluded {len(report['excluded'])}; sanitized {len(report['sanitized'])}")
