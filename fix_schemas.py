import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
import models

db = SessionLocal()
for p in db.query(models.Product).all():
    if p.sku_name is None: p.sku_name = p.name
    if p.generic_specs is None: p.generic_specs = "[]"
    if p.applications is None: p.applications = ""
    if p.packaging is None: p.packaging = ""
    if p.certifications is None: p.certifications = ""
    if p.image is None: p.image = ""
db.commit()
db.close()
print("Fixed schemas")
