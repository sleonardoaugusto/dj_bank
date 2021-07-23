# Dj Bank

[![Tests](https://github.com/sleonardoaugusto/dj_bank/actions/workflows/tests.yaml/badge.svg)](https://github.com/sleonardoaugusto/dj_bank/actions/workflows/tests.yaml)

A simple bank transactions system.

## How develop?

1. Clone this repo.
2. Create a virtualenv with Python 3.x.
3. Activate virtualenv.
4. Install dependencies.
5. Setup instance with .env.
6. Run tests.

```console
git clone git@github.com:sleonardoaugusto/dj_bank.git
cd dj_bank
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp contrib/env-sample .env
pytest
```

### Documentation

http://localhost:8000/api/docs/