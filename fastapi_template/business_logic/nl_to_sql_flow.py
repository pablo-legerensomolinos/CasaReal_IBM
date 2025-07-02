from fastapi_template.connectors.WatsonxClient import WatsonxClient
from fastapi_template.connectors.DbManager import DatabaseManager
from fastapi_template.env import WatsonxConfig, WatsonxAPIConfig, Db2Config

# Puedes ajustar estas instrucciones según tu prompt/modelo
WATSONX_SQL_INSTRUCTIONS = "Traduce la siguiente consulta en lenguaje natural a SQL para DB2:"

def process_nl_query(nl_query: str) -> list:
    """
    Orquesta el flujo: NL -> Watsonx (SQL) -> DB2 -> Respuesta
    Args:
        nl_query (str): Consulta en lenguaje natural
    Returns:
        list: Lista de filas resultado de la consulta
    """
    # Instanciar configuraciones
    watsonx_config = WatsonxConfig()
    watsonx_api_config = WatsonxAPIConfig()
    db2_config = Db2Config()

    # 1. Traducir NL a SQL usando Watsonx
    watsonx = WatsonxClient(watsonx_config, watsonx_api_config)
    prompt = f"{WATSONX_SQL_INSTRUCTIONS}\n{nl_query}"
    sql_response = watsonx.text_generation(prompt_query=prompt)
    # Suponemos que el modelo devuelve el SQL como texto plano
    sql_query = sql_response["results"][0]["generated_text"] if sql_response and "results" in sql_response else ""

    # 2. Ejecutar SQL en DB2
    db = DatabaseManager(db2_config)
    # Aquí deberías implementar un método execute_raw_sql en DatabaseManager
    result = db.connection.execute(sql_query).fetchall() if sql_query else []
    # Convertir a lista de dicts para serializar
    rows = [dict(row) for row in result]

    # 3. Retornar lista de filas
    return rows 