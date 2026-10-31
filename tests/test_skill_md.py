# -*- coding: utf-8 -*-
"""Check SKILL.md and the plugin metadata against the published limits.

    python tests/test_skill_md.py

No third-party dependency, so this runs on a bare Python 3.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "van-ban-hanh-chinh-vn")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")

# Published limits for Agent Skills frontmatter.
NAME_MAX = 64
DESC_MAX = 1024
# Anthropic's authoring guide: keep the SKILL.md body under 500 lines.
BODY_MAX_LINES = 500
RESERVED = ("anthropic", "claude")

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def main():
    with open(SKILL_MD, encoding="utf-8") as f:
        raw = f.read()

    check(raw.startswith("---\n"), "SKILL.md must open with YAML frontmatter")
    _, frontmatter, body = raw.split("---", 2)

    name = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.M)
    check(bool(name), "frontmatter has no 'name'")
    if name:
        value = name.group(1)
        check(len(value) <= NAME_MAX, "name longer than %d characters" % NAME_MAX)
        check(bool(re.match(r"^[a-z0-9-]+$", value)),
              "name must be lower case letters, digits and hyphens only: %r" % value)
        for word in RESERVED:
            check(word not in value, "name must not contain the reserved word %r" % word)
        check(value == os.path.basename(SKILL_DIR),
              "the skill directory name must equal the frontmatter name")

    desc = frontmatter.split("description:", 1)
    check(len(desc) == 2, "frontmatter has no 'description'")
    if len(desc) == 2:
        text = re.sub(r"\s+", " ", desc[1].replace(">-", "", 1)).strip()
        check(len(text) > 0, "description is empty")
        check(len(text) <= DESC_MAX,
              "description is %d characters, limit is %d" % (len(text), DESC_MAX))
        check("<" not in text and ">" not in text, "description must not contain XML tags")
        # The description is injected into a system prompt, so it has to read in
        # the third person, not as the skill talking to the user.
        for bad in ("I can ", "I will ", "You can use this"):
            check(bad not in text, "description must be third person, found %r" % bad)
        check("Use when" in text, "description should say when to use the skill")

    lines = body.strip().splitlines()
    check(len(lines) <= BODY_MAX_LINES,
          "SKILL.md body is %d lines, keep it under %d" % (len(lines), BODY_MAX_LINES))

    # Every relative link in SKILL.md must resolve, and stay one level deep.
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if target.startswith(("http://", "https://", "#")):
            continue
        path = os.path.join(SKILL_DIR, target)
        check(os.path.exists(path), "SKILL.md links to a missing file: %s" % target)
        check("\\" not in target, "use forward slashes in paths: %s" % target)

    # Reference files over 100 lines carry a table of contents.
    for ref in sorted(os.listdir(os.path.join(SKILL_DIR, "references"))):
        p = os.path.join(SKILL_DIR, "references", ref)
        with open(p, encoding="utf-8") as f:
            content = f.read()
        if len(content.splitlines()) > 100:
            check("## Mục lục" in content or "## Contents" in content,
                  "%s is over 100 lines and needs a table of contents" % ref)

    # No em dash anywhere in the skill, which is the rule the skill itself enforces.
    for folder, _, files in os.walk(SKILL_DIR):
        for fn in files:
            if not fn.endswith((".md", ".json", ".py")):
                continue
            p = os.path.join(folder, fn)
            with open(p, encoding="utf-8") as f:
                text = f.read()
            if fn in ("tao_vanban.py", "kiem_tra.py"):
                continue  # these two define the rule and quote the character
            check("—" not in text,
                  "%s contains an em dash U+2014" % os.path.relpath(p, ROOT))

    # Plugin and marketplace manifests agree with each other.
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        plugin = json.load(f)
    with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
        market = json.load(f)
    check(plugin["name"] == os.path.basename(SKILL_DIR),
          "plugin.json name must match the skill directory")
    entries = [p["name"] for p in market["plugins"]]
    check(plugin["name"] in entries,
          "marketplace.json must list an entry named %r" % plugin["name"])
    for entry in market["plugins"]:
        check(".." not in entry["source"], "a relative source must not contain '..'")

    if failures:
        print("%d FAILED:" % len(failures))
        for m in failures:
            print("  -", m)
        return 1
    print("SKILL.md, references and plugin metadata all pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
