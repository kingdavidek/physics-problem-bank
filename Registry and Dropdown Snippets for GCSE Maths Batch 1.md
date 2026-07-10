# Registry and Dropdown Snippets for GCSE Maths Batch 1

This file contains the ready-to-paste updates for adding **Geometry and Angles**, **Mensuration**, and **Graphs** to the existing PythonAnywhere Flask project.

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
)
```

If your actual import line is still written on one line, you can instead append this section before the closing parenthesis:

```python
gcse_geometry_angles, gcse_geometry_angles_variants, gcse_mensuration, gcse_mensuration_variants, gcse_graphs, gcse_graphs_variants,
```

## `topic_registry.py` GCSE maths topic entries

Add these entries inside `TOPICS["gcse"]["maths"]`.

```python
"geometry_angles": {"name": "Geometry and Angles", "func": gcse_geometry_angles, "variants_func": gcse_geometry_angles_variants},
"mensuration": {"name": "Mensuration", "func": gcse_mensuration, "variants_func": gcse_mensuration_variants},
"graphs": {"name": "Graphs", "func": gcse_graphs, "variants_func": gcse_graphs_variants},
```

A sensible order for the GCSE maths section would place these new topics after **Statistics** and before older single-skill topics, although the order is not technically important.

```python
"maths": {
    "number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
    "ratio_proportion": {"name": "Ratio and Proportion", "func": gcse_ratio_proportion, "variants_func": gcse_ratio_proportion_variants},
    "probability": {"name": "Probability", "func": gcse_probability, "variants_func": gcse_probability_variants},
    "statistics": {"name": "Statistics", "func": gcse_statistics, "variants_func": gcse_statistics_variants},
    "geometry_angles": {"name": "Geometry and Angles", "func": gcse_geometry_angles, "variants_func": gcse_geometry_angles_variants},
    "mensuration": {"name": "Mensuration", "func": gcse_mensuration, "variants_func": gcse_mensuration_variants},
    "graphs": {"name": "Graphs", "func": gcse_graphs, "variants_func": gcse_graphs_variants},
    "algebra": {"name": "Algebra", "func": gcse_maths_algebra},
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
<option value="geometry_angles" data-subject="maths" data-level="gcse">Geometry and Angles</option>
<option value="mensuration" data-subject="maths" data-level="gcse">Mensuration</option>
<option value="graphs" data-subject="maths" data-level="gcse">Graphs</option>
```

## Template file placement

Place the attached lesson files in the `templates/` directory using these exact filenames, because the Flask app builds the lesson template filename from the topic slug.

| Topic slug | Lesson template filename |
|---|---|
| `geometry_angles` | `gcse_maths_geometry_angles_lesson.html` |
| `mensuration` | `gcse_maths_mensuration_lesson.html` |
| `graphs` | `gcse_maths_graphs_lesson.html` |

## Generator file placement

Append the contents of `gcse_batch1_generator_additions.py` to the bottom of:

```text
generators/gcse/maths.py
```

The additions define the following public functions expected by the registry.

| Topic | Main generator | Variant queue function |
|---|---|---|
| Geometry and Angles | `gcse_geometry_angles` | `gcse_geometry_angles_variants` |
| Mensuration | `gcse_mensuration` | `gcse_mensuration_variants` |
| Graphs | `gcse_graphs` | `gcse_graphs_variants` |

## Validation note

The generator file was checked with a small runtime harness. It successfully generated revision-mode problems, named Quick Test variants, and MCQ-mode problems for all three topics.
