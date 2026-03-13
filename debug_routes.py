from fastapi.routing import APIRoute

from app.main import app


def main() -> None:
    for r in app.routes:
        if isinstance(r, APIRoute):
            print(r.name, r.path, r.methods)


if __name__ == "__main__":
    main()
