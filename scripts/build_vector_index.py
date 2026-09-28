"""Vector index builder reserved for the later embedding and FAISS phase."""


def main() -> None:
    """Avoid creating an empty or misleading index before ingestion is configured."""
    raise NotImplementedError("Vector indexing is planned after an embedding provider is selected")


if __name__ == "__main__":
    main()