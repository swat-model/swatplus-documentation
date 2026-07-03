#!/usr/bin/env python3
"""Generate per-node PDFs for the SWAT+ docs (every nav level: page, section, full).

Reads mkdocs.yml nav, renders each node with pandoc -> xelatex, resolves
internal cross-references to in-PDF jumps (or live-site URLs when the target
is outside the node), rotates wide tables to landscape, and caches by content
hash so a deploy only rebuilds what changed.

Usage:
  python3 pdf/build.py --repo . --out SITE_DIR [--cache DIR] [--site-url URL]
                       [--workers N] [--landscape-cols N] [--only SLUG]

Outputs:
  SITE_DIR/pdf/<slug>.pdf        one PDF per nav node
  SITE_DIR/pdf/manifest.json     consumed by assets/pdf-download.js
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import yaml

# bump to force a full rebuild when the rendering logic changes materially
SCRIPT_VERSION = "3"


# ---------------------------------------------------------------------------
# mkdocs.yml loading (ignore !!python/name: tags used by material)
# ---------------------------------------------------------------------------
class _Loader(yaml.SafeLoader):
    pass


_Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda l, s, n: None)
_Loader.add_multi_constructor("!!python/name:", lambda l, s, n: None)


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def mkdocs_slug(text):
    """Approximate python-markdown toc slugify (default, ascii)."""
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


_LTX = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}"}


def latex_escape(s):
    """Escape LaTeX specials for raw values passed through -V (pandoc does not)."""
    return "".join(_LTX.get(c, c) for c in s)


def safe_id(s):
    """LaTeX-safe identifier: hyphens only, no underscores (which need math mode)."""
    return re.sub(r"-+", "-", s.replace("_", "-")).strip("-")


# ---------------------------------------------------------------------------
# nav -> node tree
# ---------------------------------------------------------------------------
class Node:
    _sec = 0

    def __init__(self, ntype, title, src=None, parent_slug="", parent=None):
        self.type = ntype
        self.title = title
        self.parent = parent
        self.children = []
        self.src_files = []
        if ntype == "page":
            self.slug = "pages/" + (src[:-3] if src.endswith(".md") else src)
            self.src_files = [src]
            self.src = src
        elif ntype == "root":
            self.slug = "swatplus-documentation"
            self.src = None
        else:
            base = slugify(title) or f"section-{Node._sec}"
            Node._sec += 1
            self.slug = f"sections/{parent_slug}-{base}" if parent_slug else f"sections/{base}"
            self.src = None
        self.pdf = f"{self.slug}.pdf"


def title_from_path(path):
    stem = Path(path).stem
    if stem == "index":
        stem = Path(path).parent.name or "Home"
    return stem.replace("-", " ").replace("_", " ").title()


# nav pages that are site-only and should not get their own PDF
EXCLUDE_SRC = {"downloads.md"}


def walk(items, parent_slug, parent):
    nodes = []
    for item in items:
        if isinstance(item, str):
            if item in EXCLUDE_SRC:
                continue
            nodes.append(Node("page", title_from_path(item), src=item, parent=parent))
        elif isinstance(item, dict):
            (title, val), = item.items()
            if isinstance(val, str):
                if val in EXCLUDE_SRC:
                    continue
                nodes.append(Node("page", title, src=val, parent=parent))
            elif isinstance(val, list):
                sec = Node("section", title, parent_slug=parent_slug, parent=parent)
                base = sec.slug.split("/", 1)[1]
                sec.children = walk(val, base, sec)
                sec.src_files = collect(sec.children)
                nodes.append(sec)
    return nodes


def collect(nodes):
    out = []
    for n in nodes:
        out.extend(n.src_files if n.type == "page" else collect(n.children))
    return out


def flatten(nodes, acc):
    for n in nodes:
        acc.append(n)
        flatten(n.children, acc)


def section_index_url(node, prefix):
    """Site URL of a node's landing page: a page's own url, or a section's index child."""
    if node.type == "page":
        return page_url(node.src, prefix)
    for c in node.children:
        if c.type == "page" and Path(c.src).stem == "index":
            return page_url(c.src, prefix)
    return None


def page_url(rel_md, prefix):
    p = rel_md[:-3] if rel_md.endswith(".md") else rel_md
    if p.endswith("index"):
        p = p[:-5]
    return f"{prefix}/{p}".replace("//", "/").rstrip("/") + "/"


