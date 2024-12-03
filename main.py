from dotenv import load_dotenv
import os
import gradio as gr
import psycopg2
import openai
import pandas as pd

load_dotenv()

openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

print(openai.api_key)

# Configuration PostgreSQL
DATABASE = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}


# Prompt générique pour le modèle
generic_prompt = """Le schéma est public, et les tables sont :
"Artist", "Album", "Employee", "Customer", "Invoice", "InvoiceLine", "Track", "Playlist", "PlaylistTrack", "Genre", "MediaType".

Pour avoir une meilleure idée des tables, voici le schéma :
Modèle de base de données :
    table_name   |    column_name    |          data_type
    ---------------+-------------------+-----------------------------
    Album         | "AlbumId"         | integer
    Album         | "Title"           | character varying
    Album         | "ArtistId"        | integer
    Artist        | "ArtistId"        | integer
    Artist        | "Name"            | character varying
    Customer      | "CustomerId"      | integer
    Customer      | "FirstName"       | character varying
    Customer      | "LastName"        | character varying
    Customer      | "Company"         | character varying
    Customer      | "Address"         | character varying
    Customer      | "City"            | character varying
    Customer      | "State"           | character varying
    Customer      | "Country"         | character varying
    Customer      | "PostalCode"      | character varying
    Customer      | "Phone"           | character varying
    Customer      | "Fax"             | character varying
    Customer      | "Email"           | character varying
    Customer      | "SupportRepId"    | integer
    Employee      | "EmployeeId"      | integer
    Employee      | "LastName"        | character varying
    Employee      | "FirstName"       | character varying
    Employee      | "Title"           | character varying
    Employee      | "ReportsTo"       | integer
    Employee      | "BirthDate"       | timestamp without time zone
    Employee      | "HireDate"        | timestamp without time zone
    Employee      | "Address"         | character varying
    Employee      | "City"            | character varying
    Employee      | "State"           | character varying
    Employee      | "Country"         | character varying
    Employee      | "PostalCode"      | character varying
    Employee      | "Phone"           | character varying
    Employee      | "Fax"             | character varying
    Employee      | "Email"           | character varying
    Genre         | "GenreId"         | integer
    Genre         | "Name"            | character varying
    Invoice       | "InvoiceId"       | integer
    Invoice       | "CustomerId"      | integer
    Invoice       | "InvoiceDate"     | timestamp without time zone
    Invoice       | "BillingAddress"  | character varying
    Invoice       | "BillingCity"     | character varying
    Invoice       | "BillingState"    | character varying
    Invoice       | "BillingCountry"  | character varying
    Invoice       | "BillingPostalCode"| character varying
    Invoice       | "Total"           | numeric
    InvoiceLine   | "InvoiceLineId"   | integer
    InvoiceLine   | "InvoiceId"       | integer
    InvoiceLine   | "TrackId"         | integer
    InvoiceLine   | "UnitPrice"       | numeric
    InvoiceLine   | "Quantity"        | integer
    MediaType     | "MediaTypeId"     | integer
    MediaType     | "Name"            | character varying
    Playlist      | "PlaylistId"      | integer
    Playlist      | "Name"            | character varying
    PlaylistTrack | "PlaylistId"      | integer
    PlaylistTrack | "TrackId"         | integer
    Track         | "TrackId"         | integer
    Track         | "Name"            | character varying
    Track         | "AlbumId"         | integer
    Track         | "MediaTypeId"     | integer
    Track         | "GenreId"         | integer
    Track         | "Composer"        | character varying
    Track         | "Milliseconds"    | integer
    Track         | "Bytes"           | integer
    Track         | "UnitPrice"       | numeric"
"""

def connect_to_postgres():
    """Établit une connexion à la base PostgreSQL."""
    try:
        conn = psycopg2.connect(**DATABASE)
        return conn
    except psycopg2.Error as e:
        return f"Erreur de connexion PostgreSQL : {e}"

