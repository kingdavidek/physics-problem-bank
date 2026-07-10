"""Set GCSE maths variant functions to 3 practice + 3 MCQ variants per tier."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GCSE = ROOT / "generators" / "gcse"

IMPORT = "from generators.shared.variant_utils import select_tier_variants, mcq_variants_from_bank, mcq_variants_from_fn\n"

PRACTICE_TAIL_OLD = re.compile(
    r"    shuffled = random\.sample\(pool, len\(pool\)\)\n"
    r"    return \(shuffled \* \(10 // len\(shuffled\) \+ 1\)\)\[:10\]"
)
PRACTICE_TAIL_NEW = "    return select_tier_variants(pool, 3)"

PYTHAGORAS_OLD = re.compile(
    r"    pool = pools\[difficulty\]\n    return random\.sample\(pool, len\(pool\)\)"
)
PYTHAGORAS_NEW = "    pool = pools[difficulty]\n    return select_tier_variants(pool, 3)"

MCQ_PATTERNS = [
    (re.compile(r"return \[[\w]+_mcq\] \* 15"), None),
    (re.compile(r"return \[[\w]+_mcq\] \* 10"), None),
]

# (filename, [(mcq_old_pattern, mcq_new), ...])  — applied per file
FILE_MCQ = {
    "sequences.py": ("sequences_mcq", "_SEQ_MCQ_BANK", "sequences"),
    "equations_inequalities.py": ("equations_inequalities_mcq", None, "equations_inequalities"),
    "geometry_angles.py": ("geometry_angles_mcq", "_GEOM_MCQ_BANK", "geometry_angles"),
    "transformations.py": ("transformations_mcq", "_TRANS_MCQ_BANK", "transformations"),
    "maths_mensuration.py": ("mensuration_mcq", "_MENS_MCQ_BANK", "mensuration"),
    "maths_bearings.py": ("bearings_mcq", "_BRG_MCQ_BANK", "bearings"),
    "maths_circle_theorems.py": ("circle_theorems_mcq", "_CT_MCQ_BANK", "circle_theorems"),
    "maths_compound_measures.py": ("compound_measures_mcq", "_CM_MCQ_BANK", "compound_measures"),
    "maths_similarity_congruence.py": ("similarity_congruence_mcq", "_SC_MCQ_BANK", "similarity_congruence"),
    "maths_constructions_loci.py": ("constructions_loci_mcq", "_CL_MCQ_BANK", "constructions_loci"),
    "maths_pythagoras.py": ("pythagoras_mcq", "_PY_MCQ_BANK", "pythagoras"),
}

NUM_STATS_MCQ = [
    ("number_mcq", "number"),
    ("ratio_proportion_mcq", "ratio_proportion"),
    ("probability_mcq", "probability"),
    ("statistics_mcq", "statistics"),
    ("graphs_mcq", "graphs"),
]


def ensure_import(text):
    if "variant_utils" in text:
        return text
    anchor = "from generators.shared.utils import make_problem"
    if anchor in text:
        return text.replace(anchor, anchor + "\n" + IMPORT.strip(), 1)
    return IMPORT + text


def patch_file(path: Path, mcq_fn=None, bank=None, slug=None, procedural=False):
    text = path.read_text(encoding="utf-8")
    orig = text
    text = ensure_import(text)

    if mcq_fn and slug:
        if procedural:
            repl = f"return mcq_variants_from_fn({mcq_fn}, '{slug}', difficulty)"
        elif bank:
            repl = f"return mcq_variants_from_bank({bank}, '{slug}', difficulty)"
        else:
            repl = f"return mcq_variants_from_fn({mcq_fn}, '{slug}', difficulty)"
        text = re.sub(
            rf"return \[{re.escape(mcq_fn)}\] \* (?:10|15)",
            repl,
            text,
        )

    if PRACTICE_TAIL_OLD.search(text):
        text = PRACTICE_TAIL_OLD.sub(PRACTICE_TAIL_NEW, text)
    if PYTHAGORAS_OLD.search(text):
        text = PYTHAGORAS_OLD.sub(PYTHAGORAS_NEW, text)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def patch_mcq_generator_call(text, mcq_fn, variants_fn):
    """Use run_mcq_variant in main generator mcq branch."""
    if "run_mcq_variant" in text:
        return text
    old = (
        f"        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = {mcq_fn}()\n"
    )
    new = (
        f"        variants = {variants_fn}(difficulty, 'mcq')\n"
        f"        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(\n"
        f"            variants, variant_name\n"
        f"        )\n"
    )
    if old in text:
        if "run_mcq_variant" not in text:
            text = text.replace(
                "from generators.shared.variant_utils import select_tier_variants, mcq_variants_from_bank, mcq_variants_from_fn",
                "from generators.shared.variant_utils import select_tier_variants, mcq_variants_from_bank, mcq_variants_from_fn, run_mcq_variant",
            )
        return text.replace(old, new, 1)
    return text


def main():
    updated = []
    for fname, (mcq_fn, bank, slug) in FILE_MCQ.items():
        p = GCSE / fname
        if p.exists() and patch_file(p, mcq_fn, bank, slug):
            updated.append(fname)
            text = p.read_text(encoding="utf-8")
            # guess variants function name
            vfn = f"gcse_{slug}_variants"
            if slug == "equations_inequalities":
                vfn = "gcse_equations_inequalities_variants"
            new_text = patch_mcq_generator_call(text, mcq_fn, vfn)
            if new_text != text:
                p.write_text(new_text, encoding="utf-8")

    p = GCSE / "maths_num_stats_prob_rat.py"
    if p.exists():
        text = ensure_import(p.read_text(encoding="utf-8"))
        orig = text
        for mcq_fn, slug in NUM_STATS_MCQ:
            text = re.sub(
                rf"return \[{re.escape(mcq_fn)}\] \* 10",
                f"return mcq_variants_from_fn({mcq_fn}, '{slug}', difficulty)",
                text,
            )
        text = PRACTICE_TAIL_OLD.sub(PRACTICE_TAIL_NEW, text)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            updated.append("maths_num_stats_prob_rat.py")

    print("Updated:", sorted(set(updated)))


if __name__ == "__main__":
    main()
