import functions_framework
from json import dumps

@functions_framework.http
def hello_star_wars(request):
    """
    Handler básico para testar a conectividade e o framework.
    """
    print("Recebendo requisição no Insights API...")

    payload = {
        "message": "Que a Força esteja com você!",
        "status": "online",
        "api_version": "v1"
    }
    
    response_body = dumps(payload, ensure_ascii=False)

    return response_body, 200, {
        'Content-Type': 'application/json; charset=utf-8'
    }