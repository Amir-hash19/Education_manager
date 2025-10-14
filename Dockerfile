FROM python:3.12-slim


WORKDIR /usr/src/core


COPY ./requirements.txt .

# Dockerfile snippet
RUN pip install --upgrade pip setuptools wheel

# اول Redis و cache نصب می‌شوند
RUN pip install redis==5.0.8 asyncpg==0.30.0 argon2-cffi
RUN pip install fastapi-cache2[redis]==0.2.2 passlib[bcrypt]==1.7.4 email-validator==2.3.0


# بعد بقیه پکیج‌ها
RUN pip install pydantic==2.11.9 pydantic-core==2.33.2 pydantic-settings==2.11.0 pyjwt==1.7.1 SQLAlchemy==2.0.43 alembic==1.16.5


# RUN pip install -r requirements.txt


COPY ./app /usr/src/core/app
COPY .env .

CMD ["uvicorn", "app.main:app","--reload" ,"--host", "0.0.0.0", "--port", "8000"]


