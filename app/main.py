from fastapi import FastAPI


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
