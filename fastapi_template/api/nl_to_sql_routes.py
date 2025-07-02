from fastapi import APIRouter, Body
from fastapi_template.business_logic.nl_to_sql_flow import process_nl_query
from fastapi_template.env import WatsonxConfig, WatsonxAPIConfig, Db2Config

nl_to_sql_bp = APIRouter(prefix='/api/nl-to-sql', tags=['NL to SQL'])

@nl_to_sql_bp.post('/', summary="Consulta en lenguaje natural a SQL y DB2")
def nl_to_sql_endpoint(query: str = Body(..., embed=True)):
    """
    Recibe una consulta en lenguaje natural, la traduce a SQL y ejecuta en DB2.
    """
    result = process_nl_query(query)
    return {"rows": result} 