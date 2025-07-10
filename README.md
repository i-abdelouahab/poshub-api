# 🚀 poshub-api

A minimal and extensible FastAPI service for managing orders with internal/external integrations.

---

## 🧰 Project Setup

### ✅ Requirements

- Python ≥ 3.10
- [Poetry](https://python-poetry.org/docs/#installation)
- (Optional) `pre-commit` for code linting

### 🔧 Install dependencies

```bash
poetry 
```

### ▶️ Run locally (development)

```bash
poetry run uvicorn poshub_api.main:app --reload
```

Visit: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Tests

- Sync tests with `TestClient`
- Async tests with `pytest-asyncio`

```bash
poetry run pytest
```

> External calls are mocked via [`respx`](https://github.com/lundberg/respx).

---

## 📁 Project Structure Approaches

FastAPI is flexible in how you structure your code. Below are **three common options** for scalable backend services:

---

### 1️⃣ Flat / Minimal (for quick PoCs)

```
src/
  poshub_api/
    main.py
    models.py
    routes.py
    services.py
  tests/
    test_services.py
    ...
```

- ✅ Easy for beginners and fast to prototype  
- ❌ Becomes hard to maintain in growing codebases

---

### 2️⃣ Layered / Domain-Centric ✅ (Chosen for this project)

```
src/
  poshub_api/
    main.py
    api/
      routers/
        orders.py
    domain/
      models.py
      entities.py
    services/
      order_service.py
    infrastructure/
      http/
        external_client.py
    shared/
      exceptions.py
      dependencies.py
      logger.py
  tests/
    services/
      test_order_service.py
    ...
```

- ✅ Clear separation of concerns (API, domain, infra, shared)  
- ✅ Scales well for mid-to-large projects  
- ❌ Slightly more verbose setup

---

### 3️⃣ Feature-Based / Modular

```
src/
  poshub_api/
    main.py
    modules/
      orders/
        router.py
        models.py
        service.py
      users/
        router.py
        models.py
    shared/
      config.py
  tests/
    orders/
      test_service.py
    ...
      
```

- ✅ Modules are independent and testable  
- ✅ Good fit for microservice-aligned architectures  
- ❌ Some code duplication if not managed well

---

## 🛡️ Features Implemented (Chapter 1 Scope)

- [x] `GET /health` route
- [x] `POST /orders` and `GET /orders/{id}` (in-memory)
- [x] Pydantic v2 strict models (validation, aliases)
- [x] Dependency-injected `OrderService`
- [x] External HTTP call with:
  - Shared `httpx.AsyncClient` in lifespan
  - Retry via `tenacity`
  - Structured logs via `structlog`
- [x] Global exception handler
- [x] `X-Correlation-ID` middleware
- [x] Auth via `HTTPBearer` + JWT + scope check
- [x] OpenAPI JSON export (`openapi/poshub_v1.json`)
- [x] Test coverage for core routes

---

## OpenAPI JSON

```bash
# For the raw JSON schema
http://localhost:8000/openapi.json
```


## 🧹 Linting & Formatting

Install pre-commit hooks (auto-format on commit):

```bash
pre-commit install
```

Included tools:
- `black`
- `isort`
- `flake8`

---

## 🐳 Bonus (Optional)

- `Dockerfile` for containerization
- GitHub Actions workflow for CI/CD

---

## 📄 License

MIT – see `LICENSE` file.

## Install dependencies

```bash
# forced x86_64 architecture to avoid mismatch during dependencies installation
docker run --rm \                                                        
  -v $(pwd):/var/task \
  -w /var/task \
  public.ecr.aws/sam/build-python3.12:latest-x86_64 \
  /bin/sh -c "pip install -r requirements.txt -t layer/python --no-cache-dir --platform manylinux2014_x86_64 --only-binary=:all:"
cd layer && zip -r9 ../layer.zip python && cd .. # generate zip
```

## Build functions within an AWS Lambda-like container

```bash
sam build --use-container -t sam-min.yaml --cached 
```

```bash
sam build --template-file sam-min.yaml 
```

## Invoke Lambda function locally using an event

```bash
sam local invoke --container-host 127.0.0.1 -t sam-min.yaml -e event.json
```

## SAM Deploy
```bash
sam deploy --stack-name poshub-dev-api # create an api gateway for our app
```

## Publish FastApiLayer (lambda function dependencies)

```bash
ismailabdelouahab@Ismails-MacBook-Pro poshub-api % aws lambda publish-layer-version \                     
  --layer-name SimpleFastApiLayer \     
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.12 \ 
  --region eu-north-1 
```

## Create AWS Lambda Function

```bash
ismailabdelouahab@Ismails-MacBook-Pro poshub-api % aws lambda create-function \                           
  --function-name PosHubFunctionManual \
  --runtime python3.12 \
  --handler poshub_api.main.handler \
  --zip-file fileb://lambda.zip \
  --role arn:aws:iam::471448382724:role/poshub-lambda-role \
  --layers arn:aws:lambda:eu-north-1:471448382724:layer:SimpleFastApiLayer:5 \
  --region eu-north-1
```