from __future__ import annotations

import base64
import hashlib
import pathlib
import sys
import tarfile

EXPECTED_DIGEST = "e822a3e7b9d2b62b19c720b598893bc63d51d8d14ea7fbb2688650b2d507d408"
EXPECTED_CHUNKS = (1, 2, 3)


def main() -> None:
    source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    chunks: dict[int, str] = {}

    sections = source.split("PATCH-CHUNK-")
    for section in sections[1:]:
        number_text, separator, remainder = section.partition("\n")
        if not separator or not number_text.strip().isdigit():
            continue
        number = int(number_text.strip())
        payload_lines: list[str] = []
        for line in remainder.splitlines():
            if line.startswith("PATCH-"):
                break
            payload_lines.append(line.strip())
        chunks[number] = "".join(payload_lines)

    if tuple(sorted(chunks)) != EXPECTED_CHUNKS:
        raise RuntimeError(
            f"Expected chunks {EXPECTED_CHUNKS}, received {tuple(sorted(chunks))}"
        )

    archive_bytes = base64.b64decode(
        "".join(chunks[index] for index in EXPECTED_CHUNKS),
        validate=True,
    )
    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != EXPECTED_DIGEST:
        raise RuntimeError(f"Archive checksum mismatch: {digest}")

    archive = pathlib.Path("/tmp/meal-options-feature.tar.gz")
    archive.write_bytes(archive_bytes)
    with tarfile.open(archive, "r:gz") as source_archive:
        source_archive.extractall(".")


if __name__ == "__main__":
    main()
