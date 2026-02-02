import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InsightResponse(BaseModel):
    status: str = "success"
    entity: str
    category: str
    insight_value: Any = Field(..., description="O dado filtrado ou objeto completo")
    source: str = Field(default="SWAPI Ecosystem", description="Origem da informação (Firestore/Live)")

    class Config:
        json_encoders = {str: lambda v: v.encode('utf-8').decode('utf-8')}

def format_insight_response(data: Dict, filter_fields: Optional[list[str]] = None, source: str = "SWAPI Ecosystem") -> tuple:
    """
    Transforma o Model bruto em uma estrutura de View (JSON + HTTP Status).
    """
    if not data or "error" in data:
        return _format_error_response(data)

    if filter_fields:
        insight_value = {field: data.get(field) for field in filter_fields}

        if all(value is None for value in insight_value.values()):
            return _format_error_response({"error": f"Nenhum dos atributos solicitados em '{', '.join(filter_fields)}' foi encontrado."}, 404)
    else:
        # Se não houver filtro, retorna o objeto completo
        insight_value = data


    response_model = InsightResponse(
        entity=data.get("name") or data.get("title", "Unknown"),
        category=data.get("type", "generic"),
        insight_value=insight_value,
        source=source
    )

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
    }


    return (response_model.model_dump_json(by_alias=True), 200, headers)

def _format_error_response(error_data: Dict, status_code: int = 400) -> tuple:
    headers = {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}
    body = json.dumps({
        "status": "error",
        "message": error_data.get("error", "Erro desconhecido"),
        "details": error_data.get("details", "")
    }, ensure_ascii=False)
    
    return (body, status_code, headers)