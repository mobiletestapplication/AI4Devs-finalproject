import os

# La aplicación valida los ajustes al importarse; los tests no necesitan una BD real.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://traide@localhost:5432/traide_tests")
