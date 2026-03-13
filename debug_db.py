import sqlalchemy as sa

import app.core.database as d
import app.models.user  # noqa: F401


def main() -> None:
    d.Base.metadata.create_all(bind=d.engine)
    with d.engine.connect() as conn:
        db = conn.execute(sa.text("select database()")).scalar()
        tables = conn.execute(sa.text("show tables")).fetchall()
    print("db =", db)
    print("tables =", tables)


if __name__ == "__main__":
    main()
