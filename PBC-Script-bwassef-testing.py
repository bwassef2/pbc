from abaqus import *
from abaqusConstants import *


mdb = mdb
a = mdb.models['Model-1'].rootAssembly

if 'Part-1-1' not in a.instances.keys():
    raise ValueError("Instance 'Part-1-1' does not exist in the assembly. Please create or verify the instance.")

a.regenerate()  

n = a.instances['Part-1-1'].nodes

if not n:
    raise ValueError("The instance 'Part-1-1' has no nodes. Ensure the part is meshed and the instance is valid.")


groups = {
    "Faces": {
        "ABCD": [], "A-primeB-primeC-primeD-prime": [],
        "AA-primeD-primeD": [], "BB-primeC-primeC": [],
        "DD-primeC-primeC": [], "AA-primeB-primeB": []
    }
}

tol = 1e-6

min_x = min(node.coordinates[0] for node in n)
max_x = max(node.coordinates[0] for node in n)
min_y = min(node.coordinates[1] for node in n)
max_y = max(node.coordinates[1] for node in n)
min_z = min(node.coordinates[2] for node in n)
max_z = max(node.coordinates[2] for node in n)

used_nodes = set()

for node in n:
    node_set_name = "Node_" + str(node.label)
    a.Set(nodes=n.getByBoundingSphere(node.coordinates, 1e-6), name=node_set_name)

    x, y, z = node.coordinates

    if node_set_name not in used_nodes:
        if abs(z - min_z) < tol:
            groups["Faces"]["ABCD"].append(node_set_name)
            used_nodes.add(node_set_name)
        elif abs(z - max_z) < tol:
            groups["Faces"]["A-primeB-primeC-primeD-prime"].append(node_set_name)
            used_nodes.add(node_set_name)
        elif abs(x - min_x) < tol:
            groups["Faces"]["AA-primeD-primeD"].append(node_set_name)
            used_nodes.add(node_set_name)
        elif abs(x - max_x) < tol:
            groups["Faces"]["BB-primeC-primeC"].append(node_set_name)
            used_nodes.add(node_set_name)
        elif abs(y - max_y) < tol:
            groups["Faces"]["DD-primeC-primeC"].append(node_set_name)
            used_nodes.add(node_set_name)
        elif abs(y - min_y) < tol:
            groups["Faces"]["AA-primeB-primeB"].append(node_set_name)
            used_nodes.add(node_set_name)

# Generate reference points outside the cube using DatumPoints and ReferencePoints
p = mdb.models['Model-1'].parts['Part-1']

# Datum points outside the cube
datum1 = p.DatumPointByCoordinate(coords=(max_x + (max_x - min_x) * 0.5, min_y, min_z))
# datum2 = p.DatumPointByCoordinate(coords=(min_x, max_y + (max_y - min_y) * 0.5, min_z))
#datum3 = p.DatumPointByCoordinate(coords=(min_x, min_y, max_z + (max_z - min_z) * 0.5))

# Create reference points from the datums
ref1 = p.ReferencePoint(point=p.datums[datum1.id])
#ref2 = p.ReferencePoint(point=p.datums[datum2.id])
#ref3 = p.ReferencePoint(point=p.datums[datum3.id])

# Assign sets to the reference points
#p.Set(referencePoints=(ref1,), name="RP_X")
#p.Set(referencePoints=(ref2,), name="RP_Y")
#p.Set(referencePoints=(ref3,), name="RP_Z")

# Apply periodic boundary constraints (PBCs)
constraint_id = 1

# Constraints for A'B'C'D' to ABCD
for set1, set2 in zip(groups["Faces"]["A-primeB-primeC-primeD-prime"], groups["Faces"]["ABCD"]):
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 1), (-1.0, set2, 1)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 2), (-1.0, set2, 2)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 3), (-1.0, set2, 3)))
    constraint_id += 1

# Constraints for AA'D'D to BB'C'C
for set1, set2 in zip(groups["Faces"]["AA-primeD-primeD"], groups["Faces"]["BB-primeC-primeC"]):
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 1), (-1.0, set2, 1)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 2), (-1.0, set2, 2)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 3), (-1.0, set2, 3)))
    constraint_id += 1

# Constraints for DD'C'C to AA'B'B
for set1, set2 in zip(groups["Faces"]["DD-primeC-primeC"], groups["Faces"]["AA-primeB-primeB"]):
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 1), (-1.0, set2, 1)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 2), (-1.0, set2, 2)))
    constraint_id += 1
    mdb.models['Model-1'].Equation(name='Constraint-{}'.format(constraint_id), terms=((1.0, set1, 3), (-1.0, set2, 3)))
    constraint_id += 1


