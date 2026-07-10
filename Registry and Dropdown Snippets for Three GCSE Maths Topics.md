# Registry and Dropdown Snippets for Three GCSE Maths Topics

This file contains the ready-to-paste updates for adding **Ratio and Proportion**, **Probability**, and **Statistics** to the existing PythonAnywhere Flask project.

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
)
```

If your actual import line is still written on one line, you can instead just append these names before the closing parenthesis:

```python
gcse_ratio_proportion, gcse_ratio_proportion_variants, gcse_probability, gcse_probability_variants, gcse_statistics, gcse_statistics_variants,
```

## `topic_registry.py` GCSE maths topic entries

Add these entries inside `TOPICS["gcse"]["maths"]`.

```python
"ratio_proportion": {"name": "Ratio and Proportion", "func": gcse_ratio_proportion, "variants_func": gcse_ratio_proportion_variants},
"probability": {"name": "Probability", "func": gcse_probability, "variants_func": gcse_probability_variants},
"statistics": {"name": "Statistics", "func": gcse_statistics, "variants_func": gcse_statistics_variants},
```

A suitable GCSE maths section would therefore include the new topics like this:

```python
"maths": {
    "number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
    "ratio_proportion": {"name": "Ratio and Proportion", "func": gcse_ratio_proportion, "variants_func": gcse_ratio_proportion_variants},
    "probability": {"name": "Probability", "func": gcse_probability, "variants_func": gcse_probability_variants},
    "statistics": {"name": "Statistics", "func": gcse_statistics, "variants_func": gcse_statistics_variants},
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

Add these options inside the GCSE Maths topic `<select>` options.

```html
<option value="ratio_proportion" data-subject="maths" data-level="gcse">Ratio and Proportion</option>
<option value="probability" data-subject="maths" data-level="gcse">Probability</option>
<option value="statistics" data-subject="maths" data-level="gcse">Statistics</option>
```

## Template file placement

Place the attached lesson files in the `templates/` directory using these exact filenames, because the Flask app builds the lesson template filename from the topic slug.

| Topic slug | Lesson template filename |
|---|---|
| `ratio_proportion` | `gcse_maths_ratio_proportion_lesson.html` |
| `probability` | `gcse_maths_probability_lesson.html` |
| `statistics` | `gcse_maths_statistics_lesson.html` |

## Generator file placement

Append the contents of `gcse_three_topics_generator_additions.py` to the bottom of:

```text
generators/gcse/maths.py
```

The additions define the following public functions expected by the registry.

| Topic | Main generator | Variant queue function |
|---|---|---|
| Ratio and Proportion | `gcse_ratio_proportion` | `gcse_ratio_proportion_variants` |
| Probability | `gcse_probability` | `gcse_probability_variants` |
| Statistics | `gcse_statistics` | `gcse_statistics_variants` |
