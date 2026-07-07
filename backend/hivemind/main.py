"""Entrypoint: uvicorn run of the Hivemind demo server."""
import uvicorn


def main() -> None:
    uvicorn.run("hivemind.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
