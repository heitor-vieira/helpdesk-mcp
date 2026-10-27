from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client

from helpdesk_mcp.database import initialize_database
from helpdesk_mcp.server import create_server


class BuscarHistoricoClienteTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "helpdesk.db"
        initialize_database(self.db_path)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM ticket_history")
            connection.execute("DELETE FROM tickets")
            connection.executemany(
                """
                INSERT INTO tickets (
                    ticket_id, client_name, description, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        203,
                        "Ana Souza",
                        "Chamado mais recente",
                        "aberto",
                        "2025-02-03T09:00:00Z",
                        "2025-02-03T09:00:00Z",
                    ),
                    (
                        202,
                        "Ana Souza Silva",
                        "Cliente com nome semelhante",
                        "resolvido",
                        "2025-02-02T09:00:00Z",
                        "2025-02-02T09:00:00Z",
                    ),
                    (
                        201,
                        "Ana Souza",
                        "Chamado inicial",
                        "em_andamento",
                        "2025-02-01T09:00:00Z",
                        "2025-02-01T10:00:00Z",
                    ),
                ],
            )
        self.server = create_server(self.db_path)
        self.client = Client(self.server)
        await self.client.__aenter__()

    async def asyncTearDown(self) -> None:
        await self.client.__aexit__(None, None, None)
        self.temp_dir.cleanup()

    async def call_tool(self, client_name: str) -> list[dict[str, object]]:
        result = await self.client.call_tool(
            "buscar_historico_cliente", {"client_name": client_name}
        )
        self.assertIsNotNone(result.structured_content)
        structured = result.structured_content
        self.assertIsInstance(structured, dict)
        return structured["result"]

    async def test_tool_is_registered_with_mcp_server(self) -> None:
        tools = await self.client.list_tools()

        self.assertIn("buscar_historico_cliente", {tool.name for tool in tools})

    async def test_returns_exact_client_matches_ordered_and_audited(self) -> None:
        tickets_before = self._ticket_rows()

        tickets = await self.call_tool("Ana Souza")

        self.assertEqual([ticket["ticket_id"] for ticket in tickets], [201, 203])
        self.assertTrue(all(ticket["client_name"] == "Ana Souza" for ticket in tickets))
        self.assertEqual(
            set(tickets[0]),
            {
                "ticket_id",
                "client_name",
                "description",
                "status",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(self._ticket_rows(), tickets_before)
        with sqlite3.connect(self.db_path) as connection:
            events = connection.execute(
                """
                SELECT ticket_id, action
                FROM ticket_history
                ORDER BY ticket_id
                """
            ).fetchall()
        self.assertEqual(events, [(201, "consulta"), (203, "consulta")])

    async def test_unknown_client_returns_empty_without_audit_events(self) -> None:
        tickets = await self.call_tool("Cliente inexistente")

        self.assertEqual(tickets, [])
        self.assertEqual(self._query_event_count(), 0)

    async def test_partial_or_different_text_does_not_match(self) -> None:
        for client_name in ("Ana", "ana souza", "Ana Souza "):
            with self.subTest(client_name=client_name):
                self.assertEqual(await self.call_tool(client_name), [])
        self.assertEqual(self._query_event_count(), 0)

    async def test_empty_name_is_compared_as_an_exact_value(self) -> None:
        self.assertEqual(await self.call_tool(""), [])
        self.assertEqual(self._query_event_count(), 0)

    async def test_missing_or_non_text_name_is_rejected(self) -> None:
        for arguments in ({}, {"client_name": 123}):
            with self.subTest(arguments=arguments):
                result = await self.client.call_tool(
                    "buscar_historico_cliente",
                    arguments,
                    raise_on_error=False,
                )
                self.assertTrue(result.is_error)
        self.assertEqual(self._query_event_count(), 0)

    def _query_event_count(self) -> int:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'consulta'"
            ).fetchone()[0]

    def _ticket_rows(self) -> list[tuple[object, ...]]:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute(
                """
                SELECT ticket_id, client_name, description, status, created_at, updated_at
                FROM tickets
                ORDER BY ticket_id
                """
            ).fetchall()
