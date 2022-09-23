from backend_base_layer import http_response

def lambda_handler(event, context) -> str:
    print("request:", event)
    return http_response({"somekey": "someval"})
