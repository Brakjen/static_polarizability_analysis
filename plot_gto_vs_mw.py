from pprint import pprint
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import operator
import yaml
import math

import functions

# Get data structures
with open("hg_data.yaml") as f, open("mw_data_0001v2.yaml") as g, open("datafiles_orca_response_v2.yaml") as h:
    data1 = yaml.load(f)
    data2 = yaml.load(g)
    data3 = yaml.load(h)

# Only use molecules common in both data sets
spin_filter = False
re_filter = False
skip = []
molecules = functions.incommon(data1.keys(), data2.keys(), data3.keys())

# Filter based on the spin information
if spin_filter:
    molecules = filter(lambda mol: data1[mol]["multiplicity"] > 0, molecules)

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_mw_gto = [100 * (data1[mol]["pbe"]["mean"] / data2[mol]["pbe"]["mean"] - 1) for mol in molecules]

# Sort data based on the PBE relative error results
molecules_sorted, rel_err_mw_gto_sorted = zip(*sorted(zip(molecules, rel_err_mw_gto), reverse=True, key=operator.itemgetter(1)))

# Filter based on the magnitude of relative error
molecules_subset = []
rel_err_mw_gto_subset = []
if re_filter:
    for i, RE in enumerate(rel_err_mw_gto_sorted):
        if RE > 1 or RE < 0:
            rel_err_mw_gto_subset.append(RE)
            molecules_subset.append(molecules_sorted[i])
    molecules_sorted = molecules_subset
    rel_err_mw_gto_sorted = rel_err_mw_gto_subset
    xticks = range(len(molecules_sorted))

print("Number of species: ", len(molecules))
print("Mean relative error (MRE): ", sum(rel_err_mw_gto) / len(rel_err_mw_gto))
print("RMSRE: ", math.sqrt(sum(map(lambda x: x**2, rel_err_mw_gto)) / len(molecules)))

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if data2[mol]["multiplicity"] == 1 else "crimson" for mol in molecules_sorted]

# Set up the figure with subplots
fontsize = 20
width=0.7

# Define custom lines that we will use for making a custom legend
# that explains the red and blue colors
lines = [Line2D([0], [0], color="deepskyblue"),
         Line2D([0], [0], color="crimson")]

fig = plt.figure(figsize=(15, 5), dpi=100)
ax = plt.gca()

ax.set_ylabel("Relative Error [%]", fontsize=fontsize)
ax.set_yticks(range(9))
ax.tick_params("y", labelsize=fontsize)
ax.set_xlim(-1, len(molecules_sorted))
ax.set_xticklabels([])

# Plot data
for i in range(len(molecules_sorted)):
    ax.bar(xticks[i], rel_err_mw_gto_sorted[i], color=spin_colors[i], edgecolor="black", width=width, linewidth=1.65)

ax.plot(range(len(molecules_sorted)), [0.5 for i in range(len(molecules_sorted))], color="black", linestyle="--")
ax.plot(range(len(molecules_sorted)), [-0.5 for i in range(len(molecules_sorted))], color="black", linestyle="--")

ax.grid(True, linestyle="--", linewidth=0.3)

# Place the molecule names on the xtick positions, rotation by 90 degrees
#plt.xticks(xticks, [mol.upper() for mol in molecules_sorted], rotation=70, fontsize=10)


plt.legend(lines, ["Closed-shell", "Open-shell"], fontsize=fontsize)
fig.tight_layout()
plt.savefig("fig_{}.png".format(__file__.split(".")[0]), dpi=100)
plt.show()