def generate_question_based_on_db_modele():
    """Génère des questions basées sur le schéma de la base de données."""
    prompt = f"""
    Vous êtes un expert SQL et en language humain, spécialisé dans la génération de questions pertinentes pour explorer une base de données. Posez des questions en langage naturel sur les données de la base de données fournie.

    {generic_prompt}

    Directives :  
    - Formulez des questions en français, claires et concises, pour explorer les données de la base de données.
    - Utilisez un langage naturel et accessible, sans jargon technique.
    - Posez des questions variées pour couvrir différents aspects des données, comme un analyste curieux et perspicace le ferait.
    - Une fois sur 5, posez une question bizarre qui n'as pas de rapport avec la base de données.

    NB : J'ai besoin de 25 questions sous forme de tableau pour pouvoir générer un dataset.
    NB : Retourne moi seulement le tableau avec 25 questions et rien d'autre.
    NB : Ne me mens pas

    exemple de output : ["Quels sont les artistes ayant vendu le plus de titres ?", "Quels sont les clients ayant effectué le plus d'achats ?", "Quel est le genre musical le plus populaire ?", "Quel est le titre le plus long ?", "Quel est le titre le plus court ?"]

    """

    try:
        # Appel à l'API OpenAI
        response = openai.ChatCompletion.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant SQL expert et en language humain."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )

        # Extraction de la réponse
        questions = response.choices[0].message.content.strip().split('\n')
        return questions

    except Exception as e:
        # Gestion des erreurs
        return f"Une erreur est survenue : {e}"

def process_question_to_sql(requete):
    prompt = f"""
    Vous êtes un assistant SQL expert. Répondez uniquement avec la requête SQL en syntaxe PostgreSQL, en veillant à ce que tous les noms de tables et de colonnes soient entre guillemets doubles et sensibles à la casse.
    Le schéma est public, et les tables sont :
    "Artist", "Album", "Employee", "Customer", "Invoice", "InvoiceLine", "Track", "Playlist", "PlaylistTrack", "Genre", "MediaType".
    NB : Ne me mens pas
    {generic_prompt}

    Examples:
    - Requête de l'utilisateur : "Lister tous les noms des artistes."
    Requête SQL : SELECT "Name" FROM public."Artist";

    - Requête de l'utilisateur : "Obtenir tous les albums sortis par l'artiste avec l'ID 5."
    Requête SQL : SELECT * FROM public."Album" WHERE "ArtistId" = 5;

    - Requête de l'utilisateur : "Lister tous les clients vivant en France."
    Requête SQL : SELECT * FROM public."Customer" WHERE "Country" = 'France';

    Requete utilisateur : "{requete}"
    Requete SQL :
    """
    try:
        response = openai.ChatCompletion.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant SQL expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )

        sql_query = response.choices[0].message.content.strip()
        
        sql_query = sql_query.replace("sql", "").replace("", "").strip()
        
        return sql_query
    except Exception as e:
        return f"Erreur lors de la génération de l'explication : {str(e)}"
    except Exception as e:
        return f"Erreur lors de la génération SQL : {str(e)}"


def execute_sql_query(sql_query):
    """Exécute une requête SQL et retourne les résultats."""
    conn = connect_to_postgres()
    if isinstance(conn, str):  # Gestion des erreurs de connexion
        return conn

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=columns)
            else:
                conn.commit()
                return "Requête exécutée avec succès sans résultat."
    except psycopg2.Error as e:
        return f"Erreur SQL : {e}"
    finally:
        conn.close()

def generate_report_from_result(result):
    """Génère un rapport détaillé basé sur le résultat de la requête SQL."""

    prompt = f"""
    Vous êtes un expert SQL et analyste en data marketing, spécialisé dans la création de rapports synthétiques et percutants. Rédigez un paragraphe captivant et clair en français, d’un maximum de six lignes, pour interpréter le résultat d'une requête SQL. Faites ressortir des insights puissants et pertinents.

    {generic_prompt}

    Directives :  
    - Mentionnez les noms des tables et colonnes entre guillemets doubles.  
    - Ne reproduisez pas la requête SQL, concentrez-vous sur une analyse enrichissante et accessible des résultats.  
    - Expliquez précisément les données fournies, leur contexte et leur impact potentiel, en illustrant par des exemples fictifs si nécessaire.  
    - Intégrez des statistiques ou comparaisons pertinentes pour valoriser l’information, comme un marketeur mondialement reconnu le ferait.  
    - Employez un ton affirmé et engageant pour convaincre et captiver l’audience.  

    Résultat de la requête : "{result}"  
    Rapport interprété :  
    """

    try:
        # Appel à l'API OpenAI
        response = openai.ChatCompletion.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant SQL expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )

        # Extraction de la réponse
        repport = response.choices[0].message.content.strip()
        return repport

    except Exception as e:
        # Gestion des erreurs
        return f"Une erreur est survenue : {e}"