# ---------------------------------------------------------------------------
# markdown preprocessing: frontmatter, admonitions, heading ids, links, images
# ---------------------------------------------------------------------------
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ADMON = re.compile(r'^!!!\s+\w+(?:\s+"([^"]*)")?\s*$')
EXISTING_ID = re.compile(r"\{#([\w-]+)\}\s*$")


def strip_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\r?\n.*?\r?\n(?:---|\.\.\.)\r?\n", text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


# Material-for-MkDocs-only markup that pandoc cannot render and must not leak
_ICON = re.compile(r":(?:material|fontawesome|octicons|simple)-[a-z0-9-]+:")
_ATTRCLASS = re.compile(r"\{:?\s*\.[^}]*\}")          # { .lg .middle }, { .md-button }
_DIVLINE = re.compile(r"^\s*</?div\b[^>]*>\s*$")      # <div class="grid cards" markdown> / </div>
_CARDRULE = re.compile(r"^\s+-{3,}\s*$")              # indented card divider inside grid cards


def strip_material(text):
    """Drop Material-only markup (icon shortcodes, attr-list classes, grid/card
    <div> wrappers) so it never appears as literal text in a PDF."""
    out, in_code = [], False
    for ln in text.split("\n"):
        if FENCE.match(ln):
            in_code = not in_code
            out.append(ln); continue
        if in_code:
            out.append(ln); continue
        if _DIVLINE.match(ln) or _CARDRULE.match(ln):
            continue
        ln = _ICON.sub("", ln)
        ln = _ATTRCLASS.sub("", ln)
        out.append(ln)
    return "\n".join(out)


def convert_admonitions(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = ADMON.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        out.append(f"> **{m.group(1) or 'Note'}**"); out.append(">"); i += 1
        while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
            out.append(">" if lines[i].strip() == "" else "> " + lines[i][4:])
            i += 1
        out.append("")
    return "\n".join(out)


def fileslug(rel_md):
    p = rel_md[:-3] if rel_md.endswith(".md") else rel_md
    if p.endswith("/index"):
        p = p[:-6]
    return safe_id(re.sub(r"[^\w]+", "-", p).strip("-")) or "home"


def build_heading_map(rel_md, text):
    """Return (slug_map, first_id). slug_map: mkdocs-slug -> explicit unique id."""
    fs = fileslug(rel_md)
    slug_map, used, first_id = {}, set(), None
    in_code = False
    for ln in text.split("\n"):
        f = FENCE.match(ln)
        if f:
            in_code = not in_code
            continue
        if in_code:
            continue
        h = HEADING.match(ln)
        if not h:
            continue
        htext = h.group(2)
        ex = EXISTING_ID.search(htext)
        if ex:
            eid = ex.group(1)
            htext_clean = EXISTING_ID.sub("", htext).strip()
        else:
            ms = mkdocs_slug(re.sub(r"`([^`]*)`", r"\1", htext)) or "section"
            eid = base = safe_id(f"{fs}--{ms}")
            n = 1
            while eid in used:
                n += 1; eid = f"{base}-{n}"
            htext_clean = htext
        used.add(eid)
        ms = mkdocs_slug(re.sub(r"`([^`]*)`", r"\1", htext_clean)) or "section"
        slug_map.setdefault(ms, eid)
        if ex:
            slug_map.setdefault(eid, eid)
        if first_id is None:
            first_id = eid
    if first_id is None:
        first_id = f"{fs}--top"
    return slug_map, first_id


def norm(base_dir, target):
    parts = ((base_dir + "/" + target) if base_dir else target).split("/")
    stack = []
    for seg in parts:
        if seg in ("", "."):
            continue
        if seg == "..":
            if stack:
                stack.pop()
        else:
            stack.append(seg)
    return "/".join(stack)


def to_key(base_dir, path):
    key = norm(base_dir, path)
    if key.endswith(".md"):
        return key
    if key.endswith("/") or key == "":
        return (key + "index.md") if key else "index.md"
    return key + ".md"


def rewrite_file(rel_md, text, docs_dir, included, maps, firstids, prefix, site_url):
    """Add explicit heading ids + rewrite links/images. Returns processed text."""
    base_dir = "" if "/" not in rel_md else str(Path(rel_md).parent)
    out_lines, in_code = [], False

    def fix_links(line):
        # images first: ![alt](path) -> absolute fs path
        def img(m):
            alt, tgt = m.group(1), m.group(2).strip()
            if tgt.startswith(("http://", "https://", "/")):
                return m.group(0)
            return f"![{alt}]({(docs_dir / norm(base_dir, tgt)).resolve()})"
        line = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, line)

        def link(m):
            label, tgt = m.group(1), m.group(2).strip()
            if tgt.startswith(("http://", "https://", "mailto:", "tel:")):
                return m.group(0)
            if tgt.startswith("#"):
                # same-page anchor: retarget to this file's renamed heading id
                fr = tgt[1:]
                eid = maps[rel_md].get(mkdocs_slug(fr), maps[rel_md].get(fr, fr))
                return f"[{label}](#{eid})"
            path, _, frag = tgt.partition("#")
            if not path:
                return m.group(0)
            key = to_key(base_dir, path)
            if key in included:
                if frag:
                    dest = "#" + maps[key].get(mkdocs_slug(frag), maps[key].get(frag, frag))
                else:
                    dest = "#" + firstids[key]
            else:
                url = page_url(key, prefix)
                dest = (site_url.rstrip("/").rsplit(prefix, 1)[0] + url) if site_url else url
                if frag:
                    dest += "#" + frag
            return f"[{label}]({dest})"
        return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", link, line)

    # headingless pages get a top heading so file-level links land and the page
    # becomes its own chapter in merged PDFs (id matches build_heading_map's fallback)
    has_heading, _code = False, False
    for ln in text.split("\n"):
        if FENCE.match(ln):
            _code = not _code
        elif not _code and HEADING.match(ln):
            has_heading = True
            break
    if not has_heading:
        out_lines.append(f"# {title_from_path(rel_md)} {{#{fileslug(rel_md)}--top}}")
        out_lines.append("")

    for ln in text.split("\n"):
        f = FENCE.match(ln)
        if f:
            in_code = not in_code
            out_lines.append(ln); continue
        if in_code:
            out_lines.append(ln); continue
        h = HEADING.match(ln)
        if h and not EXISTING_ID.search(h.group(2)):
            htext = h.group(2)
            ms = mkdocs_slug(re.sub(r"`([^`]*)`", r"\1", htext)) or "section"
            eid = maps[rel_md].get(ms)
            ln = f"{h.group(1)} {htext} {{#{eid}}}" if eid else ln
        out_lines.append(fix_links(ln))
    return "\n".join(out_lines)


