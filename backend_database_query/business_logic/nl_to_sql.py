from datetime import datetime
from backend_database_query.connectors.WatsonxClient import WatsonxClient
from backend_database_query.connectors.DbManager import DatabaseManager
from backend_database_query.env import WatsonxConfig, WatsonxAPIConfig, Db2Config, WATSONX_INTERPRET_DEPLOYMENT_ID


def process_nl_query(nl_query: str) -> list:
    """
    Args:
        nl_query (str): Consulta en lenguaje natural
    Returns:
        list: Lista de filas resultado de la consulta
    """
    watsonx_config = WatsonxConfig()
    watsonx_api_config = WatsonxAPIConfig()
    db2_config = Db2Config()

    # 1. Traducir LN a SQL usando Watsonx
    watsonx = WatsonxClient(watsonx_config, watsonx_api_config)
    
    input_params = {'user_query':nl_query}
    try:
        sql_response = watsonx.text_generation(
            params=input_params,
            deployment_id=watsonx_config.deployment_id  # Viene de env.py
        )
        sql_query = sql_response["results"][0]["generated_text"].strip()
    except Exception as e:
        return f"Error generando la consulta SQL: {e}"

    if not sql_query.lower().startswith("select"):
        return "La consulta generada no es válida. Reformula tu pregunta."

    # 2. Ejecutar SQL
    db = DatabaseManager(db2_config)
    try:
        result_rows = db.execute_sql(sql_query)
    except Exception as e:
        db.logger.error(f"Error ejecutando SQL: {e}")
        return "Error al ejecutar la consulta en la base de datos."

    if not result_rows:
        return "No se encontraron resultados para la consulta."

    # 3. Enviar resultados tabulares a Watsonx para interpretación en LN
    results_str = str(result_rows)
    try:
        interpretation = watsonx.text_generation(
            params={
                "user_query": nl_query,
                "query_result": results_str
            },
            deployment_id=WATSONX_INTERPRET_DEPLOYMENT_ID
        )
        final_response = interpretation["results"][0]["generated_text"].strip()
    except Exception as e:
        watsonx.logger.error(f"Error interpretando resultados: {e}")
        final_response = "No se pudo generar una interpretación de los resultados."

    return final_response or "No se pudo generar una interpretación de los resultados."