def process_user_query():
    """Gère l'ensemble du flux : Génération question, génération SQL, exécution et rapport."""
    # Génération de la question
    question = generate_question_based_on_db_modele()
    print(question)
    
    sql_query = process_question_to_sql(question)
    if "Erreur" in sql_query:
        return sql_query, None, None

    result = execute_sql_query(sql_query)
    if isinstance(result, pd.DataFrame):
        report = generate_report_from_result(result.head(5))  # Limiter à 5 lignes pour le rapport
        return sql_query,report , result
    return sql_query, result, None


#Fonction pour generer un dataset sous le format jsonl a partir des different fonction (Génération question, génération SQL, exécution et rapport.) exp : [ { "role": "system", "content": "You are a SQL expert assistant. Generate clear, efficient SQL queries based on user requests. Provide only the SQL query without any additional text or explanation." }, { "role": "user", "content": "Using a database with tables 'customers' (columns: customer_id, name, email) and 'orders' (columns: order_id, customer_id, order_date, total_amount), show me all customers who have spent more than $1000 in total." }, { "role": "assistant", "content": "SELECT c.customer_id, c.name, c.email, SUM(o.total_amount) as total_spent FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name, c.email HAVING SUM(o.total_amount) > 1000 ORDER BY total_spent DESC;" } ]
def generate_dataset(questions):
    dataset = []
    if isinstance(questions, list):
        # Loop into questions
        #start from 1 to 20
        for i in range(2, 22):
            sql_query = process_question_to_sql(questions[i])
            result = execute_sql_query(sql_query)
            entries = [
                {"role": "system", "content": "Vous etes un assistant SQL expert."},
                {"role": "user", "content": questions[i]},
                {"role": "assistant", "content": result}
            ]
            dataset.extend(entries)
    else:
        print("Erreur : La fonction generate_question_based_on_db_modele n'a pas retourné une liste.")

    return dataset

if __name__ == "__main__":
    # Génération du dataset
    questions = generate_question_based_on_db_modele()
    print(questions)
    #output of questions : ['| Questions |', '| --- |', '| Quels sont les artistes ayant vendu le plus de titres ? |', "| Quels sont les clients ayant effectué le plus d'achats ? |", '| Quel est le genre musical le plus populaire ? |', '| Quel est le titre le plus long ? |', '| Quel est le titre le plus court ? |', '| Quels sont les albums les plus vendus ? |', '| Quels sont les clients les plus fidèles ? |', '| Quel est le montant total des ventes pour chaque année ? |', '| Quels sont les employés ayant le plus de clients attribués ? |', '| Quel est le titre le plus écouté dans les playlists ? |', '| Quels sont les genres musicaux les moins populaires ? |', '| Quels sont les albums les moins vendus ? |', '| Quel est le montant moyen des achats par client ? |', "| Quels sont les clients ayant dépensé le plus d'argent ? |", '| Quel est le titre le plus cher ? |', '| Quels sont les employés ayant travaillé le plus longtemps ? |', '| Quel est le nombre moyen de titres par album ? |', '| Quels sont les clients ayant acheté le plus de titres différents ? |', '| Quel est le pourcentage de clients ayant acheté des titres de chaque genre ? |', '| Quel est le nombre de pattes que possède un chat ? |']
    #clean the questions and create a list of questions
    questions_clean = [q.replace('|', '').replace('?', '') for q in questions if q != ""]
    print(questions_clean)

    dataset = generate_dataset(questions_clean)
    
    df = pd.DataFrame(dataset)
    df.to_json('data/dataset.jsonl', orient='records', lines=True)
    print("Dataset généré avec succès !")
    # # Exécution de la fonction pour générer un rapport
