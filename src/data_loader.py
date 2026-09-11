"""
Sample data generation and basic data loading utilities.
"""

import random
from datetime import date, timedelta
from src.database import init_db, get_session, Species, Tree

SPECIES_DATA = [
    {"name": "Neem", "scientific_name": "Azadirachta indica", "carbon_rate": 0.28, "max_height": 20,
     "description": "Hardy, medicinal tree widely planted in India."},
    {"name": "Banyan", "scientific_name": "Ficus benghalensis", "carbon_rate": 0.35, "max_height": 25,
     "description": "Iconic large canopy tree with aerial roots."},
    {"name": "Peepal", "scientific_name": "Ficus religiosa", "carbon_rate": 0.32, "max_height": 22,
     "description": "Sacred fig, excellent for air purification."},
    {"name": "Mango", "scientific_name": "Mangifera indica", "carbon_rate": 0.22, "max_height": 18,
     "description": "Fruit tree with good shade value."},
    {"name": "Gulmohar", "scientific_name": "Delonix regia", "carbon_rate": 0.20, "max_height": 15,
     "description": "Flowering ornamental tree."},
    {"name": "Jamun", "scientific_name": "Syzygium cumini", "carbon_rate": 0.25, "max_height": 16,
     "description": "Fruit-bearing evergreen tree."},
    {"name": "Ashoka", "scientific_name": "Saraca asoca", "carbon_rate": 0.18, "max_height": 12,
     "description": "Ornamental and medicinal tree."},
    {"name": "Teak", "scientific_name": "Tectona grandis", "carbon_rate": 0.30, "max_height": 30,
     "description": "High-value timber tree."},
    {"name": "Amaltas", "scientific_name": "Cassia fistula", "carbon_rate": 0.19, "max_height": 14,
     "description": "Golden shower tree, beautiful blooms."},
    {"name": "Arjun", "scientific_name": "Terminalia arjuna", "carbon_rate": 0.27, "max_height": 25,
     "description": "Riverine tree with medicinal bark."},
]

ZONES = ["North Park", "Central Lake", "South Avenue", "East Garden", "West Colony"]


def generate_sample_data(n_trees=800, db_path="database/trees.db"):
    """Generate realistic sample tree inventory."""
    init_db(db_path)
    session = get_session(db_path)

    # Clear previous data
    session.query(Tree).delete()
    session.query(Species).delete()
    session.commit()

    # Insert species
    species_objs = {}
    for s in SPECIES_DATA:
        sp = Species(**s)
        session.add(sp)
        session.flush()
        species_objs[s["name"]] = sp
    session.commit()

    # Generate trees
    for i in range(n_trees):
        sp_name = random.choice(list(species_objs.keys()))
        sp = species_objs[sp_name]

        age_years = random.randint(2, 48)
        planting = date.today() - timedelta(days=age_years * 365 + random.randint(0, 200))

        # DBH roughly correlated with age
        base_dbh = 6 + age_years * random.uniform(1.1, 1.7)
        dbh = round(min(base_dbh + random.uniform(-4, 8), 95), 1)

        height = round(min(sp.max_height * 0.92,
                           dbh * random.uniform(0.28, 0.48)), 1)

        tree = Tree(
            species_id=sp.id,
            common_name=sp_name,
            latitude=round(28.52 + random.uniform(-0.18, 0.18), 5),
            longitude=round(77.12 + random.uniform(-0.22, 0.22), 5),
            planting_date=planting,
            dbh_cm=dbh,
            height_m=height,
            zone=random.choice(ZONES),
            notes="",
            last_inspected=date.today() - timedelta(days=random.randint(30, 400))
        )
        session.add(tree)

    session.commit()
    session.close()
    print(f"✅ Successfully generated {n_trees} sample trees in {db_path}")
