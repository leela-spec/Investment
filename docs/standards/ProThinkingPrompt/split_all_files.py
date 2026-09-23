#!/usr/bin/env python3
"""Split a heading/fenced-file bundle into the files it contains.

The bundle format is:

    ## `file-name.ext`

    ````markdown
    file contents
    ````

The closing fence is the final matching fence before the next filename
heading. This tolerates bundle sections whose opening and closing fence widths
do not match, while keeping inner code blocks inside the extracted payload.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_RE = re.compile(r"^##\s+`([^`]+)`\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(?:[^`]*)?$")


def split_bundle(source: Path) -> list[tuple[str, str]]:
    lines = source.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, str]] = []
    index = 0

    while index < len(lines):
        heading = HEADING_RE.match(lines[index])
        if not heading:
            index += 1
            continue

        filename = heading.group(1).strip()
        if Path(filename).name != filename or filename in {".", ".."}:
            raise ValueError(f"Unsafe output filename at line {index + 1}: {filename!r}")

        opening_index = index + 1
        while opening_index < len(lines) and not lines[opening_index].strip():
            opening_index += 1
        if opening_index >= len(lines):
            raise ValueError(f"Missing opening fence for {filename!r}")

        opening = FENCE_RE.match(lines[opening_index])
        if not opening:
            raise ValueError(f"Missing opening fence for {filename!r} at line {opening_index + 1}")
        marker = opening.group(1)
        marker_char = marker[0]

        next_heading = len(lines)
        for candidate_index in range(index + 1, len(lines)):
            if HEADING_RE.match(lines[candidate_index]):
                next_heading = candidate_index
                break

        closing_candidates = [
            candidate_index
            for candidate_index in range(opening_index + 1, next_heading)
            if (candidate := FENCE_RE.match(lines[candidate_index]))
            and candidate.group(1)[0] == marker_char
        ]
        if not closing_candidates:
            raise ValueError(f"Missing closing fence for {filename!r}")
        closing_index = closing_candidates[-1]

        content_lines = lines[opening_index + 1 : closing_index]
        if content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        if content_lines and not content_lines[-1].strip():
            content_lines.pop()
        content = "\n".join(content_lines).rstrip("\n") + "\n"
        sections.append((filename, content))
        index = closing_index + 1

    if not sections:
        raise ValueError(f"No bundled file sections found in {source}")
    names = [name for name, _ in sections]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate bundled filenames: {', '.join(duplicates)}")
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, help="bundle to split (default: AllFilesInOne.md)")
    parser.add_argument("--force", action="store_true", help="overwrite existing extracted files")
    args = parser.parse_args()

    source = args.source or Path(__file__).with_name("AllFilesInOne.md")
    sections = split_bundle(source)
    output_dir = source.parent
    existing = [output_dir / name for name, _ in sections if (output_dir / name).exists()]
    if existing and not args.force:
        names = ", ".join(path.name for path in existing)
        raise SystemExit(f"Refusing to overwrite existing files: {names}. Re-run with --force.")

    for filename, content in sections:
        (output_dir / filename).write_text(content, encoding="utf-8", newline="\n")
    print(f"Extracted {len(sections)} files to {output_dir}")
    for filename, _ in sections:
        print(f"- {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
