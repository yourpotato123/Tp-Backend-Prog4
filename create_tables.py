print(">>> Ejecutando create_tables.py")

from database import create_db_and_tables
import models  # IMPORTANTE: registra todos los modelos en SQLModel.metadata


def main():
    print(">>> Creando tablas en la base de datos…")
    create_db_and_tables()
    print(">>> Tablas creadas correctamente.")


if __name__ == "__main__":
    main()
