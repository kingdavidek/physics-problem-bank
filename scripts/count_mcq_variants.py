"""Count distinct MCQ question variants per topic."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from topic_registry import TOPICS
from generators.shared.lesson_quiz import topic_supports_lesson_mcq

def read_text(rel_path):
    return (ROOT / rel_path).read_text(encoding="utf-8")


def count_bank(src, bank_name):
    m = re.search(rf"{re.escape(bank_name)}\s*=\s*\[(.*?)\n\]", src, re.S)
    if not m:
        return None
    body = m.group(1)
    return body.count('"q":') + body.count("'q':")


def count_dispatch_pool(src, dispatch_name):
    m = re.search(
        rf"def {re.escape(dispatch_name)}\(\):.*?return random\.choice\(\[(.*?)\]\)",
        src,
        re.S,
    )
    if not m:
        return None
    return len(re.findall(r"_\w+_mcq_\w+", m.group(1)))


def count_inline_questions_list(src, fn_name):
    m = re.search(rf"def {re.escape(fn_name)}\(\):.*?questions\s*=\s*\[(.*?)\n\s*\]", src, re.S)
    if not m:
        return None
    return m.group(1).count('"q":') + m.group(1).count("'q':")


def count_random_int_branches(src, fn_name):
    m = re.search(rf"def {re.escape(fn_name)}\(\):(.*?)(?=\ndef |\Z)", src, re.S)
    if not m:
        return None
    body = m.group(1)
    ints = [int(x) for x in re.findall(r"mcq_type\s*==\s*(\d+)", body)]
    if ints:
        return max(ints)
    ints = [int(x) for x in re.findall(r"random\.randint\(1,\s*(\d+)\)", body)]
    return ints[0] if ints else None


TOPIC_SOURCES = {
    # procedural dispatch pools
    "algebraic_fractions": ("generators/gcse/algebraic_fractions.py", "dispatch", "_af_mcq_dispatch"),
    "algebraic_proof": ("generators/gcse/algebraic_proof.py", "dispatch", "_ap_mcq_dispatch"),
    "completing_the_square": ("generators/gcse/completing_the_square.py", "dispatch", "_cts_mcq_dispatch"),
    "functions": ("generators/gcse/functions.py", "dispatch", "_fn_mcq_dispatch"),
    "graphical_simultaneous_equations": ("generators/gcse/graphical_simultaneous_equations.py", "dispatch", "_gsim_mcq_dispatch"),
    "changing_the_subject": ("generators/gcse/changing_the_subject.py", "dispatch", "_cts_mcq_dispatch"),
    "quadratic_simultaneous_equations": ("generators/gcse/quadratic_simultaneous_equations.py", "dispatch", "_qsim_mcq_dispatch"),
    # banks
    "simultaneous_equations": ("generators/gcse/simultaneous_equations.py", "bank", "_SIM_MCQ_BANK"),
    "circle_theorems": ("generators/gcse/maths_circle_theorems.py", "bank", "_CT_MCQ_BANK"),
    "mensuration": ("generators/gcse/maths_mensuration.py", "bank", "_MENS_MCQ_BANK"),
    "geometry_angles": ("generators/gcse/geometry_angles.py", "bank", "_GEOM_MCQ_BANK"),
    "similarity_congruence": ("generators/gcse/maths_similarity_congruence.py", "bank", "_SC_MCQ_BANK"),
    "pythagoras": ("generators/gcse/maths_pythagoras.py", "bank", "_PY_MCQ_BANK"),
    "bearings": ("generators/gcse/maths_bearings.py", "bank", "_BRG_MCQ_BANK"),
    "constructions_loci": ("generators/gcse/maths_constructions_loci.py", "bank", "_CL_MCQ_BANK"),
    "sequences": ("generators/gcse/sequences.py", "bank", "_SEQ_MCQ_BANK"),
    "compound_measures": ("generators/gcse/maths_compound_measures.py", "bank", "_CM_MCQ_BANK"),
    "transformations": ("generators/gcse/transformations.py", "bank", "_TRANS_MCQ_BANK"),
    "vectors": ("generators/gcse/maths.py", "bank", "_VECTORS_MCQ_BANK"),
    "trigonometry": ("generators/gcse/maths.py", "bank", "_TRIG_MCQ_BANK"),
    "data_rep": ("generators/gcse/cs_data_rep.py", "bank", "_DR_MCQ_BANK"),
    "algorithms": ("generators/gcse/cs_algorithms.py", "bank", "_ALG_MCQ_BANK"),
    "computer_systems": ("generators/gcse/cs_computer_systems.py", "bank", "_CS_MCQ_BANK"),
    "computer_networks": ("generators/gcse/cs_computer_networks.py", "bank", "_NET_MCQ_BANK"),
    "cyber_security": ("generators/gcse/cs_cyber_security.py", "bank", "_CY_MCQ_BANK"),
    "db_sql": ("generators/gcse/gcse_cs_db_sql_lesson.py", "bank", "_DB_MCQ_BANK"),
    "ethical": ("generators/gcse/gcse_cs_ethical_lesson.py", "bank", "_ETH_MCQ_BANK"),
    "systems_software": ("generators/gcse/gcse_cs_systems_software_lesson.py", "bank", "_SW_MCQ_BANK"),
    "bidmas": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_BIDMAS_MCQ_BANK"),
    "fdp": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_FDP_MCQ_BANK"),
    "multiples_factors": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_MF_MCQ_BANK"),
    "decimals": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_DEC_MCQ_BANK"),
    "algebra": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_ALG_MCQ_BANK"),
    "surds": ("generators/gcse/maths_basic_topics_mcq.py", "bank", "_SURD_MCQ_BANK"),
    # inline question lists / branch counts
    "equations_inequalities": ("generators/gcse/equations_inequalities.py", "inline", "equations_inequalities_mcq"),
    "number": ("generators/gcse/maths_num_stats_prob_rat.py", "branches", "number_mcq"),
    "ratio_proportion": ("generators/gcse/maths_num_stats_prob_rat.py", "branches", "ratio_proportion_mcq"),
    "probability": ("generators/gcse/maths_num_stats_prob_rat.py", "branches", "probability_mcq"),
    "statistics": ("generators/gcse/maths_num_stats_prob_rat.py", "branches", "statistics_mcq"),
    "graphs": ("generators/gcse/maths_num_stats_prob_rat.py", "branches", "graphs_mcq"),
    "python_programming": ("generators/gcse/cs.py", "inline", "py_mcq"),
}


def count_topic(slug):
    if slug not in TOPIC_SOURCES:
        return None, None
    path, kind, name = TOPIC_SOURCES[slug]
    src = read_text(path)
    if kind == "dispatch":
        return count_dispatch_pool(src, name), "procedural (randomised)"
    if kind == "bank":
        return count_bank(src, name), "fixed bank"
    if kind == "inline":
        return count_inline_questions_list(src, name), "fixed bank"
    if kind == "branches":
        return count_random_int_branches(src, name), "procedural (randomised)"
    return None, None


def main():
    rows = []
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for slug, cfg in sorted(topics.items()):
                count, kind = count_topic(slug)
                quiz = topic_supports_lesson_mcq(cfg)
                rows.append((level, subject, slug, cfg.get("name", slug), count, kind, quiz))

    print(f"{'Level':<6} {'Subject':<14} {'Topic':<34} {'Variants':>8}  {'Type':<26} Quiz")
    print("-" * 100)
    for level, subject, slug, name, count, kind, quiz in rows:
        variants = str(count) if count is not None else ("—" if not quiz else "?")
        kind_str = kind or ("no MCQ" if not quiz else "unknown")
        print(f"{level:<6} {subject:<14} {slug:<34} {variants:>8}  {kind_str:<26} {'Yes' if quiz else 'No'}")

    with_mcq = [r for r in rows if r[4] is not None]
    print()
    print(f"Topics with MCQ: {len(with_mcq)} / {len(rows)}")
    print(f"Total variants (sum): {sum(r[4] for r in with_mcq)}")


if __name__ == "__main__":
    main()