def render_markdown(node, docs_dir, prefix, site_url):
    included = set(node.src_files)
    maps, firstids = {}, {}
    raws = {}
    for rel in node.src_files:
        t = strip_frontmatter((docs_dir / rel).read_text(encoding="utf-8"))
        t = strip_material(t)
        t = convert_admonitions(t)
        raws[rel] = t
        m, fid = build_heading_map(rel, t)
        maps[rel], firstids[rel] = m, fid
    chunks = [rewrite_file(rel, raws[rel], docs_dir, included, maps, firstids, prefix, site_url)
              for rel in node.src_files]
    return "\n\n".join(chunks)


# ---------------------------------------------------------------------------
# pandoc render
# ---------------------------------------------------------------------------
HERE = Path(__file__).parent


def pandoc_render(node, md_text, pdf_path, landscape_cols):
    fd, tmp = tempfile.mkstemp(suffix=".md", prefix="swatpdf-")
    md_file = Path(tmp)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(md_text)
    multi = len(node.src_files) > 1
    title = "SWAT+ Documentation" if node.type == "root" else node.title
    cmd = [
        "pandoc", str(md_file), "-o", str(pdf_path),
        "--pdf-engine=xelatex",
        "-f", "markdown+pipe_tables+grid_tables+backtick_code_blocks+fenced_divs+raw_tex-yaml_metadata_block",
        "-H", str(HERE / "header.tex"),
        "--lua-filter", str(HERE / "landscape.lua"),
        "-M", f"landscape-cols={landscape_cols}",
        "-V", "geometry:margin=2cm",
        "-V", "colorlinks=true", "-V", "linkcolor=RoyalBlue", "-V", "urlcolor=RoyalBlue",
        "-V", "documentclass=" + ("report" if multi else "article"),
        "-V", f"title={latex_escape(title)}",
    ]
    if multi:
        cmd += ["--toc", "--toc-depth=2", "--top-level-division=chapter",
                "-V", "subtitle=SWAT+ Documentation", "-V", "date=swat-model.github.io/swatplus-documentation"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"pandoc failed for {node.slug}:\n{r.stderr[-2000:]}")
    finally:
        md_file.unlink(missing_ok=True)


