from datetime import datetime
import re
from backend_database_query.connectors.WatsonxClient import WatsonxClient
from backend_database_query.connectors.DbManager import DatabaseManager
from backend_database_query.env import WatsonxConfig, WatsonxAPIConfig, Db2Config, config_env


def process_nl_query(nl_query: str) -> list:
    """
    Args:
        nl_query (str): Consulta en lenguaje natural
    Returns:
        list: Lista de filas resultado de la consulta
    """
    watsonx_translator_config = WatsonxConfig(deployment_id=config_env.get("WATSONX_AI_DEPLOYMENT_ID"))
    watsonx_interpret_config = WatsonxConfig(deployment_id=config_env.get("WATSONX_AI_DEPLOYMENT_INTERPRETATION_ID"))
    watsonx_api_config = WatsonxAPIConfig()
    db2_config = Db2Config()

    # 1. Traducir LN a SQL usando Watsonx
    watsonx_translator = WatsonxClient(watsonx_translator_config, watsonx_api_config)
    
    input_params_translator = {
    "prompt_variables": {
        "sentiment_query": nl_query,
    }
}
    try:
        sql_response = watsonx_translator.text_generation(
            params=input_params_translator,
            #deployment_id=watsonx_translator_config.deployment_id
        )
        
    except Exception as e:
        return f"Error generando la consulta SQL: {e}"

    # 2. Ejecutar SQL
    print(f"SQL Response: {sql_response}")

    db = DatabaseManager(db2_config)
    try:
        result_rows = db.execute_raw_sql(sql_response)
    except Exception as e:
        db.logger.error(f"Error ejecutando SQL: {e}")
        return "Error al ejecutar la consulta en la base de datos."

    if not result_rows:
        return "No se encontraron resultados para la consulta."
    
    print(f"Result Rows: {result_rows}")

    # 3. Enviar resultados tabulares a Watsonx para interpretación en LN
    watsonx_interpret = WatsonxClient(watsonx_interpret_config, watsonx_api_config)
    results_str = str(result_rows)

    input_params_interpret = {
        "prompt_variables": {
            "user_query": nl_query,
            "sentiment_results": results_str
        }
    }

    try:
        interpretation = watsonx_interpret.text_generation(
            params=input_params_interpret,
            #deployment_id=watsonx_interpret_config
        )
        final_response = interpretation
    except Exception as e:
        watsonx_interpret.logger.error(f"Error interpretando resultados: {e}")
        final_response = f"No se pudo generar una interpretación de los resultados."

    return final_response