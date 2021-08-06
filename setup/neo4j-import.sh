# Assuming this is ran from your $NEO4J_HOME
# First, lets do a quick sanity check to make sure that's true
if grep -qF '/neo4j/' <<< $(pwd); then
    echo "Looks like you're in your \$NEO4J_HOME,\nbut if you are not then please navigate there first.\n"
else
    echo "WARNING: I'm not sure if you're in your \$NEO4J_HOME!\nPlease navigate there first.\n"
fi

# Clear the neo4J database then import the data.
read -p "WARNING: Make sure your neo4j database is clean by running the following commands:
    neo4j stop
    rm -rf \$NEO4J_HOME/data/databases/neo4j/*
    rm -rf \$NEO4J_HOME/data/transactions/neo4j/*
Otherwise, the import will run into problems, as it expects a fresh database.
    (For your safety, we will NOT do this for you!)

Also, make sure you have switched to Java11!

Are you sure you are ready to proceed? (y/n) " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Stop neo4j
    neo4j stop
    echo "Importing data..."
    bin/neo4j-admin import --database=neo4j \
        --nodes=Disease=import/disease_nodes.csv \
        --nodes=Drug=import/drug_nodes.csv \
        --nodes=SideEffect=import/side_effect_nodes.csv \
        --relationships=TREATS=import/drug_disease_edges.csv \
        --nodes=Interaction=import/interaction_nodes.csv \
        --relationships=CAUSES=import/drug_side_effects_edges.csv \
        --relationships=INTERACTS=import/drug_interaction_edges.csv \
        --relationships=CAUSES=import/interaction_side_effects_edges.csv
    echo "Done!"
fi