def pdf_pages(pdf_path):
    try:
        out = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        return int(m.group(1)) if m else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# caching + orchestration
# ---------------------------------------------------------------------------
def node_hash(node, docs_dir, template_hash, landscape_cols, site_url):
    h = hashlib.sha256()
    h.update(f"v{SCRIPT_VERSION}|{landscape_cols}|{site_url}|".encode())
    h.update(template_hash.encode())
    for rel in node.src_files:
        h.update(rel.encode())
        h.update((docs_dir / rel).read_bytes())
    return h.hexdigest()


def build_one(node, docs_dir, out_dir, cache_dir, prefix, site_url, landscape_cols, template_hash):
    pdf_out = out_dir / "pdf" / node.pdf
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    flat = node.slug.replace("/", "__")
    cache_pdf = cache_dir / (flat + ".pdf")
    cache_hash = cache_dir / (flat + ".hash")
    want = node_hash(node, docs_dir, template_hash, landscape_cols, site_url)
    cached = cache_hash.read_text().strip() if cache_hash.exists() else None
    if cached == want and cache_pdf.exists():
        shutil.copy2(cache_pdf, pdf_out)
        return node, pdf_pages(pdf_out), "cache"
    md = render_markdown(node, docs_dir, prefix, site_url)
    pandoc_render(node, md, pdf_out, landscape_cols)
    cache_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf_out, cache_pdf)
    cache_hash.write_text(want)
    return node, pdf_pages(pdf_out), "build"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True, help="mkdocs site output dir")
    ap.add_argument("--cache", default=None)
    ap.add_argument("--site-url", default=None)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--landscape-cols", type=int, default=6)
    ap.add_argument("--only", default=None, help="build a single slug (debug)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    docs_dir = repo / "docs"
    out_dir = Path(args.out).resolve()
    cache_dir = Path(args.cache).resolve() if args.cache else (out_dir / "pdf" / ".cache")
    cfg = yaml.load((repo / "mkdocs.yml").read_text(), Loader=_Loader)
    site_url = args.site_url or cfg.get("site_url") or ""
    prefix = urlparse(site_url).path.rstrip("/") if site_url else ""

    Node._sec = 0
    top = walk(cfg["nav"], "", None)
    root = Node("root", cfg.get("site_name", "SWAT+ Documentation"))
    root.children = top
    for n in top:
        n.parent = root
    root.src_files = collect(top)

    nodes = []
    flatten([root], nodes)
    if args.only:
        nodes = [n for n in nodes if n.slug == args.only]

    template_hash = hashlib.sha256(
        (HERE / "header.tex").read_bytes() + (HERE / "landscape.lua").read_bytes()
    ).hexdigest()

    built = cached = failed = 0
    results = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(build_one, n, docs_dir, out_dir, cache_dir, prefix,
                          site_url, args.landscape_cols, template_hash): n for n in nodes}
        for fut in cf.as_completed(futs):
            n = futs[fut]
            try:
                node, pages, how = fut.result()
                results[n.slug] = pages
                if how == "cache":
                    cached += 1
                else:
                    built += 1
                print(f"[{how:5}] {n.pdf} ({pages}p)")
            except Exception as e:
                failed += 1
                print(f"[FAIL ] {n.slug}: {e}", file=sys.stderr)

    # manifest for the front-end
    manifest = {"site_url": site_url, "prefix": prefix, "nodes": []}
    for n in nodes:
        manifest["nodes"].append({
            "slug": n.slug,
            "type": n.type,
            "title": n.title if n.type != "root" else "Full Documentation",
            "pdf": f"{prefix}/pdf/{n.pdf}",
            "url": section_index_url(n, prefix),
            "parent": n.parent.slug if n.parent else None,
            "pages": results.get(n.slug),
        })
    (out_dir / "pdf" / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"\nbuilt={built} cached={cached} failed={failed} nodes={len(nodes)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
