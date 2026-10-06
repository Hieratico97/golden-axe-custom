"""Validate Genesis images and create verified IPS patches. Standard library only."""
import hashlib
import json
import struct
import sys
from pathlib import Path


def finalize(path):
    data = bytearray(path.read_bytes())
    if len(data) < 512 or len(data) % 2 or data[256:260] != b'SEGA':
        raise ValueError('Invalid Genesis ROM header or size')
    struct.pack_into('>I', data, 0x1A4, len(data) - 1)
    checksum = sum(value[0] for value in struct.iter_unpack('>H', data[512:])) & 0xFFFF
    struct.pack_into('>H', data, 0x18E, checksum)
    path.write_bytes(data)
    report = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                  checksum=f'{checksum:04X}', reset_vector=hex(struct.unpack_from('>I', data, 4)[0]))
    path.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


def patch(base_path, changed_path, output):
    base, changed = base_path.read_bytes(), changed_path.read_bytes()
    if len(changed) < len(base) or len(changed) > 0xFFFFFF:
        raise ValueError('IPS export supports equal-size or expanded ROMs up to 16 MiB')
    result, records = bytearray(b'PATCH'), []
    pos = 0
    while pos < len(changed):
        if pos < len(base) and base[pos] == changed[pos]:
            pos += 1
            continue
        start = pos
        # 0x454F46 is reserved for the EOF marker; include the preceding byte.
        if start == 0x454F46:
            start -= 1
        pos += 1
        while pos < len(changed) and pos - start < 65535 and (pos >= len(base) or base[pos] != changed[pos]):
            pos += 1
        block = changed[start:pos]
        result += start.to_bytes(3, 'big') + len(block).to_bytes(2, 'big') + block
        records.append((start, block))
    result += b'EOF'
    rebuilt = bytearray(base) + bytearray(len(changed) - len(base))
    for start, block in records:
        rebuilt[start:start + len(block)] = block
    if bytes(rebuilt) != changed:
        raise ValueError('Patch verification failed')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
    print(f'IPS verified: {len(records)} records, {len(result)} bytes, {output}')


if __name__ == '__main__':
    if sys.argv[1] == 'finalize':
        finalize(Path(sys.argv[2]))
    elif sys.argv[1] == 'patch':
        patch(*(Path(arg) for arg in sys.argv[2:5]))
    else:
        raise SystemExit('Usage: rom.py finalize ROM | patch BASE CUSTOM OUTPUT')
