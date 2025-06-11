from app.api import api  # noqa: F401 # type: ignore
import uvicorn


def main():
    print("Hello from backend!")

    uvicorn.run(
        app="app.api:api",
        loop="asyncio",
        reload=True,
    )


if __name__ == "__main__":
    main()
