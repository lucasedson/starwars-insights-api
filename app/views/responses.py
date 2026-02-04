import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InsightResponse(BaseModel):
    status: str = "success"
    entity: str
    category: str
    insight_value: Any = Field(..., description="O dado filtrado ou objeto completo")
    source: str = Field(default="SWAPI Ecosystem", description="Origem da informação (Firestore/Live)")
    suggestion: Optional[str] = None

    class Config:
        json_encoders = {str: lambda v: v.encode('utf-8').decode('utf-8')}

def format_insight_response(
    data: Dict, 
    filter_fields: Optional[list[str]] = None, 
    source: str = "SWAPI Ecosystem",
    suggestion: Optional[str] = None 
) -> tuple:
    """
    Formata uma resposta para uma requisiçãoo de insight.

    Parameters
    ----------
    data : Dict
        Dados da entidade.
    filter_fields : Optional[list[str]]
        Se informado, retorna apenas os campos especificados.
    source : str
        Origem da informação (Firestore/Live).
    suggestion : Optional[str]
        Sugestão de busca para o caso de não encontrar a entidade.

    Returns
    -------
    tuple
        Tupla com a resposta formatada em JSON, o c digo de status HTTP e os headers da resposta.
    """
    if not data or "error" in data:
        return _format_error_response(data, 404)

    if filter_fields:
        insight_value = {field: data.get(field) for field in filter_fields}
        if all(value is None for value in insight_value.values()):
            return _format_error_response({
                "error": f"Atributos '{', '.join(filter_fields)}' não encontrados."
            }, 404)
    else:
        insight_value = data


    response_model = InsightResponse(
        entity=data.get("name") or data.get("title", "Unknown"),
        category=data.get("type", "generic"),
        insight_value=insight_value,
        source=source,
        suggestion=suggestion 
    )

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
    }

    return (response_model.model_dump_json(by_alias=True), 200, headers)

def _format_error_response(error_data: Dict, status_code: int = 400) -> tuple:
    
    """
    Formata uma resposta para uma requisição de insight com um erro.

    Parameters
    ----------
    error_data : Dict
        Dados do erro.
    status_code : int
        C digo de status HTTP.

    Returns
    -------
    tuple
        Tupla com a resposta formatada em JSON, o código de status HTTP e os headers da resposta.
    """
    headers = {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}
    body = json.dumps({
        "status": "error",
        "message": error_data.get("error", "Erro desconhecido"),
        "details": error_data.get("details", "")
    }, ensure_ascii=False)
    
    
    return (body, status_code, headers)