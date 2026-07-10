"""Count standard (practice) problem variants per topic and difficulty tier."""
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from topic_registry import TOPICS
from generators.gcse.maths_basic_topics_mcq import _practice_pools
from generators.gcse import cs as cs_mod

DIFFS = ["foundational", "intermediate", "difficult"]
POOL_ATTRS = {
    "foundational": ["_FOUNDATIONAL", "_found_pool", "found_pool"],
    "intermediate": ["_INTERMEDIATE", "_inter_pool", "inter_pool"],
    "difficult": ["_DIFFICULT", "_diff_pool", "diff_pool"],
}
LIST_VAR_NAMES = {
    "foundational": ["foundational", "found", "found_pool", "_MAG_FOUND_POOL"],
    "intermediate": ["intermediate", "inter", "inter_pool", "_MAG_INTER_POOL"],
    "difficult": ["difficult", "diff", "diff_pool", "_MAG_DIFFICULT_POOL", "_MAG_DIFF_POOL"],
}


def count_list_var(text, var_name):
    m = re.search(rf"{re.escape(var_name)}\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    refs = re.findall(r"\b[_a-z][\w]*", body)
    return len(refs) if refs else len(split_pool_items(body))


def split_pool_items(body):
    items = re.split(r",(?=\s*(?:m\.)?[_\w]+)", body)
    return [x.strip() for x in items if x.strip() and not x.strip().startswith("#")]


def count_from_pools_dict(mod):
    for name in ("_POOLS", "_PRACTICE_POOLS"):
        if hasattr(mod, name):
            d = getattr(mod, name)
            if isinstance(d, dict):
                out = {}
                for diff in DIFFS:
                    if diff in d and isinstance(d[diff], list):
                        out[diff] = len(d[diff])
                if out:
                    return out
    return None


def count_from_module_attrs(mod):
    out = {}
    for diff, attrs in POOL_ATTRS.items():
        for attr in attrs:
            if hasattr(mod, attr):
                val = getattr(mod, attr)
                if isinstance(val, list):
                    out[diff] = len(val)
                    break
    return out


def parse_inline_pools_from_text(text):
    out = {}

    # pools = {"foundational": [...], ...} inside variants_func
    m_pools = re.search(
        r'pools\s*=\s*\{.*?'
        r'"foundational"\s*:\s*\[(.*?)\].*?'
        r'"intermediate"\s*:\s*\[(.*?)\].*?'
        r'"difficult"\s*:\s*\[(.*?)\]',
        text,
        re.DOTALL,
    )
    if m_pools:
        out["foundational"] = len(split_pool_items(m_pools.group(1)))
        out["intermediate"] = len(split_pool_items(m_pools.group(2)))
        out["difficult"] = len(split_pool_items(m_pools.group(3)))
        return out

    # found / foundational / inter / diff list variables
    named = {}
    for diff, var_names in LIST_VAR_NAMES.items():
        for vn in var_names:
            n = count_list_var(text, vn)
            if n:
                named[diff] = n
                break
    if len(named) == 3:
        return named

    for diff in DIFFS:
        pat = (
            rf"(?:if|elif)\s+difficulty\s*==\s*['\"]{diff}['\"].*?"
            rf"pool\s*=\s*\[(.*?)\]"
        )
        m = re.search(pat, text, re.DOTALL)
        if m:
            out[diff] = len(split_pool_items(m.group(1)))
            continue
        # pool = found / inter / diff
        short = {"foundational": "found", "intermediate": "inter", "difficult": "diff"}[diff]
        m3 = re.search(
            rf"(?:if|elif)\s+difficulty\s*==\s*['\"]{diff}['\"].*?pool\s*=\s*{short}\b",
            text,
            re.DOTALL,
        )
        if m3 and diff in named:
            out[diff] = named[diff]

    if out:
        return out

    # random.choice([...]) per tier (physics-style)
    for diff in DIFFS:
        pat = (
            rf"(?:if|elif)\s+difficulty\s*==\s*['\"]{diff}['\"].*?"
            rf"random\.choice\(\[(.*?)\]\)"
        )
        m = re.search(pat, text, re.DOTALL)
        if m:
            out[diff] = len(split_pool_items(m.group(1)))
        elif diff == "difficult":
            m2 = re.search(r"else:\s*.*?random\.choice\(\[(.*?)\]\)", text, re.DOTALL)
            if m2:
                out["difficult"] = len(split_pool_items(m2.group(1)))
    return out


def parse_inline_pools(func):
    try:
        return parse_inline_pools_from_text(inspect.getsource(func))
    except OSError:
        return {}


def served_per_request(vf, pool_size):
    try:
        served = len(vf("foundational", "practice"))
    except TypeError:
        try:
            served = len(vf("foundational", mode="practice"))
        except Exception:
            return None
    except Exception:
        return None
    return served


def count_topic(level, subject, slug, cfg):
    vf = cfg.get("variants_func")
    counts = None
    source = None

    if slug in ("bidmas", "fdp", "multiples_factors", "decimals", "algebra", "surds"):
        pools = _practice_pools(slug)
        counts = {d: len(pools.get(d, [])) for d in DIFFS}
        source = "maths_basic practice pools"
    elif slug == "python_programming":
        counts = parse_inline_pools(cs_mod.gcse_python_variants)
        source = "cs.py python pools"
    elif vf:
        mod = inspect.getmodule(vf)
        counts = count_from_pools_dict(mod)
        source = "_POOLS" if counts else None
        if not counts:
            counts = count_from_module_attrs(mod)
            source = "module pool lists" if counts else None
        if not counts or len(counts) < 3:
            parsed = parse_inline_pools(vf)
            if parsed:
                counts = {**(counts or {}), **parsed}
                source = (source + " + inline") if source else "inline pools in variants_func"

    total = sum(counts.values()) if counts else None
    served = served_per_request(vf, counts.get("foundational") if counts else None) if vf else None

    return {
        "level": level,
        "subject": subject,
        "slug": slug,
        "name": cfg.get("name", slug),
        "counts": counts,
        "total": total,
        "served": served,
        "has_vf": bool(vf),
        "source": source,
    }


def patch_from_file(rows, slug, rel_path, func_name=None):
    text = (ROOT / rel_path).read_text(encoding="utf-8")
    if func_name:
        m = re.search(rf"def {re.escape(func_name)}.*?(?=\ndef |\Z)", text, re.DOTALL)
        text = m.group(0) if m else text
    counts = parse_inline_pools_from_text(text)
    for r in rows:
        if r["slug"] == slug:
            r["counts"] = counts or None
            r["total"] = sum(counts.values()) if counts else None
            r["source"] = f"parsed {rel_path}" if counts else "no tier pools found"
            break


def main():
    rows = []
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for slug, cfg in topics.items():
                rows.append(count_topic(level, subject, slug, cfg))

    patch_from_file(rows, "forces", "generators/gcse/physics_forces.py", "gcse_physics_forces")
    patch_from_file(
        rows,
        "radioactivity",
        "generators/gcse/physics.py",
        "edexcel_combined_physics_radioactivity",
    )
    # magnetism uses module-level _MAG_*_POOL lists
    mag_text = (ROOT / "generators/alevel/magnetism.py").read_text(encoding="utf-8")
    mag_counts = {}
    for diff, var_names in LIST_VAR_NAMES.items():
        for vn in var_names:
            n = count_list_var(mag_text, vn)
            if n:
                mag_counts[diff] = n
                break
    for r in rows:
        if r["slug"] == "magnetism":
            r["counts"] = mag_counts or None
            r["total"] = sum(mag_counts.values()) if mag_counts else None
            r["source"] = "magnetism _MAG_*_POOL"
            break

    patch_from_file(
        rows,
        "photoelectric",
        "generators/alevel/photoelectric.py",
        "alevel_physics_photoelectric_variants",
    )

    # MYP topics — check for pools in generator files
    # MYP redox: procedural scenario lists per tier
    redox_text = (ROOT / "generators/myp/chemistry.py").read_text(encoding="utf-8")
    m = re.search(r"def myp_chemistry_redox.*?(?=\ndef )", redox_text, re.DOTALL)
    redox_counts = {}
    if m:
        body = m.group(0)
        for diff, key in [
            ("foundational", "scenarios"),
            ("intermediate", "compounds"),
            ("difficult", "reactions"),
        ]:
            m2 = re.search(
                rf"difficulty\s*==\s*['\"]{diff}['\"].*?{key}\s*=\s*\[(.*?)\]",
                body,
                re.DOTALL,
            )
            if m2:
                redox_counts[diff] = m2.group(1).count("(") or len(split_pool_items(m2.group(1)))
    for r in rows:
        if r["slug"] == "redox":
            r["counts"] = redox_counts or None
            r["total"] = sum(redox_counts.values()) if redox_counts else None
            r["source"] = "myp redox scenario lists"
            break
    patch_from_file(
        rows,
        "energy_changes_and_rates",
        "generators/myp/chemistry.py",
        "myp_chemistry_energy_changes_and_rates",
    )

    print(
        f"{'Level':<7} {'Subject':<10} {'Topic':<30} {'Found':>5} {'Inter':>5} {'Diff':>5} "
        f"{'Total':>5} {'Served':>6}"
    )
    print("-" * 95)

    for r in sorted(rows, key=lambda x: (x["level"], x["subject"], x["slug"])):
        c = r["counts"] or {}
        f = c.get("foundational", "—")
        i = c.get("intermediate", "—")
        d = c.get("difficult", "—")
        t = r["total"] if r["total"] is not None else "—"
        s = r["served"] if r["served"] is not None else "—"
        print(
            f"{r['level']:<7} {r['subject']:<10} {r['slug']:<30} {str(f):>5} {str(i):>5} {str(d):>5} "
            f"{str(t):>5} {str(s):>6}"
        )

    print()
    print("Served = variants returned per practice request (foundational tier sample).")
    print("Most topics use select_tier_variants with default max 7; some algebra topics use 5.")


if __name__ == "__main__":
    main()
