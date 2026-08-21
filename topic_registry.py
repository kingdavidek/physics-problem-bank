#topic registry


from generators.gcse.physics_forces import (gcse_physics_forces,)
from generators.gcse.physics import (edexcel_combined_physics_radioactivity,)
from generators.myp.chemistry import (myp_chemistry_redox, myp_chemistry_energy_changes_and_rates,)
from generators.gcse.maths import (
    gcse_maths_algebra,gcse_maths_surds,gcse_maths_decimals,gcse_maths_bidmas,
    gcse_maths_fdp,gcse_maths_multiples_factors,gcse_vectors,gcse_vectors_variants,
    gcse_trigonometry,gcse_trigonometry_variants,)
from generators.gcse.maths_basic_topics_mcq import (
    gcse_maths_algebra_variants,
    gcse_maths_surds_variants,
    gcse_maths_decimals_variants,
    gcse_maths_bidmas_variants,
    gcse_maths_fdp_variants,
    gcse_maths_multiples_factors_variants,
)
from generators.gcse.equations_inequalities import (
    gcse_equations_inequalities, gcse_equations_inequalities_variants,)
from generators.gcse.simultaneous_equations import (
    gcse_simultaneous_equations, gcse_simultaneous_equations_variants,)
from generators.gcse.completing_the_square import (
    gcse_completing_the_square, gcse_completing_the_square_variants,)
from generators.gcse.quadratic_simultaneous_equations import (
    gcse_quadratic_simultaneous_equations,
    gcse_quadratic_simultaneous_equations_variants,
)
from generators.gcse.graphical_simultaneous_equations import (
    gcse_graphical_simultaneous_equations,
    gcse_graphical_simultaneous_equations_variants,
)
from generators.gcse.changing_the_subject import (
    gcse_changing_the_subject,
    gcse_changing_the_subject_variants,
)
from generators.gcse.functions import (
    gcse_functions,
    gcse_functions_variants,
)
from generators.gcse.algebraic_fractions import (
    gcse_algebraic_fractions,
    gcse_algebraic_fractions_variants,
)
from generators.gcse.algebraic_proof import (
    gcse_algebraic_proof,
    gcse_algebraic_proof_variants,
)
from generators.gcse.sequences import (
    gcse_sequences, gcse_sequences_variants,)
from generators.gcse.geometry_angles import (
    gcse_geometry_angles, gcse_geometry_angles_variants,)
from generators.gcse.transformations import (
    gcse_transformations, gcse_transformations_variants,)
from generators.gcse.maths_mensuration import (
    gcse_mensuration, gcse_mensuration_variants,)
from generators.gcse.maths_bearings import (
    gcse_bearings, gcse_bearings_variants,)
from generators.gcse.maths_circle_theorems import (
    gcse_circle_theorems, gcse_circle_theorems_variants,)
from generators.gcse.maths_compound_measures import (
    gcse_compound_measures, gcse_compound_measures_variants,)
from generators.gcse.maths_similarity_congruence import (
    gcse_similarity_congruence, gcse_similarity_congruence_variants,)
from generators.gcse.maths_constructions_loci import (
    gcse_constructions_loci, gcse_constructions_loci_variants,)
from generators.gcse.maths_pythagoras import (
    gcse_pythagoras, gcse_pythagoras_variants,)
from generators.gcse.maths_num_stats_prob_rat import (
    gcse_number, gcse_number_variants,
    gcse_ratio_proportion, gcse_ratio_proportion_variants,
    gcse_probability, gcse_probability_variants,
    gcse_statistics, gcse_statistics_variants,gcse_graphs_variants,gcse_graphs)
