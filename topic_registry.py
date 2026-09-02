#topic registry

import os

from generators.shared.variant_utils import (
    ADVANCED_MODES,
    MCQ_MODE,
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
    STANDARD_MODE,
    normalize_mode,
)
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
from generators.eursc.s1_food import (
    eursc_science_cooking_acid,
    eursc_science_cooking_acid_variants,
    eursc_science_cooking_fermentation,
    eursc_science_cooking_fermentation_variants,
    eursc_science_cooking_heat,
    eursc_science_cooking_heat_variants,
    eursc_science_cooking_salt,
    eursc_science_cooking_salt_variants,
    eursc_science_food_formulas,
    eursc_science_food_formulas_variants,
    eursc_science_healthy_meal_project,
    eursc_science_healthy_meal_project_variants,
    eursc_science_nutrition,
    eursc_science_nutrition_variants,
    eursc_science_water_substances,
    eursc_science_water_substances_variants,
)
from generators.eursc.s1_puberty import (
    eursc_science_pregnancy_sexual_health,
    eursc_science_pregnancy_sexual_health_variants,
    eursc_science_puberty_maturity,
    eursc_science_puberty_maturity_variants,
    eursc_science_reproductive_anatomy,
    eursc_science_reproductive_anatomy_variants,
)
from generators.eursc.s1_science_lab import (
    eursc_science_measurement,
    eursc_science_measurement_variants,
    eursc_science_science_lab,
    eursc_science_science_lab_variants,
    eursc_science_what_is_science,
    eursc_science_what_is_science_variants,
)
from generators.eursc.s1_sports import (
    eursc_science_breathing,
    eursc_science_breathing_variants,
    eursc_science_forces_sport,
    eursc_science_forces_sport_variants,
    eursc_science_movement,
    eursc_science_movement_variants,
    eursc_science_sport_health,
    eursc_science_sport_health_variants,
)
from generators.eursc.s2_universe import (
    eursc_science_atoms_molecules,
    eursc_science_atoms_molecules_variants,
    eursc_science_life_earth_elsewhere,
    eursc_science_life_earth_elsewhere_variants,
    eursc_science_light_telescopes,
    eursc_science_light_telescopes_variants,
    eursc_science_solar_system,
    eursc_science_solar_system_variants,
)
from generators.eursc.s2_health import (
    eursc_science_dependence_addiction,
    eursc_science_dependence_addiction_variants,
    eursc_science_healthy_living,
    eursc_science_healthy_living_variants,
    eursc_science_infectious_disease,
    eursc_science_infectious_disease_variants,
    eursc_science_noninfectious_disease,
    eursc_science_noninfectious_disease_variants,
    eursc_science_tobacco,
    eursc_science_tobacco_variants,
)
from generators.eursc.s2_senses import (
    eursc_science_hearing,
    eursc_science_hearing_variants,
    eursc_science_interoception,
    eursc_science_interoception_variants,
    eursc_science_nonhuman_senses,
    eursc_science_nonhuman_senses_variants,
    eursc_science_proprioception_balance,
    eursc_science_proprioception_balance_variants,
    eursc_science_smell,
    eursc_science_smell_variants,
    eursc_science_taste,
    eursc_science_taste_variants,
    eursc_science_touch,
    eursc_science_touch_variants,
    eursc_science_vision,
    eursc_science_vision_variants,
)
from generators.eursc.s3_machines import (
    eursc_science_electric_current,
    eursc_science_electric_current_variants,
    eursc_science_electrostatics,
    eursc_science_electrostatics_variants,
    eursc_science_energy,
    eursc_science_energy_variants,
    eursc_science_force_work_machines,
    eursc_science_force_work_machines_variants,
    eursc_science_magnetism,
    eursc_science_magnetism_variants,
    eursc_science_robotics_project,
    eursc_science_robotics_project_variants,
)
from generators.eursc.s3_living_earth import (
    eursc_science_classification_biodiversity,
    eursc_science_classification_biodiversity_variants,
    eursc_science_ecology_field_project,
    eursc_science_ecology_field_project_variants,
    eursc_science_ecosystem_characteristics,
    eursc_science_ecosystem_characteristics_variants,
    eursc_science_ecosystems_cycles,
    eursc_science_ecosystems_cycles_variants,
    eursc_science_food_environment,
    eursc_science_food_environment_variants,
)

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
    "eursc": {
        "science": {
            "what_is_science": {
                "name": "What Is Science?",
                "order": 1,
                "year": "s1",
                "unit_code": "1.1",
                "unit_name": "Science Lab",
                "syllabus_ref": "1.1.1",
                "lesson_bank": True,
                "func": eursc_science_what_is_science,
                "variants_func": eursc_science_what_is_science_variants,
            },
            "measurement": {
                "name": "Measurement and SI Units",
                "order": 2,
                "year": "s1",
                "unit_code": "1.1",
                "unit_name": "Science Lab",
                "syllabus_ref": "1.1.2",
                "lesson_bank": True,
                "func": eursc_science_measurement,
                "variants_func": eursc_science_measurement_variants,
            },
            "science_lab": {
                "name": "The Science Laboratory",
                "order": 3,
                "year": "s1",
                "unit_code": "1.1",
                "unit_name": "Science Lab",
                "syllabus_ref": "1.1.3",
                "lesson_bank": True,
                "func": eursc_science_science_lab,
                "variants_func": eursc_science_science_lab_variants,
            },
            "food_formulas": {
                "name": "Food Formulas: Molecules of Life",
                "order": 4,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.1",
                "lesson_bank": True,
                "func": eursc_science_food_formulas,
                "variants_func": eursc_science_food_formulas_variants,
            },
            "water_substances": {
                "name": "Water and Other Substances",
                "order": 5,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.2",
                "lesson_bank": True,
                "func": eursc_science_water_substances,
                "variants_func": eursc_science_water_substances_variants,
            },
            "cooking_heat": {
                "name": "Basic Cooking: Heat",
                "order": 6,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.3",
                "lesson_bank": True,
                "func": eursc_science_cooking_heat,
                "variants_func": eursc_science_cooking_heat_variants,
            },
            "cooking_acid": {
                "name": "Basic Cooking: Acid",
                "order": 7,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.4",
                "lesson_bank": True,
                "func": eursc_science_cooking_acid,
                "variants_func": eursc_science_cooking_acid_variants,
            },
            "cooking_salt": {
                "name": "Basic Cooking: Salt",
                "order": 8,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.5",
                "lesson_bank": True,
                "func": eursc_science_cooking_salt,
                "variants_func": eursc_science_cooking_salt_variants,
            },
            "cooking_fermentation": {
                "name": "Basic Cooking: Fermentation",
                "order": 9,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.6",
                "lesson_bank": True,
                "func": eursc_science_cooking_fermentation,
                "variants_func": eursc_science_cooking_fermentation_variants,
            },
            "nutrition": {
                "name": "Nutrition and Food Information",
                "order": 10,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.7",
                "lesson_bank": True,
                "func": eursc_science_nutrition,
                "variants_func": eursc_science_nutrition_variants,
            },
            "healthy_meal_project": {
                "name": "Project: A Healthy Meal",
                "order": 11,
                "year": "s1",
                "unit_code": "1.2",
                "unit_name": "Food",
                "syllabus_ref": "1.2.8",
                "lesson_bank": True,
                "func": eursc_science_healthy_meal_project,
                "variants_func": eursc_science_healthy_meal_project_variants,
            },
            "movement": {
                "name": "Movement",
                "order": 12,
                "year": "s1",
                "unit_code": "1.3",
                "unit_name": "Sports",
                "syllabus_ref": "1.3.1",
                "lesson_bank": True,
                "func": eursc_science_movement,
                "variants_func": eursc_science_movement_variants,
            },
            "forces_sport": {
                "name": "Forces in Sport",
                "order": 13,
                "year": "s1",
                "unit_code": "1.3",
                "unit_name": "Sports",
                "syllabus_ref": "1.3.2",
                "lesson_bank": True,
                "func": eursc_science_forces_sport,
                "variants_func": eursc_science_forces_sport_variants,
            },
            "breathing": {
                "name": "Breathing, Respiration and Circulation",
                "order": 14,
                "year": "s1",
                "unit_code": "1.3",
                "unit_name": "Sports",
                "syllabus_ref": "1.3.3",
                "lesson_bank": True,
                "func": eursc_science_breathing,
                "variants_func": eursc_science_breathing_variants,
            },
            "sport_health": {
                "name": "Sport and Health",
                "order": 15,
                "year": "s1",
                "unit_code": "1.3",
                "unit_name": "Sports",
                "syllabus_ref": "1.3.4",
                "lesson_bank": True,
                "func": eursc_science_sport_health,
                "variants_func": eursc_science_sport_health_variants,
            },
            "puberty_maturity": {
                "name": "Puberty and Sexual Maturity",
                "order": 16,
                "year": "s1",
                "unit_code": "1.4",
                "unit_name": "Puberty",
                "syllabus_ref": "1.4.1",
                "lesson_bank": True,
                "func": eursc_science_puberty_maturity,
                "variants_func": eursc_science_puberty_maturity_variants,
            },
            "reproductive_anatomy": {
                "name": "Human Reproductive Anatomy",
                "order": 17,
                "year": "s1",
                "unit_code": "1.4",
                "unit_name": "Puberty",
                "syllabus_ref": "1.4.2",
                "lesson_bank": True,
                "func": eursc_science_reproductive_anatomy,
                "variants_func": eursc_science_reproductive_anatomy_variants,
            },
            "pregnancy_sexual_health": {
                "name": "Pregnancy and Sexual Health",
                "order": 18,
                "year": "s1",
                "unit_code": "1.4",
                "unit_name": "Puberty",
                "syllabus_ref": "1.4.3",
                "lesson_bank": True,
                "func": eursc_science_pregnancy_sexual_health,
                "variants_func": eursc_science_pregnancy_sexual_health_variants,
            },
            "solar_system": {
                "name": "The Solar System",
                "order": 19,
                "year": "s2",
                "unit_code": "2.1",
                "unit_name": "Universe",
                "syllabus_ref": "2.1.1",
                "lesson_bank": True,
                "func": eursc_science_solar_system,
                "variants_func": eursc_science_solar_system_variants,
            },
            "light_telescopes": {
                "name": "Light and Telescopes",
                "order": 20,
                "year": "s2",
                "unit_code": "2.1",
                "unit_name": "Universe",
                "syllabus_ref": "2.1.2",
                "lesson_bank": True,
                "func": eursc_science_light_telescopes,
                "variants_func": eursc_science_light_telescopes_variants,
            },
            "life_earth_elsewhere": {
                "name": "Life on Earth and Elsewhere",
                "order": 21,
                "year": "s2",
                "unit_code": "2.1",
                "unit_name": "Universe",
                "syllabus_ref": "2.1.3",
                "lesson_bank": True,
                "func": eursc_science_life_earth_elsewhere,
                "variants_func": eursc_science_life_earth_elsewhere_variants,
            },
            "atoms_molecules": {
                "name": "Atoms and Molecules",
                "order": 22,
                "year": "s2",
                "unit_code": "2.1",
                "unit_name": "Universe",
                "syllabus_ref": "2.1.4",
                "lesson_bank": True,
                "func": eursc_science_atoms_molecules,
                "variants_func": eursc_science_atoms_molecules_variants,
            },
            "healthy_living": {
                "name": "Healthy Living",
                "order": 23,
                "year": "s2",
                "unit_code": "2.2",
                "unit_name": "Health",
                "syllabus_ref": "2.2.1",
                "lesson_bank": True,
                "func": eursc_science_healthy_living,
                "variants_func": eursc_science_healthy_living_variants,
            },
            "infectious_disease": {
                "name": "Infectious Disease and Immunity",
                "order": 24,
                "year": "s2",
                "unit_code": "2.2",
                "unit_name": "Health",
                "syllabus_ref": "2.2.2",
                "lesson_bank": True,
                "func": eursc_science_infectious_disease,
                "variants_func": eursc_science_infectious_disease_variants,
            },
            "noninfectious_disease": {
                "name": "Noninfectious and Environmental Disease",
                "order": 25,
                "year": "s2",
                "unit_code": "2.2",
                "unit_name": "Health",
                "syllabus_ref": "2.2.3",
                "lesson_bank": True,
                "func": eursc_science_noninfectious_disease,
                "variants_func": eursc_science_noninfectious_disease_variants,
            },
            "dependence_addiction": {
                "name": "Pleasure, Dependence and Addiction",
                "order": 26,
                "year": "s2",
                "unit_code": "2.2",
                "unit_name": "Health",
                "syllabus_ref": "2.2.4",
                "lesson_bank": True,
                "func": eursc_science_dependence_addiction,
                "variants_func": eursc_science_dependence_addiction_variants,
            },
            "tobacco": {
                "name": "Tobacco, Nicotine and Vaping",
                "order": 27,
                "year": "s2",
                "unit_code": "2.2",
                "unit_name": "Health",
                "syllabus_ref": "2.2.5",
                "lesson_bank": True,
                "func": eursc_science_tobacco,
                "variants_func": eursc_science_tobacco_variants,
            },
            "vision": {
                "name": "Vision",
                "order": 28,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.1",
                "lesson_bank": True,
                "func": eursc_science_vision,
                "variants_func": eursc_science_vision_variants,
            },
            "hearing": {
                "name": "Hearing",
                "order": 29,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.2",
                "lesson_bank": True,
                "func": eursc_science_hearing,
                "variants_func": eursc_science_hearing_variants,
            },
            "touch": {
                "name": "Touch",
                "order": 30,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.3",
                "lesson_bank": True,
                "func": eursc_science_touch,
                "variants_func": eursc_science_touch_variants,
            },
            "smell": {
                "name": "Smell",
                "order": 31,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.4",
                "lesson_bank": True,
                "func": eursc_science_smell,
                "variants_func": eursc_science_smell_variants,
            },
            "taste": {
                "name": "Taste",
                "order": 32,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.5",
                "lesson_bank": True,
                "func": eursc_science_taste,
                "variants_func": eursc_science_taste_variants,
            },
            "proprioception_balance": {
                "name": "Proprioception and Balance",
                "order": 33,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.6",
                "lesson_bank": True,
                "func": eursc_science_proprioception_balance,
                "variants_func": eursc_science_proprioception_balance_variants,
            },
            "interoception": {
                "name": "Interoception",
                "order": 34,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.7",
                "lesson_bank": True,
                "func": eursc_science_interoception,
                "variants_func": eursc_science_interoception_variants,
            },
            "nonhuman_senses": {
                "name": "Nonhuman Senses",
                "order": 35,
                "year": "s2",
                "unit_code": "2.3",
                "unit_name": "Senses",
                "syllabus_ref": "2.3.8",
                "lesson_bank": True,
                "func": eursc_science_nonhuman_senses,
                "variants_func": eursc_science_nonhuman_senses_variants,
            },
            "force_work_machines": {
                "name": "Force, Work and Simple Machines",
                "order": 36,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.1",
                "lesson_bank": True,
                "func": eursc_science_force_work_machines,
                "variants_func": eursc_science_force_work_machines_variants,
            },
            "energy": {
                "name": "Energy",
                "order": 37,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.2",
                "lesson_bank": True,
                "func": eursc_science_energy,
                "variants_func": eursc_science_energy_variants,
            },
            "electrostatics": {
                "name": "Electrostatics",
                "order": 38,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.3",
                "lesson_bank": True,
                "func": eursc_science_electrostatics,
                "variants_func": eursc_science_electrostatics_variants,
            },
            "electric_current": {
                "name": "Electric Current and Circuits",
                "order": 39,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.4",
                "lesson_bank": True,
                "func": eursc_science_electric_current,
                "variants_func": eursc_science_electric_current_variants,
            },
            "magnetism": {
                "name": "Magnetism and Electromagnetism",
                "order": 40,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.5",
                "lesson_bank": True,
                "func": eursc_science_magnetism,
                "variants_func": eursc_science_magnetism_variants,
            },
            "robotics_project": {
                "name": "Project: Build a Simple Robot",
                "order": 41,
                "year": "s3",
                "unit_code": "3.1",
                "unit_name": "Machines",
                "syllabus_ref": "3.1.6",
                "lesson_bank": True,
                "func": eursc_science_robotics_project,
                "variants_func": eursc_science_robotics_project_variants,
            },
            "food_environment": {
                "name": "Human Nutrition and the Environment",
                "order": 42,
                "year": "s3",
                "unit_code": "3.2",
                "unit_name": "Living Earth",
                "syllabus_ref": "3.2.1",
                "lesson_bank": True,
                "func": eursc_science_food_environment,
                "variants_func": eursc_science_food_environment_variants,
            },
            "ecosystems_cycles": {
                "name": "Ecosystems, Matter and Energy",
                "order": 43,
                "year": "s3",
                "unit_code": "3.2",
                "unit_name": "Living Earth",
                "syllabus_ref": "3.2.2",
                "lesson_bank": True,
                "func": eursc_science_ecosystems_cycles,
                "variants_func": eursc_science_ecosystems_cycles_variants,
            },
            "ecosystem_characteristics": {
                "name": "Ecosystem Characteristics",
                "order": 44,
                "year": "s3",
                "unit_code": "3.2",
                "unit_name": "Living Earth",
                "syllabus_ref": "3.2.3",
                "lesson_bank": True,
                "func": eursc_science_ecosystem_characteristics,
                "variants_func": eursc_science_ecosystem_characteristics_variants,
            },
            "classification_biodiversity": {
                "name": "Classification and Biodiversity",
                "order": 45,
                "year": "s3",
                "unit_code": "3.2",
                "unit_name": "Living Earth",
                "syllabus_ref": "3.2.4",
                "lesson_bank": True,
                "func": eursc_science_classification_biodiversity,
                "variants_func": eursc_science_classification_biodiversity_variants,
            },
            "ecology_field_project": {
                "name": "Project: An Ecological Field Study",
                "order": 46,
                "year": "s3",
                "unit_code": "3.2",
                "unit_name": "Living Earth",
                "syllabus_ref": "3.2.5",
                "lesson_bank": True,
                "func": eursc_science_ecology_field_project,
                "variants_func": eursc_science_ecology_field_project_variants,
            },
        },
    },
}

