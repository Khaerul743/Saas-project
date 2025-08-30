from slowapi import Limiter
from slowapi.util import get_remote_address

# def real_ip(request):
#     return request.headers.get("X-Forwarded-For", request.client.host)

# limiter = Limiter(key_func=real_ip, default_limits=["100/minute"])

# Definisikan limiter di sini
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # global default, bisa override per endpoint
)
