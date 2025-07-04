from datetime import datetime
from fastapi_template.connectors.WatsonxClient import WatsonxClient
from fastapi_template.connectors.DbManager import DatabaseManager
from fastapi_template.env import WatsonxConfig, WatsonxAPIConfig, Db2Config

top_k = 5
date = datetime.now().strftime("%Y-%m-%d 00:00:00.0")

SQL_TRANSLATE_PROMPT = f"""
    You are an agent specialized in translating natural language queries into SQL.  
    The user will input a query about a table in natural language, and your task is to return ONLY the equivalent SQL query corresponding to the user's request.

    Given a query, generate a syntactically correct SQL statement to help find the answer.  
    Unless the user explicitly specifies a number of examples to retrieve, ALWAYS limit the query to {top_k} results at most.

    If the user's query includes a time reference such as "the last 3 months", assume the current date is: {date}.  
    All date and datetime values must be formatted as 'YYYY-MM-DD 00:00:00.0' to match the DB2 timestamp format.  
    For example: use '2024-01-01 00:00:00.0' instead of '2024-01-01'.

    Table field description for ListaActividadesSMLR:  
    - ID: Unique identifier for each activity.  
    - Título: Description or name of the event or activity.  
    - Ámbito CASA: Thematic area assigned by the Royal Household.  
    - Ámbito SECRETARÍA: Thematic area assigned by the Secretariat.  
    - Subámbito: More specific subcategory within the thematic area.  
    - ACT_SMLR_Area1: Additional thematic categorization (may be empty).  
    - Area 2: Further thematic subdivision (may be empty).  
    - Area 3: Further thematic subdivision (may be empty).  
    - Tematica: Main theme of the event (often empty).  
    - ACT_SMLR_TipoAct: General type of activity, such as "Acto", "Audiencia", "Presidencia de honor", "Viaje con SM el Rey", "Viaje en solitario", "Videoconferencia".  
    - ANEXO Organizaciones/Colectivos: Entities or groups participating in the event.  
    - Estado: Status of the request or activity ("Archivado", "Borrador", "Celebrado", "Denegado", "Fijado", "Tomado nota").  
    - Fecha Solicitud: Date on which the activity was requested (TIMESTAMP).  
    - Fecha de celebración: Date on which the activity took place (TIMESTAMP).  
    - Lugar de Celebración: City or location where the activity was held.  
    - Número de asistentes: Total number of participants.  
    - Nombre y apellidos del solicitante: Name of the person who submitted the request.  
    - Cargo del solicitante: Position or role of the requester.  
    - Dirección del solicitante: Postal address of the requester (optional).  
    - Teléfono del solicitante: Contact phone number of the requester (optional).  
    - Email del solicitante: Email address of the requester (optional).  
    - Observaciones: Additional notes related to the activity.  
    - Petición de informes: Indicates whether a report was requested (VERDADERO/FALSO).  
    - Observaciones2: Additional field for comments (may be empty).  
    - Resultados informes: Result of the requested report ("Favorable", "Pendiente", "Desfavorable", "Sin criterio").  
    - Enviada Notificación: Indicates whether a post-event notification was sent.  
    - ACT_SMLR_TipoActividad: Specific classification of the type of activity carried out.  
    - Miembro: Representative of the Royal Household who participated (if applicable).  

    *** EXAMPLES ***

    Natural language: "Dime todas las actividades que se realizaron en 2023"  
    SQL response: 'SELECT * FROM ListaActividadesSMLR WHERE YEAR([Fecha de celebración]) = 2023'

    Natural language: "Cuántas actividades tienen el subámbito cáncer"  
    SQL response: 'SELECT COUNT(*) FROM ListaActividadesSMLR WHERE LOWER([Subámbito]) = 'cáncer''

    Natural language: "Lista las actividades con informes pendientes"  
    SQL response: 'SELECT * FROM ListaActividadesSMLR WHERE LOWER([Resultados informes]) = 'pendiente''

    Natural language: "Cuáles son los ámbitos casa más comunes"  
    SQL response: 'SELECT [Ámbito CASA], COUNT(*) AS total FROM ListaActividadesSMLR GROUP BY [Ámbito CASA] ORDER BY total DESC'

    Natural language: "Ver actividades con múltiples organizaciones o colectivos"  
    SQL response: 'SELECT * FROM ListaActividadesSMLR WHERE [ANEXO Organizaciones/Colectivos] IS NOT NULL'

    Natural language: "Dime los actos relacionados con la mujer celebrados en Madrid"  
    SQL response: 'SELECT * FROM ListaActividadesSMLR WHERE (LOWER([Ámbito CASA]) = 'mujer' OR LOWER([Ámbito SECRETARÍA]) = 'mujer' OR LOWER([Subámbito]) = 'mujer') AND LOWER([Lugar de Celebración]) LIKE '%madrid%''

    Natural language: "Cuántas actividades pidieron informe y recibieron resultado favorable"  
    SQL response: 'SELECT COUNT(*) FROM ListaActividadesSMLR WHERE [Petición de informes] = VERDADERO AND LOWER([Resultados informes]) = 'favorable''

    Natural language: "Cuáles son los tipos de actividad más comunes entre 2023 y 2025"  
    SQL response: 'SELECT [ACT_SMLR_TipoActividad], COUNT(*) AS total FROM ListaActividadesSMLR WHERE [Fecha de celebración] BETWEEN '2023-01-01 00:00:00.0' AND '2025-12-31 00:00:00.0' GROUP BY [ACT_SMLR_TipoActividad] ORDER BY total DESC'

    *** Output format ***
    - Respond only with the valid SQL query, with no extra text, comments, or explanations.  
    - Remove all line breaks or any non-SQL text from the response.
"""

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

    # 1. Traducir NL a SQL usando Watsonx
    watsonx = WatsonxClient(watsonx_config, watsonx_api_config)
    prompt = f"{SQL_TRANSLATE_PROMPT}\n{nl_query}"
    sql_response = watsonx.text_generation(prompt_query=prompt)
    sql_query = sql_response["results"][0]["generated_text"] if sql_response and "results" in sql_response else ""

    # 2. Ejecutar SQL
    db = DatabaseManager(db2_config)
    try:
        result_rows = db.execute_sql(sql_query)
    except Exception as e:
        db.logger.error(f"Error ejecutando SQL: {e}")
        return "Error al ejecutar la consulta en la base de datos."

    if not result_rows:
        return "No se encontraron resultados para la consulta."

    # 3. Enviar resultados tabulares a Watsonx para interpretación en lenguaje natural
    results_str = str(result_rows[:5])  # Limita a 5 filas
    interpretation_prompt = (
        f'''La siguiente tabla es el resultado de una consulta sobre actividades de Su Majestad La Reina Letizia:\n
        {results_str}\n"
        Redacta una respuesta en lenguaje natural basada en esos datos, adecuada para el usuario final.'''
    )

    interpretation = watsonx.text_generation(prompt_query=interpretation_prompt)
    final_response = interpretation["results"][0]["generated_text"].strip() if interpretation and "results" in interpretation else ""

    return final_response or "No se pudo generar una interpretación de los resultados."