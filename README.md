# SQL Assistant with OpenAI

This project provides an interactive interface to generate and execute SQL queries on a PostgreSQL database using natural language input. It leverages OpenAI's language model to translate user queries into SQL and provides detailed reports based on the query results.

## Features

- **Natural Language to SQL**: Converts user queries in natural language to SQL queries.
- **PostgreSQL Integration**: Executes the generated SQL queries on a PostgreSQL database.
- **Detailed Reports**: Generates detailed reports based on the query results.
- **Interactive Interface**: Provides an interactive interface using Gradio.

## Requirements

- Python 3.10 or higher
- PostgreSQL
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/sql-assistant.git
   cd sql-assistant
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Set up your PostgreSQL database using the provided `Chinook_PostgreSql.sql` script.

5. Create a `.env` file in the project root and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Run the main script to start the Gradio interface:

   ```sh
   python main.py
   ```

2. Open the provided URL in your browser to access the interface.

3. Enter your query in natural language and get the SQL query, detailed report, and query results.

## Example Queries

- "Lister tous les noms des artistes."
- "Lister tous les titres des albums."
- "Obtenir tous les clients vivant en France."
- "Quelles sont les dernières ventes effectuées ?"
- "Combien de pistes sont disponibles dans chaque playlist ?"

## Project Structure

- `main.py`: Main script to run the Gradio interface.
- `Chinook_PostgreSql.sql`: SQL script to set up the PostgreSQL database.
- `requirements.txt`: List of required Python packages.
- `.env`: Environment file to store sensitive information like API keys.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenAI](https://openai.com) for providing the language model.
- [Gradio](https://gradio.app) for the interactive interface.
- [Chinook Database](http://www.codeplex.com/ChinookDatabase) for the sample database.
