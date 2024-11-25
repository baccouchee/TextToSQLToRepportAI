import os
import gradio as gr
import psycopg2
import openai
import pandas as pd

# Configuration API OpenAI
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

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
            model="meta-llama/llama-3.1-8b-instruct:free",
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
            model="meta-llama/llama-3.1-8b-instruct:free",
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


def process_user_query(requete):
    """Gère l'ensemble du flux : génération SQL, exécution et rapport."""
    sql_query = process_question_to_sql(requete)
    if "Erreur" in sql_query:
        return sql_query, None, None

    result = execute_sql_query(sql_query)
    if isinstance(result, pd.DataFrame):
        report = generate_report_from_result(result.head(5))  # Limiter à 5 lignes pour le rapport
        return sql_query,report , result
    return sql_query, result, None

# Interface Gradio
iface = gr.Interface(
    fn=process_user_query,
    inputs=gr.Textbox(lines=2, placeholder="Exemple : Listez tous les noms des artistes."),
    outputs=[
        gr.Textbox(label="Requête SQL générée", lines=3),
        gr.Textbox(label="Rapport détaillé", lines=3),
        gr.DataFrame(label="Résultat de la requête"),

    ],
    title="Assistant SQL avec OpenAI",
    description=(
        "Posez une question en langage naturel, et l'outil générera une requête SQL exécutée sur une base PostgreSQL. "
        "Les résultats et un rapport détaillé seront affichés."
    ),
    examples=[
        ["Lister tous les noms des artistes."],
        ["Lister tous les titres des albums."],
        ["Obtenir tous les clients vivant en France."],
        ["Quelles sont les dernières ventes effectuées ?"],
        ["Combien de pistes sont disponibles dans chaque playlist ?"],
    ],
    theme="Soft"
)

if __name__ == "__main__":
    iface.launch()
