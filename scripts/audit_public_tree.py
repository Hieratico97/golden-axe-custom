"""Check tracked publication files for private data and excluded media/binaries."""
import ast,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOW={'.py','.asm','.ps1','.cmd','.md','.txt','.json','.yml','.toml'}
SPECIAL={'.gitignore','.gitattributes','LICENSE'}
BLOCKED_DIRS={'assets','build','source','game','tools','downloads','reference-32x','.venv'}
SECRET=re.compile(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[\w-]{25,}|'
    r'sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|'
    r'drive\.google\.com/file/d/|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|'
    r'(?:[A-Za-z]:[/\\]Users[/\\]|'+'/'+'home'+'/'+'|'+'/'+'Users'+'/'+r')[^\s\x27\x22]+',re.I)


def main():
    git=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True)
    if git.returncode==0:
        names=[n for n in git.stdout.decode().split('\0') if n]
        if not names:raise SystemExit('No tracked files: stage the reviewed publication before auditing.')
    else:
        names=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts]
    findings=[]
    for name in names:
        path=ROOT/name
        if Path(name).parts[0] in BLOCKED_DIRS:findings.append(dict(path=name,reason='excluded directory'));continue
        if path.suffix not in ALLOW and path.name not in SPECIAL:findings.append(dict(path=name,reason='binary/media or unexpected extension'));continue
        if path.is_symlink():findings.append(dict(path=name,reason='symlink'));continue
        try:content=path.read_text(encoding='utf-8')
        except (UnicodeDecodeError,OSError):findings.append(dict(path=name,reason='not UTF-8 text'));continue
        if SECRET.search(content):findings.append(dict(path=name,reason='potential private data; values withheld'))
        if path.suffix=='.py':ast.parse(content,filename=name)
    print(json.dumps(dict(result='pass' if not findings else 'fail',files=len(names),findings=findings),indent=2))
    return 1 if findings else 0


if __name__=='__main__':raise SystemExit(main())
