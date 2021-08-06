# Website instructions:

1. Start your local Neo4J instance `neo4j start`
2. Make sure you install the following dependencies in your preferred environment:
   - Flask (`pip install flask` or `conda install flask`)
   - Neo4J (`pip install neo4j` or `conda install -c conda-forge neo4j`)
   - dotenv (`pip install dotenv` or `conda install dotenv`)
3. Create a new `.env` file in this directory with the following:

   ```json
   USER=<your local Neo4J username>
   PASS=<your local Neo4J password>
   ```

4. Run `python app.py` and navigate to the URL at which the website is running
   (by default, <http://localhost:5000/>)