from generators.alevel.magnetism import alevel_physics_magnetism
from generators.alevel.photoelectric import (
    alevel_physics_photoelectric,
    alevel_physics_photoelectric_variants,
)
from generators.alevel.particles import (
    alevel_physics_particles,
    alevel_physics_particles_variants,
)
from generators.gcse.cs import gcse_python_programming
from generators.gcse.cs_algorithms import gcse_algorithms, gcse_algorithms_variants
from generators.gcse.cs_data_rep import gcse_data_rep, gcse_data_rep_variants
from generators.gcse.cs_computer_systems import gcse_computer_systems, gcse_computer_systems_variants
from generators.gcse.cs_computer_networks import gcse_computer_networks, gcse_computer_networks_variants
from generators.gcse.cs_cyber_security import gcse_cyber_security, gcse_cyber_security_variants
from generators.gcse.gcse_cs_db_sql_lesson import gcse_db_sql, gcse_db_sql_variants
from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical, gcse_ethical_variants
from generators.gcse.gcse_cs_systems_software_lesson import gcse_systems_software, gcse_systems_software_variants

#from generators.gcse.cs import (
#    gcse_cs_binary,
#)



TOPICS = {
    "gcse": {
        "maths": {
            "bidmas": {
                "name": "Order of Operations & Negatives",
                "order": 1,
                "func": gcse_maths_bidmas,
                "variants_func": gcse_maths_bidmas_variants,
            },
            "multiples_factors": {
                "name": "Multiples and Factors",
                "order": 2,
                "func": gcse_maths_multiples_factors,
                "variants_func": gcse_maths_multiples_factors_variants,
            },
            "decimals": {
                "name": "Decimals",
                "order": 3,
                "func": gcse_maths_decimals,
                "variants_func": gcse_maths_decimals_variants,
            },
            "fdp": {
                "name": "Fractions, Decimals and Percentages",
                "order": 4,
                "prereqs": ["decimals"],
                "func": gcse_maths_fdp,
                "variants_func": gcse_maths_fdp_variants,
            },
            "number": {
                "name": "Number",
                "order": 5,
                "func": gcse_number,
                "variants_func": gcse_number_variants,
            },
            "ratio_proportion": {
                "name": "Ratio and Proportion",
                "order": 6,
                "func": gcse_ratio_proportion,
                "variants_func": gcse_ratio_proportion_variants,
            },
            "algebra": {
                "name": "Algebra",
                "order": 7,
                "prereqs": ["bidmas"],
                "func": gcse_maths_algebra,
                "variants_func": gcse_maths_algebra_variants,
            },
            "equations_inequalities": {
                "name": "Equations and Inequalities",
                "order": 8,
                "prereqs": ["algebra"],
                "func": gcse_equations_inequalities,
                "variants_func": gcse_equations_inequalities_variants,
            },
            "changing_the_subject": {
                "name": "Changing the Subject",
                "order": 9,
                "prereqs": ["algebra"],
                "func": gcse_changing_the_subject,
                "variants_func": gcse_changing_the_subject_variants,
            },
            "sequences": {
                "name": "Sequences",
                "order": 10,
                "prereqs": ["algebra"],
                "func": gcse_sequences,
                "variants_func": gcse_sequences_variants,
            },
            "surds": {
                "name": "Surds",
                "order": 11,
                "prereqs": ["algebra"],
                "func": gcse_maths_surds,
                "variants_func": gcse_maths_surds_variants,
            },
            "simultaneous_equations": {
                "name": "Simultaneous Equations",
                "order": 12,
                "prereqs": ["algebra", "equations_inequalities"],
                "func": gcse_simultaneous_equations,
                "variants_func": gcse_simultaneous_equations_variants,
            },
            "completing_the_square": {
                "name": "Completing the Square",
                "order": 13,
                "prereqs": ["algebra"],
                "func": gcse_completing_the_square,
                "variants_func": gcse_completing_the_square_variants,
            },
            "quadratic_simultaneous_equations": {
                "name": "Quadratic Simultaneous Equations",
                "order": 14,
                "prereqs": ["simultaneous_equations", "completing_the_square"],
                "func": gcse_quadratic_simultaneous_equations,
                "variants_func": gcse_quadratic_simultaneous_equations_variants,
            },
            "graphs": {
                "name": "Graphs",
                "order": 15,
                "prereqs": ["algebra"],
                "func": gcse_graphs,
                "variants_func": gcse_graphs_variants,
            },
            "graphical_simultaneous_equations": {
                "name": "Graphical Simultaneous Equations",
                "order": 16,
                "prereqs": ["simultaneous_equations", "graphs"],
                "func": gcse_graphical_simultaneous_equations,
                "variants_func": gcse_graphical_simultaneous_equations_variants,
            },
            "algebraic_fractions": {
                "name": "Algebraic Fractions",
                "order": 17,
                "prereqs": ["algebra"],
                "func": gcse_algebraic_fractions,
                "variants_func": gcse_algebraic_fractions_variants,
            },
            "functions": {
                "name": "Functions",
                "order": 18,
                "prereqs": ["algebra"],
                "func": gcse_functions,
                "variants_func": gcse_functions_variants,
            },
            "algebraic_proof": {
                "name": "Algebraic Proof",
                "order": 19,
                "prereqs": ["algebra"],
                "func": gcse_algebraic_proof,
                "variants_func": gcse_algebraic_proof_variants,
            },
            "geometry_angles": {
                "name": "Geometry and Angles",
                "order": 20,
                "func": gcse_geometry_angles,
                "variants_func": gcse_geometry_angles_variants,
            },
            "pythagoras": {
                "name": "Pythagoras' Theorem",
                "order": 21,
                "prereqs": ["geometry_angles"],
                "func": gcse_pythagoras,
                "variants_func": gcse_pythagoras_variants,
            },
            "trigonometry": {
                "name": "Trigonometry",
                "order": 22,
                "prereqs": ["pythagoras"],
                "func": gcse_trigonometry,
                "variants_func": gcse_trigonometry_variants,
            },
            "mensuration": {
                "name": "Mensuration",
                "order": 23,
                "prereqs": ["geometry_angles"],
                "func": gcse_mensuration,
                "variants_func": gcse_mensuration_variants,
            },
            "bearings": {
                "name": "Bearings",
                "order": 24,
                "prereqs": ["trigonometry"],
                "func": gcse_bearings,
                "variants_func": gcse_bearings_variants,
            },
            "transformations": {
                "name": "Transformations",
                "order": 25,
                "func": gcse_transformations,
                "variants_func": gcse_transformations_variants,
            },
            "similarity_congruence": {
                "name": "Similarity and Congruence",
                "order": 26,
                "prereqs": ["geometry_angles"],
                "func": gcse_similarity_congruence,
                "variants_func": gcse_similarity_congruence_variants,
            },
            "circle_theorems": {
                "name": "Circle Theorems",
                "order": 27,
                "prereqs": ["geometry_angles"],
                "func": gcse_circle_theorems,
                "variants_func": gcse_circle_theorems_variants,
            },
            "constructions_loci": {
                "name": "Constructions and Loci",
                "order": 28,
                "prereqs": ["geometry_angles"],
                "func": gcse_constructions_loci,
                "variants_func": gcse_constructions_loci_variants,
            },
            "compound_measures": {
                "name": "Compound Measures",
                "order": 29,
                "prereqs": ["ratio_proportion"],
                "func": gcse_compound_measures,
                "variants_func": gcse_compound_measures_variants,
            },
            "vectors": {
                "name": "Vectors",
                "order": 30,
                "prereqs": ["algebra"],
                "func": gcse_vectors,
                "variants_func": gcse_vectors_variants,
            },
            "statistics": {
                "name": "Statistics",
                "order": 31,
                "func": gcse_statistics,
                "variants_func": gcse_statistics_variants,
            },
            "probability": {
                "name": "Probability",
                "order": 32,
                "prereqs": ["statistics"],
                "func": gcse_probability,
                "variants_func": gcse_probability_variants,
            },
        },
        "physics": {
            "forces": {"name": "Forces", "order": 1, "func": gcse_physics_forces},
            "radioactivity": {
                "name": "Radioactivity",
                "order": 2,
                "func": edexcel_combined_physics_radioactivity,
            },
        },
        "cs": {
            "data_rep": {
                "name": "Fundamentals of Data Representation",
                "order": 1,
                "func": gcse_data_rep,
                "variants_func": gcse_data_rep_variants,
            },
            "systems_software": {
                "name": "Systems Software",
                "order": 2,
                "func": gcse_systems_software,
                "variants_func": gcse_systems_software_variants,
            },
            "algorithms": {
                "name": "Fundamentals of Algorithms",
                "order": 3,
                "func": gcse_algorithms,
                "variants_func": gcse_algorithms_variants,
            },
            "python_programming": {
                "name": "Python Programming",
                "order": 4,
                "prereqs": ["algorithms"],
                "func": gcse_python_programming,
            },
            "computer_systems": {
                "name": "Computer Systems",
                "order": 5,
                "prereqs": ["systems_software", "data_rep"],
                "func": gcse_computer_systems,
                "variants_func": gcse_computer_systems_variants,
            },
            "computer_networks": {
                "name": "Computer Networks",
                "order": 6,
                "prereqs": ["computer_systems"],
                "func": gcse_computer_networks,
                "variants_func": gcse_computer_networks_variants,
            },
            "cyber_security": {
                "name": "Cyber Security",
                "order": 7,
                "prereqs": ["computer_networks"],
                "func": gcse_cyber_security,
                "variants_func": gcse_cyber_security_variants,
            },
            "db_sql": {
                "name": "Relational Databases & SQL",
                "order": 8,
                "prereqs": ["data_rep"],
                "func": gcse_db_sql,
                "variants_func": gcse_db_sql_variants,
            },
            "ethical": {
                "name": "Ethical, Legal & Environmental Impacts",
                "order": 9,
                "func": gcse_ethical,
                "variants_func": gcse_ethical_variants,
            },
        },
    },
    "myp": {
        "chemistry": {
            "energy_changes_and_rates": {
                "name": "Energy Changes and Rates of Reaction",
                "order": 1,
                "func": myp_chemistry_energy_changes_and_rates,
            },
            "redox": {
                "name": "Redox Reactions",
                "order": 2,
                "prereqs": ["energy_changes_and_rates"],
                "func": myp_chemistry_redox,
            },
        },
    },
    "alevel": {
        "physics": {
            "particles": {
                "name": "Particle Physics & the Standard Model",
                "order": 1,
                "func": alevel_physics_particles,
                "variants_func": alevel_physics_particles_variants,
            },
            "magnetism": {
                "name": "Magnetic Fields",
                "order": 2,
                "prereqs": ["particles"],
                "func": alevel_physics_magnetism,
            },
            "photoelectric": {
                "name": "Photoelectric Effect and Wave-Particle Duality",
                "order": 3,
                "prereqs": ["particles"],
                "func": alevel_physics_photoelectric,
                "variants_func": alevel_physics_photoelectric_variants,
            },
        },
    },
}


