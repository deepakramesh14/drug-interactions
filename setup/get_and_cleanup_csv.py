import pandas as pd
import pubchempy as pcp
import time
import requests

# Import drug-drug-side_effect csv
print("Importing drug-drug-side_effect CSV...")
drug_interaction_side_effects = pd.read_csv(
    'https://snap.stanford.edu/biodata/datasets/10017/files/ChChSe-Decagon_polypharmacy.csv.gz',
    names=['Drug 1 ID', 'Drug 2 ID', 'Side Effect ID', 'Side Effect Name'], skiprows=1)

# Import drug-side_effect csv
print("Importing drug-side_effect CSV...")
drug_side_effects = pd.read_csv(
    'https://snap.stanford.edu/biodata/datasets/10018/files/ChSe-Decagon_monopharmacy.csv.gz',
    names=['Drug ID', 'Side Effect ID', 'Side Effect Name'], skiprows=1)

# Get all unique PubMed compound IDs from above datasets
all_drug_ids = set([*drug_side_effects['Drug ID'].unique(),
                    *drug_interaction_side_effects['Drug 1 ID'].unique(),
                    *drug_interaction_side_effects['Drug 2 ID'].unique()])

# Initialize empty dictionary to store ID --> name mapping
drug_id_names = {}

# Query PubMed for name of each unique drug/compound ID
counter = 1
for drug_id in all_drug_ids:
    print("Processing drug #", counter, "/", len(all_drug_ids))
    counter += 1

    # To prevent PubMed from timing us out. Apparently this is NOT built into
    # the PubMed RESTful API wrapper...
    time.sleep(0.2)
    try:
        drug_id_names[drug_id] = pcp.Compound.from_cid(drug_id[3:]).synonyms[0]
    # If the synonyms list is empty, then most likely PubMed did not return a
    # valid compound corresponding to our ID. So let's take the easy route and
    # just remove the offending compound ID from our data. We'll still have
    # plenty left to play with...
    except (IndexError):
        drug_interaction_side_effects = drug_interaction_side_effects[(drug_interaction_side_effects['Drug 1 ID']
                                                                       != drug_id) & (drug_interaction_side_effects['Drug 2 ID'] != drug_id)]
        drug_side_effects = drug_side_effects[drug_side_effects['Drug ID'] != drug_id]

# Apply the mapping to each drug column in our data.
print("All drug names fetched successfully! Applying to drug-side_effect and drug-drug-side_effect CSVs...")
drug_interaction_side_effects['Drug 1 Name'] = drug_interaction_side_effects['Drug 1 ID'].apply(
    lambda drug: drug_id_names[drug])
drug_interaction_side_effects['Drug 2 Name'] = drug_interaction_side_effects['Drug 2 ID'].apply(
    lambda drug: drug_id_names[drug])
drug_side_effects['Drug Name'] = drug_side_effects['Drug ID'].apply(
    lambda drug: drug_id_names[drug])

print("Saving both CSVs...")
drug_interaction_side_effects.to_csv(
    'data/drug_interaction_side_effects.csv', index=False)
drug_side_effects.to_csv('data/drug_side_effects.csv', index=False)
print("drug-side_effect and drug-drug-side_effect CSVs saved successfully!")

# Import drug-disease csv
print('Importing drug_disease CSV...')
drug_disease = pd.read_csv(
    'https://snap.stanford.edu/biodata/datasets/10004/files/DCh-Miner_miner-disease-chemical.tsv.gz',
    delimiter='\t', names=['Disease ID', 'Drug ID'], skiprows=1)

all_ncbi_drug_ids = set(drug_disease['Drug ID'])
all_disease_ids = set(drug_disease['Disease ID'])

drug_id_cid_names = {}
counter = 1
for ncbi_drug_id in all_ncbi_drug_ids:
    print("Processing drug #", counter, "/", len(all_ncbi_drug_ids))
    counter += 1
    time.sleep(0.2)
    try:
        # Get appropriate compound based on NCBI ID
        drug_info = pcp.get_compounds(ncbi_drug_id, 'name')[0]
        # Get PubMed compound ID in the same format as previous two datasets
        drug_id_cid_names[ncbi_drug_id] = ("CID" + str(drug_info.cid).zfill(9),
                                           drug_info.synonyms[0])
    except (IndexError):
        drug_disease = drug_disease[drug_disease['Drug ID'] != ncbi_drug_id]

print("All drug names fetched successfully! Applying to drug-disease CSV...")
drug_disease['Drug Name'] = drug_disease['Drug ID'].apply(
    lambda drug: drug_id_cid_names[drug][1])
drug_disease['Drug ID'] = drug_disease['Drug ID'].apply(
    lambda drug: drug_id_cid_names[drug][0])

disease_id_names = {}
counter = 1
for disease_id in all_disease_ids:
    print("Processing disease #", counter, "/", len(all_disease_ids))
    counter += 1
    time.sleep(0.2)
    try:
        disease_id_names[disease_id] = requests.get(
            f"https://id.nlm.nih.gov/mesh/lookup/details?descriptor={disease_id[5:]}&includes=terms").json()['terms'][0]['label']
    except (IndexError):
        drug_disease = drug_disease[drug_disease['Disease ID'] != disease_id]

print("All disease names fetched successfully! Applying to drug-disease CSV...")
drug_disease['Disease Name'] = drug_disease['Disease ID'].apply(
    lambda disease: disease_id_names[disease])

# Save the csv
print("Saving drug-disease CSV...")
drug_disease.to_csv('data/drug_disease.csv', index=False)
print("CSV saved successfully, all done!")