_VALID_YEARS = frozenset({"s1", "s2", "s3"})

# Optional product-level overrides live in one place. EURSC advanced capability
# is otherwise derived from bind_eursc_topic's dedicated advanced pools.
TOPIC_MODE_CAPABILITY_OVERRIDES = {}


def topic_mode_capabilities(level, subject, topic):
    """Return public Practice modes supported by one registered topic."""
    try:
        cfg = TOPICS[level][subject][topic]
    except KeyError:
        return (STANDARD_MODE,)

    override = TOPIC_MODE_CAPABILITY_OVERRIDES.get((level, subject, topic))
    if override is not None:
        modes = {normalize_mode(mode) for mode in override}
    elif level == "eursc" and subject == "science":
        declared = getattr(cfg.get("variants_func"), "_supported_modes", ())
        modes = {STANDARD_MODE, *(mode for mode in declared if mode in ADVANCED_MODES)}
    else:
        modes = {STANDARD_MODE, MCQ_MODE}

    order = (
        STANDARD_MODE,
        MCQ_MODE,
        MULTI_STEP_MODE,
        SITUATIONAL_MULTI_STEP_MODE,
    )
    return tuple(mode for mode in order if mode in modes)


def topic_supports_mode(level, subject, topic, mode):
    """Whether a normalized public mode is available for a topic."""
    return normalize_mode(mode) in topic_mode_capabilities(level, subject, topic)


if os.environ.get("PB_TESTING") == "1":
    from generators.eursc.science_es0_fixture import (
        eursc_science_es0_fixture,
        eursc_science_es0_fixture_variants,
    )

    TOPICS["eursc"]["science"]["es0_fixture"] = {
        "name": "ES0 Mixed Quiz Fixture",
        "order": 99,
        "year": "s1",
        "unit_code": "1.1",
        "unit_name": "Science Lab",
        "syllabus_ref": "es0",
        "lesson_bank": True,
        "func": eursc_science_es0_fixture,
        "variants_func": eursc_science_es0_fixture_variants,
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
                year = cfg.get('year')
                if year is not None and year not in _VALID_YEARS:
                    errors.append(
                        f'{level}/{subject}/{slug}: invalid year {year!r} '
                        f'(expected one of {sorted(_VALID_YEARS)})'
                    )
                unit_code = cfg.get('unit_code')
                unit_name = cfg.get('unit_name')
                if (unit_code and not unit_name) or (unit_name and not unit_code):
                    errors.append(
                        f'{level}/{subject}/{slug}: unit_code and unit_name must be set together'
                    )
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