def topic_sort_key(item):
    """Return a sort key for a (slug, cfg) topic pair."""
    slug, cfg = item
    order = cfg.get('order')
    if order is not None:
        return (0, order, '')
    return (1, 0, (cfg.get('name') or slug).lower())


def iter_topics(topics_dict):
    """Yield topics in syllabus order, falling back to name when order is absent."""
    return sorted(topics_dict.items(), key=topic_sort_key)


def validate_topic_registry():
    """Assert every topic has a unique order within its (level, subject) group."""
    errors = []
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            seen_orders = {}
            topic_slugs = set(topics.keys())
            for slug, cfg in topics.items():
                order = cfg.get('order')
                if order is None:
                    errors.append(f'{level}/{subject}/{slug}: missing order')
                    continue
                if order in seen_orders:
                    errors.append(
                        f'{level}/{subject}: duplicate order {order} '
                        f'({seen_orders[order]} and {slug})'
                    )
                seen_orders[order] = slug
                for prereq in cfg.get('prereqs') or []:
                    if prereq not in topic_slugs:
                        errors.append(
                            f'{level}/{subject}/{slug}: unknown prereq {prereq!r}'
                        )
                        continue
                    prereq_order = topics[prereq].get('order')
                    if prereq_order is not None and order is not None and prereq_order >= order:
                        errors.append(
                            f'{level}/{subject}/{slug}: prereq {prereq!r} '
                            f'(order {prereq_order}) must come before order {order}'
                        )
    if errors:
        raise AssertionError('\n'.join(errors))