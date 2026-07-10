"""Patch GCSE maths *_variants to return 3 tier variants and 3 MCQ variants per difficulty."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_LINE = "from generators.shared.variant_utils import select_tier_variants, mcq_variants_from_bank\n"

MCQ_BANK_MAP = {
    "sequences.py": ("_SEQ_MCQ_BANK", "sequences"),
    "equations_inequalities.py": ("_EQ_MCQ_BANK", "equations_inequalities"),
    "geometry_angles.py": ("_GEO_MCQ_BANK", "geometry_angles"),
    "transformations.py": ("_TRANS_MCQ_BANK", "transformations"),
    "maths_mensuration.py": ("_MENS_MCQ_BANK", "mensuration"),
    "maths_bearings.py": ("_BEAR_MCQ_BANK", "bearings"),
    "maths_circle_theorems.py": ("_CT_MCQ_BANK", "circle_theorems"),
    "maths_compound_measures.py": ("_CM_MCQ_BANK", "compound_measures"),
    "maths_similarity_congruence.py": ("_SC_MCQ_BANK", "similarity_congruence"),
    "maths_constructions_loci.py": ("_CL_MCQ_BANK", "constructions_loci"),
    "maths_pythagoras.py": ("_PY_MCQ_BANK", "pythagoras"),
}

NUM_STATS = {
    "maths_num_stats_prob_rat.py": [
        ("_NUMBER_MCQ_BANK", "number", "gcse_number_variants"),
        ("_RATIO_MCQ_BANK", "ratio_proportion", "gcse_ratio_proportion_variants"),
        ("_PROB_MCQ_BANK", "probability", "gcse_probability_variants"),
        ("_STATS_MCQ_BANK", "statistics", "gcse_statistics_variants"),
        ("_GRAPHS_MCQ_BANK", "graphs", "gcse_graphs_variants"),
    ],
}

MATHS_FILE = {
    "maths.py": [
        ("_VECTORS_MCQ_BANK", "vectors", "gcse_vectors_variants", "_VEC_MCQ_BANK"),
        ("_TRIG_MCQ_BANK", "trigonometry", "gcse_trigonometry_variants", None),
    ],
}


def ensure_import(text):
    if "variant_utils" in text:
        return text
    if "from generators.shared.utils import make_problem" in text:
        return text.replace(
            "from generators.shared.utils import make_problem",
            "from generators.shared.utils import make_problem\n" + IMPORT_LINE.strip(),
            1,
        )
    return IMPORT_LINE + text


def patch_mcq_return(text, bank, slug):
    patterns = [
        (rf"return \[(\w+_mcq)\] \* 15", f"return mcq_variants_from_bank({bank}, '{slug}', difficulty)"),
        (rf"return \[(\w+_mcq)\] \* 10", f"return mcq_variants_from_bank({bank}, '{slug}', difficulty)"),
    ]
    for pat, repl in patterns:
        text, n = re.subn(pat, repl, text)
        if n:
            return text
    return text


def patch_practice_return(text):
    old = r"    shuffled = random\.sample\(pool, len\(pool\)\)\n    return \(shuffled \* \(10 // len\(shuffled\) \+ 1\)\)\[:10\]"
    new = "    return select_tier_variants(pool, 3)"
    if re.search(old, text):
        return re.sub(old, new, text)
    # pythagoras style
    old2 = r"    pool = pools\[difficulty\]\n    return random\.sample\(pool, len\(pool\))"
    new2 = "    pool = pools[difficulty]\n    return select_tier_variants(pool, 3)"
    if re.search(old2, text):
        return re.sub(old2, new2, text)
    return text


def process_file(path: Path, banks):
    text = path.read_text(encoding="utf-8")
    orig = text
    text = ensure_import(text)
    for entry in banks:
        if len(entry) == 3:
            bank, slug, _ = entry
        else:
            bank, slug, _, alt = entry
            if alt and alt in text:
                bank = alt
        text = patch_mcq_return(text, bank, slug)
    text = patch_practice_return(text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    updated = []
    gcse = ROOT / "generators" / "gcse"
    for fname, banks in MCQ_BANK_MAP.items():
        p = gcse / fname
        if p.exists() and process_file(p, [(b, s, "") for b, s in MCQ_BANK_MAP[fname]]):
            updated.append(fname)

    p = gcse / "maths_num_stats_prob_rat.py"
    if p.exists():
        text = p.read_text(encoding="utf-8")
        orig = text
        text = ensure_import(text)
        for bank, slug, _ in NUM_STATS["maths_num_stats_prob_rat.py"]:
            text = patch_mcq_return(text, bank, slug)
        text = patch_practice_return(text)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            updated.append("maths_num_stats_prob_rat.py")

    # vectors/trig - find bank names in maths.py
    mp = gcse / "maths.py"
    if mp.exists():
        text = mp.read_text(encoding="utf-8")
        orig = text
        if "variant_utils" not in text:
            text = text.replace(
                "from generators.shared.utils import make_problem",
                "from generators.shared.utils import make_problem\n" + IMPORT_LINE.strip(),
                1,
            )
        text = patch_mcq_return(text, "_VECTORS_MCQ_BANK", "vectors") if "_VECTORS_MCQ_BANK" in text else patch_mcq_return(text, "questions", "vectors")
        # vectors uses inline `questions` list in vectors_mcq
        text = re.sub(
            r"if mode == 'mcq':\n        return \[vectors_mcq\] \* 10",
            "if mode == 'mcq':\n        return mcq_variants_from_bank(_VECTORS_MCQ_BANK, 'vectors', difficulty)",
            text,
            count=1,
        ) if "_VECTORS_MCQ_BANK" not in text else text
        text = patch_mcq_return(text, "_TRIG_MCQ_BANK", "trigonometry") if "_TRIG_MCQ_BANK" in text else patch_mcq_return(text, "_TRIG_MCQ_BANK", "trigonometry")
        text = re.sub(
            r"if mode == 'mcq':\n        return \[trigonometry_mcq\] \* 15",
            "if mode == 'mcq':\n        return mcq_variants_from_bank(_TRIG_MCQ_BANK, 'trigonometry', difficulty)",
            text,
            count=1,
        )
        text = patch_practice_return(text)
        if text != orig:
            mp.write_text(text, encoding="utf-8")
            updated.append("maths.py")

    print("Updated:", updated)


if __name__ == "__main__":
    main()
