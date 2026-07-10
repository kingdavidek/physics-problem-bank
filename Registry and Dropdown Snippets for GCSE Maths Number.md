# Registry and Dropdown Snippets for GCSE Maths Number

## `topic_registry.py` import update

Replace the existing GCSE maths import line with this version, or add `gcse_number` and `gcse_number_variants` to the existing tuple.

```python
from generators.gcse.maths import (gcse_maths_algebra,gcse_maths_surds,gcse_maths_decimals,gcse_maths_bidmas,gcse_maths_fdp,gcse_maths_multiples_factors,gcse_vectors,gcse_vectors_variants,gcse_trigonometry,gcse_trigonometry_variants,gcse_number,gcse_number_variants,)
```

## `topic_registry.py` GCSE maths topic entry

Add this inside `TOPICS["gcse"]["maths"]`, preferably before Algebra or after Multiples and Factors.

```python
"number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
```

A suitable GCSE maths block would therefore include:

```python
"maths": {
    "number": {"name": "Number", "func": gcse_number, "variants_func": gcse_number_variants},
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

## `templates/index.html` dropdown option

Add this inside the GCSE Maths topic `<select>` options, alongside the other GCSE Maths options.

```html
<option value="number" data-subject="maths" data-level="gcse">Number</option>
```
