import utils.embedding as embedding

property_graph_definition = """CREATE PROPERTY GRAPH drug_graph
  VERTEX TABLES (
    Drug, Disorder, MOA
  )
EDGE TABLES (
  DrugDisorder 	SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
                DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
  LABEL MAY_TREAT,
  DrugMOA SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
          DESTINATION KEY (moa_id) REFERENCES MOA (moa_id)
  LABEL HAS_MOA
);"""


initialization_commands = ["LOAD duckpgq;", "LOAD fts;", "LOAD vss;", property_graph_definition]

sql_examples =  [
        {   "input": "How many drugs are there", 
            "query": 'SELECT COUNT("drug_cui") AS "drug_count" FROM "Drug"',
        },
        {   
            "input": "What is the MOA of abiraterone", 
            "query": """SELECT MOA.name 
                        FROM DrugMOA, Drug, MOA
                        WHERE DrugMOA.drug_cui = Drug.drug_cui
                        AND DrugMOA.moa_id = MOA.moa_id
                        AND LOWER(Drug.name) = LOWER('abiraterone');""",
        },
        {   
            "input": "What diseases can fluocinolone acetonide treat?", 
            "query": """SELECT Disorder.name 
                        FROM DrugDisorder, Drug, Disorder
                        WHERE DrugDisorder.drug_cui = Drug.drug_cui
                        AND DrugDisorder.disorder_cui = Disorder.disorder_cui
                        AND LOWER(Drug.name) = LOWER('fluocinolone acetonide');""",
        },
        {
            "input": "Show 5 trials and their drugs. At least one of the drugs must be used to treat against the Non-small cell lung carcinoma?",
            "query": """SELECT Trials.StudyTitle as StudyTitle, drug_for_disease.drug_name
                FROM Trials,
                GRAPH_TABLE(
                    drug_graph
                    MATCH
                    (i:Drug)-[m:MAY_TREAT]->(c:Disorder WHERE LOWER(c.name) = LOWER('Non-small cell lung carcinoma'))
                    COLUMNS (i.drug_cui AS drug_cui, i.name AS drug_name)
                )  drug_for_disease
                WHERE list_contains(Trials.drug_cui, drug_for_disease.drug_cui)
                LIMIT 5;""",
        },
        {
            "input": "Count all the trials with 'Fluticasone propionate' by sponsor and then by phase?",
            "query": """SELECT Sponsor, Phase, COUNT(PostingID) AS trial_count
                FROM Trials, Drug
                WHERE LOWER(Drug.name) = LOWER('Fluticasone propionate') AND list_contains(Trials.drug_cui, Drug.drug_cui)
                GROUP BY Sponsor, Phase
                ORDER BY Sponsor, Phase;""",
        },
    ]

sql_database_prompt = """
      The Drug table contains information about drugs. Each row represents a drug and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - name: The name of the drug.

      The Disorder table contains information about disorders. Each row represents a disorder and has the following columns:
      - disorder_cui: The unique UMLS identifier for the disorder.
      - name: The name of the disorder.
      - definition: The definition of the disorder provided by UMLS.
      - definitionEmbedding: The 1536 vector embedding of the definition of the disorder.

      The MOA table contains information about the mechanism of action of drugs. Each row represents a mechanism of action and has the following columns:
      - moa_id: The unique UMLS identifier for the mechanism of action.
      - name: The name of the mechanism of action.

      The DrugMOA table contains information about the relationship between drugs and their mechanisms of action. Each row represents that a drug has the mechanism of action and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - moa_id: The unique UMLS identifier for the mechanism of action.

      The DrugDisorder table contains information about the relationship between drugs and disorders. Each row represents that a drug may be used to treat a disorder and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - disorder_cui: The unique UMLS identifier for the disorder.

      The Trials table contains information about 2000+ clinical trials. Each row represents that a trial.  
      - PostingID: The unique id for the trial.
      - Sponsor: The sponsor behind the trial.
      - StudyTitle: The title of the trial. I have created a full-text search index on this column. For example, you can use the match_bm25 function to search for relevant trials whose StudyTitle contain "double blind & Valaciclovir".
      SELECT PostingID as trial_id, StudyTitle, score
        FROM (
            SELECT *, fts_main_Trials.match_bm25(
                PostingID,
                'double blind & Valaciclovir',
                fields := 'StudyTitle'
            ) AS score
            FROM Trials
        )
        WHERE score IS NOT NULL
        ORDER BY score DESC LIMIT 5;
      - Disorder: The disorder that the trial focuses on.
      - Phase: The phase of the trial.
      - LinkToSponsorStudyRegistry: The link to the sponsor's study registry.
      - LinkToClinicalTrials: The link to the clinicaltrials.gov website.
      - drug_cui: This column contains the drug_cui for the "Drug" that the trial tested. Use this column to join with the "Drug" table.
      - drug_names: This column contains the drug names for the "cui" that the trial focuses on.
      """

