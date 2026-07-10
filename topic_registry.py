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
            "algebra": {"name": "Algebra", "func": gcse_maths_algebra, "variants_func": gcse_maths_algebra_variants},
            "algebraic_fractions": {
                "name": "Algebraic Fractions",
                "func": gcse_algebraic_fractions,
                "variants_func": gcse_algebraic_fractions_variants,
            },
            "algebraic_proof": {
                "name": "Algebraic Proof",
                "func": gcse_algebraic_proof,
                "variants_func": gcse_algebraic_proof_variants,
            },
            "simultaneous_equations": {
                "name": "Simultaneous Equations",
                "func": gcse_simultaneous_equations,
                "variants_func": gcse_simultaneous_equations_variants,
            },
            "completing_the_square": {
                "name": "Completing the Square",
                "func": gcse_completing_the_square,
                "variants_func": gcse_completing_the_square_variants,
            },
            "quadratic_simultaneous_equations": {
                "name": "Quadratic Simultaneous Equations",
                "func": gcse_quadratic_simultaneous_equations,
                "variants_func": gcse_quadratic_simultaneous_equations_variants,
            },
            "graphical_simultaneous_equations": {
                "name": "Graphical Simultaneous Equations",
                "func": gcse_graphical_simultaneous_equations,
                "variants_func": gcse_graphical_simultaneous_equations_variants,
            },
            "surds": {"name": "Surds", "func": gcse_maths_surds, "variants_func": gcse_maths_surds_variants},
            "decimals": {"name": "Decimals", "func": gcse_maths_decimals, "variants_func": gcse_maths_decimals_variants},
            "bidmas": {"name": "Order of Operations & Negatives", "func": gcse_maths_bidmas, "variants_func": gcse_maths_bidmas_variants},
            "fdp": {"name": "Fractions, Decimals and Percentages", "func": gcse_maths_fdp, "variants_func": gcse_maths_fdp_variants},
            "multiples_factors": {"name": "Multiples and Factors", "func": gcse_maths_multiples_factors, "variants_func": gcse_maths_multiples_factors_variants},
            "vectors": {"name": "Vectors", "func": gcse_vectors, "variants_func": gcse_vectors_variants},
            "trigonometry": {"name": "Trigonometry", "func": gcse_trigonometry, "variants_func": gcse_trigonometry_variants},
            "number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
            "ratio_proportion": {"name": "Ratio and Proportion", "func": gcse_ratio_proportion, "variants_func": gcse_ratio_proportion_variants},
            "probability": {"name": "Probability", "func": gcse_probability, "variants_func": gcse_probability_variants},
            "statistics": {"name": "Statistics", "func": gcse_statistics, "variants_func": gcse_statistics_variants},
            "graphs": {"name": "Graphs", "func": gcse_graphs, "variants_func": gcse_graphs_variants},
            "functions": {
                "name": "Functions",
                "func": gcse_functions,
                "variants_func": gcse_functions_variants,
            },
            "equations_inequalities": {"name": "Equations and Inequalities", "func": gcse_equations_inequalities, "variants_func": gcse_equations_inequalities_variants},
            "changing_the_subject": {
                "name": "Changing the Subject",
                "func": gcse_changing_the_subject,
                "variants_func": gcse_changing_the_subject_variants,
            },
            "sequences": {"name": "Sequences", "func": gcse_sequences, "variants_func": gcse_sequences_variants},
            "geometry_angles": {"name": "Geometry and Angles", "func": gcse_geometry_angles, "variants_func": gcse_geometry_angles_variants},
            "transformations": {"name": "Transformations", "func": gcse_transformations, "variants_func": gcse_transformations_variants},
            "mensuration": {"name": "Mensuration", "func": gcse_mensuration, "variants_func": gcse_mensuration_variants},
            "bearings": {"name": "Bearings", "func": gcse_bearings, "variants_func": gcse_bearings_variants},
            "circle_theorems": {"name": "Circle Theorems", "func": gcse_circle_theorems, "variants_func": gcse_circle_theorems_variants},
            "compound_measures": {"name": "Compound Measures", "func": gcse_compound_measures, "variants_func": gcse_compound_measures_variants},
            "similarity_congruence": {"name": "Similarity and Congruence", "func": gcse_similarity_congruence, "variants_func": gcse_similarity_congruence_variants},
            "constructions_loci": {"name": "Constructions and Loci", "func": gcse_constructions_loci, "variants_func": gcse_constructions_loci_variants},
            "pythagoras": {"name": "Pythagoras' Theorem", "func": gcse_pythagoras, "variants_func": gcse_pythagoras_variants},
        },
        "physics": {
            "forces": {"name": "Forces", "func": gcse_physics_forces},
            "radioactivity": {"name": "Radioactivity", "func": edexcel_combined_physics_radioactivity},
        },
        "cs": {
            "python_programming": {"name": "Python Programming", "func": gcse_python_programming},
            "algorithms": {
                "name": "Fundamentals of Algorithms",
                "func": gcse_algorithms,
                "variants_func": gcse_algorithms_variants,
            },
            "data_rep": {
                "name": "Fundamentals of Data Representation",
                "func": gcse_data_rep,
                "variants_func": gcse_data_rep_variants,
            },
            "computer_systems": {
                "name": "Computer Systems",
                "func": gcse_computer_systems,
                "variants_func": gcse_computer_systems_variants,
            },
            "computer_networks": {
                "name": "Computer Networks",
                "func": gcse_computer_networks,
                "variants_func": gcse_computer_networks_variants,
            },
            "cyber_security": {
                "name": "Cyber Security",
                "func": gcse_cyber_security,
                "variants_func": gcse_cyber_security_variants,
            },
            "db_sql": {
                "name": "Relational Databases & SQL",
                "func": gcse_db_sql,
                "variants_func": gcse_db_sql_variants,
            },
            "ethical": {
                "name": "Ethical, Legal & Environmental Impacts",
                "func": gcse_ethical,
                "variants_func": gcse_ethical_variants,
            },
            "systems_software": {
                "name": "Systems Software",
                "func": gcse_systems_software,
                "variants_func": gcse_systems_software_variants,
            },
        },
    },
    "myp": {
        "chemistry": {
            "redox": {"name": "Redox Reactions", "func": myp_chemistry_redox},
            "energy_changes_and_rates": {
                "name": "Energy Changes and Rates of Reaction",
                "func": myp_chemistry_energy_changes_and_rates,
            },
        },
    },
    "alevel": {
        "physics": {
            "magnetism": {"name": "Magnetic Fields", "func": alevel_physics_magnetism},
            "photoelectric": {"name": "Photoelectric Effect and Wave-Particle Duality", "func": alevel_physics_photoelectric, "variants_func": alevel_physics_photoelectric_variants,},
            "particles": {"name": "Particle Physics & the Standard Model","func": alevel_physics_particles,"variants_func": alevel_physics_particles_variants,},
            },
    },
}