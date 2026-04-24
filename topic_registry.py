#topic registry


from generators.gcse.physics_forces import (gcse_physics_forces,)
from generators.gcse.physics import (edexcel_combined_physics_radioactivity,)
from generators.myp.chemistry import (myp_chemistry_redox, myp_chemistry_energy_changes_and_rates,)
from generators.gcse.maths import (gcse_maths_algebra,gcse_maths_surds,gcse_maths_decimals,gcse_maths_bidmas,gcse_maths_fdp,gcse_maths_multiples_factors,)
from generators.alevel.physics import (alevel_physics_magnetism,alevel_physics_photoelectric_variants,alevel_physics_photoelectric,)


#from generators.gcse.cs import (
#    gcse_cs_binary,
#)



TOPICS = {
    "gcse": {
        "maths": {
            "algebra": {"name": "Algebra", "func": gcse_maths_algebra},
            "surds": {"name": "Surds", "func": gcse_maths_surds},
            "decimals": {"name": "Decimals", "func": gcse_maths_decimals},
            "bidmas": {"name": "Order of Operations & Negatives", "func": gcse_maths_bidmas},
            "fdp": {"name": "Fractions, Decimals and Percentages", "func": gcse_maths_fdp},
            "multiples_factors": {"name": "Multiples and Factors", "func": gcse_maths_multiples_factors},
        },
        "physics": {
            "forces": {"name": "Forces", "func": gcse_physics_forces},
            "radioactivity": {"name": "Radioactivity", "func": edexcel_combined_physics_radioactivity},
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
            },
    },
}