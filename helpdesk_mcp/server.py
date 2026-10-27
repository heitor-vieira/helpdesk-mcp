from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from helpdesk_mcp.database import (
    DEFAULT_DB_PATH,
    find_tickets_by_client,
    initialize_database,
    list_tickets,
)


def create_server(db_path: Path = DEFAULT_DB_PATH) -> FastMCP:
    initialize_database(db_path)
    mcp = FastMCP("Helpdesk MCP")

    @mcp.tool
    def listar_chamados(status: str | None = None) -> list[dict[str, object]]:
        """Lista chamados, opcionalmente filtrados por status."""
        return list_tickets(status=status, db_path=db_path)

    @mcp.tool
    def buscar_historico_cliente(client_name: str) -> list[dict[str, object]]:
        """Busca chamados associados ao nome exato do cliente."""
        return find_tickets_by_client(client_name=client_name, db_path=db_path)

    return mcp


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