graph_examples = [
        {   
            "input": "What is the MOA of Nicotinamide? Use the graph query.", 
            "query": """FROM GRAPH_TABLE (drug_graph
                        MATCH
                        (d:Drug WHERE LOWER(d.name) = LOWER('Nicotinamide'))-[h:HAS_MOA]->(m:MOA)
                        COLUMNS (m.name AS moa_name)
                        )
                        LIMIT 20;"""
        },
        {
            "input": "Which drugs can be used to treat Alzheimer's Disease? Only give me all results without limit.",
            "query": """FROM GRAPH_TABLE (drug_graph
                    MATCH
                    (i:Drug)-[m:MAY_TREAT]->(c:Disorder WHERE LOWER(c.name) = LOWER('Alzheimer''s Disease'))
                    COLUMNS (i.name AS drug_name)
                    );""",
        },
        {
            "input": "What is the mechanism of action of drugs that can treat Alzheimer's Disease? Give me 5 drugs and their MOA.",
            "query": """FROM GRAPH_TABLE (drug_graph
                    MATCH
                    (mo:MOA)<-[h:HAS_MOA]-(i:Drug)-[m:MAY_TREAT]->(c:Disorder WHERE LOWER(c.name) = LOWER('Alzheimer''s Disease'))
                    COLUMNS (i.name AS drug_name, mo.name AS moa_name)
                    )
                    LIMIT 5;"""
        },
        {
            "input": "What is kind of disorders can a drug with the MOA of 'GABA B receptor interactions' treat? Give me 3 drugs and their targeting disorders.",
            "query": """FROM GRAPH_TABLE (drug_graph
                    MATCH
                    (mo:MOA WHERE LOWER(mo.name) = LOWER('GABA B receptor interactions'))<-[h:HAS_MOA]-(i:Drug)-[m:MAY_TREAT]->(c:Disorder)
                    COLUMNS (i.name AS drug_name, c.name AS disorder_name)
                    )
                    LIMIT 3;"""
        },
        {
            "input": "What diseases can etoposide treat? Only give me all results without limit.",
            "query": """FROM GRAPH_TABLE (drug_graph  
                    MATCH  
                    (i:Drug WHERE LOWER(i.name) = LOWER('etoposide'))-[m:MAY_TREAT]->(c:Disorder)  
                    COLUMNS (c.name AS disorder_name)  
                    );""",
        },
    ]

graph_database_prompt = """
      The Drug table contains information about drugs. Each row represents a drug and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - name: The name of the drug.

      The Disorder table contains information about disorders. Each row represents a disorder and has the following columns:
      - disorder_cui: The unique UMLS identifier for the disorder.
      - name: The name of the disorder.
      - definition: The definition of the disorder provided by UMLS.
      - definitionEmbedding: The 1536 vector embedding of the definition of the disorder.

      The MOA table contains information about the mechanism of action of drugs. Each row represents a mechanism of action and has the following columns:
      - moa_id: The unique UMLS identifier for the mechanism of action.
      - name: The name of the mechanism of action.

      The DrugMOA table contains information about the relationship between drugs and their mechanisms of action. Each row represents that a drug has the mechanism of action and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - moa_id: The unique UMLS identifier for the mechanism of action.

      The DrugDisorder table contains information about the relationship between drugs and disorders. Each row represents that a drug may be used to treat a disorder and has the following columns:
      - drug_cui: The unique UMLS identifier for the drug.
      - disorder_cui: The unique UMLS identifier for the disorder.

      There is a PROPERTY GRAPH called "drug_graph". This graph is defined as follows:
        VERTEX TABLES (
            Drug, Disorder, MOA
        )
        EDGE TABLES (
        DrugDisorder 	SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
                        DESTINATION KEY (disorder_cui) REFERENCES Disorder (disorder_cui)
        LABEL MAY_TREAT,
        DrugMOA SOURCE KEY (drug_cui) REFERENCES Drug (drug_cui)
                DESTINATION KEY (moa_id) REFERENCES MOA (moa_id)
        LABEL HAS_MOA
        );
      """

full_text_search_examples = [
        {   "input": """Search 3 trials with these words in their titles "double blind & Valaciclovir".""", 
            "query": """SELECT PostingID as trial_id, StudyTitle, score
                        FROM (
                            SELECT *, fts_main_Trials.match_bm25(
                                PostingID,
                                'double blind & Valaciclovir',
                                fields := 'StudyTitle'
                            ) AS score
                            FROM Trials
                        )
                        WHERE score IS NOT NULL
                        ORDER BY score DESC LIMIT 3;"""
        },
    ]

full_text_search_query_template = """SELECT PostingID as trial_id, StudyTitle, score
    FROM (
        SELECT *, fts_main_Trials.match_bm25(
            PostingID,
            '{original_query}',
            fields := '{field}'
        ) AS score
        FROM Trials
    )
    WHERE score IS NOT NULL
    ORDER BY score DESC LIMIT {limit};"""



vector_search_query_template = """SELECT name, definition
        FROM Disorder
        ORDER BY array_distance(definitionEmbedding, {question_embedding}::FLOAT[1536])
        LIMIT {limit};"""



vector_search_examples = [
        {   "input": "Show 3 joint-related disorder?", 
            "query": vector_search_query_template.format(question_embedding=embedding.get_embedding("joint-related disorder"), limit=3)
        },
        {
            "input": "Show 3 trials that tested drugs against the top 10 joint-related disorders",
            "query": """SELECT Trials.PostingID AS trial_id, Trials.StudyTitle AS StudyTitle, target_disease.name, drug_for_disorder.drug_name 
                        FROM 
                        Trials, 

                        (
                        SELECT disorder_cui, name
                            FROM Disorder
                            ORDER BY array_distance(definitionEmbedding, {question_embedding}::FLOAT[1536])
                            LIMIT 10
                        ) target_disease,

                        GRAPH_TABLE(
                            drug_graph
                            MATCH (i:Drug)-[m:MAY_TREAT]->(c:Disorder)
                            COLUMNS (i.drug_cui AS drug_cui, i.name AS drug_name,c.disorder_cui AS disorder_cui)
                            )  drug_for_disorder

                        WHERE target_disease.disorder_cui = drug_for_disorder.disorder_cui 
                        AND list_contains(Trials.drug_cui, drug_for_disorder.drug_cui) LIMIT {limit}""".format(question_embedding=embedding.get_embedding("joint-related disorder"), limit = 3),
        },
    ]