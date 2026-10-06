"""Report omitted local dependencies without downloading or modifying anything."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',action='store_true');args=parser.parse_args()
    runtime=['build/custom/golden-axe.bin','tools/libretro/genesis_plus_gx_libretro.dll']
    full=runtime+['source/ga.asm','source/ga.macrosetup.asm','source/AS/win32/asw.exe',
        'source/AS/win32/gap2bin.exe','scripts/prepare_custom.py','assets/generated','assets/custom','assets/reference']
    if not args.runtime:
        full+= [item['path'] for item in json.loads((ROOT/'docs/omitted-scripts.json').read_text())['files']
                if item['reason'].startswith('integration') and not item['path'].endswith(
                    ('backup_release.py','document_release.py','release_manifest.py'))]
    required=runtime if args.runtime else sorted(set(full))
    missing=[name for name in required if not (ROOT/name).exists()]
    report=dict(result='missing-local-components' if missing else 'paths-present',
        missing=missing,downloaded=False,note='Path presence does not establish authorization or game compatibility.')
    print(json.dumps(report,indent=2))
    return 2 if missing else 0


if __name__=='__main__':raise SystemExit(main())
