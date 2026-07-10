# Registry and Dropdown Snippets for GCSE Maths Batch 2

This file contains the ready-to-paste updates for adding **Equations and Inequalities**, **Sequences**, and **Transformations** to the existing PythonAnywhere Flask project.

## `topic_registry.py` import update

Add the six new names to the existing GCSE maths import tuple from `generators.gcse.maths`.

```python
from generators.gcse.maths import (
    gcse_maths_algebra,
    gcse_maths_surds,
    gcse_maths_decimals,
    gcse_maths_bidmas,
    gcse_maths_fdp,
    gcse_maths_multiples_factors,
    gcse_vectors,
    gcse_vectors_variants,
    gcse_trigonometry,
    gcse_trigonometry_variants,
    gcse_number,
    gcse_number_variants,
    gcse_ratio_proportion,
    gcse_ratio_proportion_variants,
    gcse_probability,
    gcse_probability_variants,
    gcse_statistics,
    gcse_statistics_variants,
    gcse_geometry_angles,
    gcse_geometry_angles_variants,
    gcse_mensuration,
    gcse_mensuration_variants,
    gcse_graphs,
    gcse_graphs_variants,
    gcse_equations_inequalities,
    gcse_equations_inequalities_variants,
    gcse_sequences,
    gcse_sequences_variants,
    gcse_transformations,
    gcse_transformations_variants,
)
```

If your actual import line is still written on one line, you can instead append this section before the closing parenthesis:

```python
gcse_equations_inequalities, gcse_equations_inequalities_variants, gcse_sequences, gcse_sequences_variants, gcse_transformations, gcse_transformations_variants,
```

## `topic_registry.py` GCSE maths topic entries

Add these entries inside `TOPICS["gcse"]["maths"]`.

```python
"equations_inequalities": {"name": "Equations and Inequalities", "func": gcse_equations_inequalities, "variants_func": gcse_equations_inequalities_variants},
"sequences": {"name": "Sequences", "func": gcse_sequences, "variants_func": gcse_sequences_variants},
"transformations": {"name": "Transformations", "func": gcse_transformations, "variants_func": gcse_transformations_variants},
```

A sensible order for the expanded GCSE maths section is to place **Equations and Inequalities** near Algebra, **Sequences** near Algebra/Graphs, and **Transformations** near Geometry. The order is not technically important, but the following structure keeps the broad topics grouped clearly.

```python
"maths": {
    "number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
    "ratio_proportion": {"name": "Ratio and Proportion", "func": gcse_ratio_proportion, "variants_func": gcse_ratio_proportion_variants},
    "algebra": {"name": "Algebra", "func": gcse_maths_algebra},
    "equations_inequalities": {"name": "Equations and Inequalities", "func": gcse_equations_inequalities, "variants_func": gcse_equations_inequalities_variants},
    "sequences": {"name": "Sequences", "func": gcse_sequences, "variants_func": gcse_sequences_variants},
    "graphs": {"name": "Graphs", "func": gcse_graphs, "variants_func": gcse_graphs_variants},
    "geometry_angles": {"name": "Geometry and Angles", "func": gcse_geometry_angles, "variants_func": gcse_geometry_angles_variants},
    "mensuration": {"name": "Mensuration", "func": gcse_mensuration, "variants_func": gcse_mensuration_variants},
    "transformations": {"name": "Transformations", "func": gcse_transformations, "variants_func": gcse_transformations_variants},
    "probability": {"name": "Probability", "func": gcse_probability, "variants_func": gcse_probability_variants},
    "statistics": {"name": "Statistics", "func": gcse_statistics, "variants_func": gcse_statistics_variants},
    "surds": {"name": "Surds", "func": gcse_maths_surds},
    "decimals": {"name": "Decimals", "func": gcse_maths_decimals},
    "bidmas": {"name": "Order of Operations & Negatives", "func": gcse_maths_bidmas},
    "fdp": {"name": "Fractions, Decimals and Percentages", "func": gcse_maths_fdp},
    "multiples_factors": {"name": "Multiples and Factors", "func": gcse_maths_multiples_factors},
    "vectors": {"name": "Vectors", "func": gcse_vectors, "variants_func": gcse_vectors_variants},
    "trigonometry": {"name": "Trigonometry", "func": gcse_trigonometry, "variants_func": gcse_trigonometry_variants},
},
```

## `templates/index.html` dropdown options

Add these options inside the GCSE Maths topic `<select>` list.

```html
<option value="equations_inequalities" data-subject="maths" data-level="gcse">Equations and Inequalities</option>
<option value="sequences" data-subject="maths" data-level="gcse">Sequences</option>
<option value="transformations" data-subject="maths" data-level="gcse">Transformations</option>
```

## Template file placement

Place the attached lesson files in the `templates/` directory using these exact filenames, because the Flask app builds the lesson template filename from the topic slug.

| Topic slug | Lesson template filename |
|---|---|
| `equations_inequalities` | `gcse_maths_equations_inequalities_lesson.html` |
| `sequences` | `gcse_maths_sequences_lesson.html` |
| `transformations` | `gcse_maths_transformations_lesson.html` |

## Generator file placement

Append the contents of `gcse_batch2_generator_additions.py` to the bottom of:

```text
generators/gcse/maths.py
```

The additions define the following public functions expected by the registry.

| Topic | Main generator | Variant queue function |
|---|---|---|
| Equations and Inequalities | `gcse_equations_inequalities` | `gcse_equations_inequalities_variants` |
| Sequences | `gcse_sequences` | `gcse_sequences_variants` |
| Transformations | `gcse_transformations` | `gcse_transformations_variants` |

## Validation note

The generator file was checked with a small runtime harness. It successfully generated revision-mode problems, named Quick Test variants, and MCQ-mode problems for all three topics.
