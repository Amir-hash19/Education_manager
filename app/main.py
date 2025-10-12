from fastapi import FastAPI
from app.users.routes import userrouter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded



app = FastAPI(
    title="Education Manager Project ",
    description="""
    This project will provide admin panel,
    customers and bootcamp managment services
    for admins""",
    version="0.0.01",
    contact={
        "name": "Amirhosein heidari",
        "url": "https://Amir-hash19.github.io",
        "email": "amirhosein.hydri1381@email.com",
    },
    license_info={
        "name": "MIT",
        
    },    
    openapi_tags=[{
        "name":"Udemy clone",
        "description": "managing CRUD operations for objects"
    }
    ]
    
)


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(userrouter, tags=["uers"])