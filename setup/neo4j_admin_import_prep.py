import pandas as pd

# First, import CSVs generate by get_and_cleanup_csvs.py
print("Importing CSVs...")
drug_interaction_side_effects = pd.read_csv(
    'data/drug_interaction_side_effects.csv')

drug_side_effects = pd.read_csv('data/drug_side_effects.csv')

drug_disease = pd.read_csv('data/drug_disease.csv')

# Generate a dictionary of side effect ID --> side effect name
# to use for later CSV generation
side_effect_id_names = dict(zip(
    drug_interaction_side_effects['Side Effect ID'],
    drug_interaction_side_effects['Side Effect Name']))
side_effect_id_names.update(dict(zip(drug_side_effects['Side Effect ID'],
                                     drug_side_effects['Side Effect Name'])))

# Generate IDs of all Interaction nodes. Let's just make it the
# concatenation of the IDs of both drugs that interact together
# to form the interaction.
# (d1:Drug)-[:Interacts]->(i:Interaction)<-[:Interacts]-(d2:Drug)
all_interaction_ids = drug_interaction_side_effects['Drug 1 ID'].str.cat(
    drug_interaction_side_effects['Drug 2 ID'].values)

# Make a CSV of all distinct Disease nodes in drug_disease.csv
# Schema: ID, name, namespace
print("Writing disease nodes...")
disease_nodes = pd.DataFrame(
    {'diseaseID:ID(Disease)': drug_disease['Disease ID'].apply(lambda disease: disease[6:]),
     'name': drug_disease['Disease Name']})
disease_nodes['namespace'] = drug_disease['Disease ID'].apply(
    lambda disease: disease[:6])
disease_nodes.drop_duplicates(inplace=True)
disease_nodes.to_csv('data/disease_nodes.csv', index=False)
print("Done writing disease nodes!")

# Make a CSV of all distinct Drug nodes in all 3 CSVs
# Schema: ID, name, namespace
print("Writing drug nodes...")
drug_nodes = pd.DataFrame(
    {'drugID:ID(Drug)': drug_interaction_side_effects['Drug 1 ID'].apply(lambda drug: drug[3:]), 'name': drug_interaction_side_effects['Drug 1 Name']})
drug_nodes = drug_nodes.append(
    pd.DataFrame(
        {'drugID:ID(Drug)': drug_interaction_side_effects['Drug 2 ID'].apply(lambda drug: drug[3:]), 'name': drug_interaction_side_effects['Drug 2 Name']}),
    ignore_index=True)
drug_nodes = drug_nodes.append(
    pd.DataFrame(
        {'drugID:ID(Drug)': drug_side_effects['Drug ID'].apply(lambda drug: drug[3:]), 'name': drug_side_effects['Drug Name']}),
    ignore_index=True)
drug_nodes = drug_nodes.append(
    pd.DataFrame({'drugID:ID(Drug)': drug_disease['Drug ID'].apply(
        lambda drug: drug[3:]), 'name': drug_disease['Drug Name']}),
    ignore_index=True)
drug_nodes.drop_duplicates(inplace=True)
drug_nodes['namespace'] = 'PubChem'
drug_nodes.to_csv('data/drug_nodes.csv', index=False)
print("Done writing drug nodes!")

# Make a CSV of all distinct SideEffect nodes
# from the dictionary generated earlier
# Schema: ID, name, namespace
print("Writing side effect nodes...")
side_effect_nodes = pd.DataFrame(
    {'sideEffectID:ID(SideEffect)': [s[1:] for s in side_effect_id_names.keys()], 'name': side_effect_id_names.values()})
side_effect_nodes['namespace'] = 'PubChem'
side_effect_nodes.drop_duplicates(inplace=True)
side_effect_nodes.to_csv('data/side_effect_nodes.csv', index=False)
print("Done writing side effect nodes!")

# Make a CSV of all distinct (:Drug)-[:TREATS]->(:Disease) edges
# Schema: Drug ID, Disease ID
print("Writing drug->disease edges...")
drug_disease_edges = pd.DataFrame(
    {':START_ID(Drug)': drug_disease['Drug ID'].apply(lambda drug: drug[3:]),
     ':END_ID(Disease)': drug_disease['Disease ID'].apply(lambda disease: disease[6:])})
drug_disease_edges.to_csv('drug_disease_edges.csv', index=False)
print("Done writing drug->disease edges!")

# Make a CSV of all distinct Interaction nodes
# from the dictionary generated earlier
# Schema: ID, Drug 1 Name, Drug 2 Name
print("Writing interaction nodes...")
interaction_nodes = pd.DataFrame({'interactionID:ID(Interaction)': all_interaction_ids,
                                  'Drug 1 Name': drug_interaction_side_effects['Drug 1 Name'],
                                  'Drug 2 Name': drug_interaction_side_effects['Drug 2 Name']})
interaction_nodes.drop_duplicates(inplace=True)
interaction_nodes.to_csv('data/interaction_nodes.csv', index=False)
print("Done writing interaction nodes!")

# Make a CSV of all distinct (:Drug)-[:CAUSES]->(:SideEffect) edges
# Schema: Drug ID, SideEffect ID
print("Writing drug->side effect edges...")
drug_side_effects_edges = pd.DataFrame(
    {':START_ID(Drug)': drug_side_effects['Drug ID'].apply(lambda drug: drug[3:]),
     ':END_ID(SideEffect)': [s[1:] for s in drug_side_effects['Side Effect ID']]})
drug_side_effects_edges.to_csv('data/drug_side_effects_edges.csv', index=False)
print("Done writing drug->side effect edges!")

# Make a CSV of all distinct (:Drug)-[:INTERACTS]->(:Interaction) edges
# Schema: Drug ID, Interaction ID
print("Writing drug->interaction<-drug edges...")
drug_interaction_edges = pd.DataFrame(
    {':START_ID(Drug)': drug_interaction_side_effects['Drug 1 ID'].apply(lambda drug: drug[3:]),
     ':END_ID(Interaction)': all_interaction_ids})
drug_interaction_edges = drug_interaction_edges.append(
    pd.DataFrame(
        {':START_ID(Drug)': drug_interaction_side_effects['Drug 2 ID'].apply(lambda drug: drug[3:]),
         ':END_ID(Interaction)': all_interaction_ids}),
    ignore_index=True)
drug_interaction_edges.drop_duplicates(inplace=True)
drug_interaction_edges.to_csv('data/drug_interaction_edges.csv', index=False)
print("Done writing drug->interaction<-drug edges!")

# Make a CSV of all distinct (:Interaction)-[:CAUSES]->(:SideEffect) edges
# Schema: Interaction ID, SideEffect ID
print("Writing interaction->side effect edges...")
interaction_side_effects_edges = pd.DataFrame(
    {':START_ID(Interaction)': all_interaction_ids,
     ':END_ID(SideEffect)': [s[1:] for s in drug_interaction_side_effects['Side Effect ID']]})
interaction_side_effects_edges.to_csv(
    'data/interaction_side_effects_edges.csv', index=False)
print("Done writing interaction->side effect edges!")
