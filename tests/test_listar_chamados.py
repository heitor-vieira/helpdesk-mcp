from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client

from helpdesk_mcp.database import (
    VALID_STATUSES,
    initialize_database,
    list_tickets,
)
from helpdesk_mcp.server import create_server


class ListarChamadosTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "nested" / "helpdesk.db"
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
                        101,
                        "Cliente Um",
                        "Chamado aberto",
                        "aberto",
                        "2025-02-01T09:00:00Z",
                        "2025-02-01T09:00:00Z",
                    ),
                    (
                        102,
                        "Cliente Dois",
                        "Chamado em andamento",
                        "em_andamento",
                        "2025-02-02T09:00:00Z",
                        "2025-02-02T10:00:00Z",
                    ),
                    (
                        103,
                        "Cliente Três",
                        "Chamado resolvido",
                        "resolvido",
                        "2025-02-03T09:00:00Z",
                        "2025-02-03T11:00:00Z",
                    ),
                    (
                        104,
                        "Cliente Quatro",
                        "Chamado fechado",
                        "fechado",
                        "2025-02-04T09:00:00Z",
                        "2025-02-04T12:00:00Z",
                    ),
                ],
            )
        self.server = create_server(self.db_path)
        self.client = Client(self.server)
        await self.client.__aenter__()

    async def asyncTearDown(self) -> None:
        await self.client.__aexit__(None, None, None)
        self.temp_dir.cleanup()

    async def call_tool(self, **arguments: str) -> list[dict[str, object]]:
        result = await self.client.call_tool("listar_chamados", arguments)
        self.assertIsNotNone(result.structured_content)
        structured = result.structured_content
        self.assertIsInstance(structured, dict)
        return structured["result"]

    async def test_lists_all_tickets_with_required_fields(self) -> None:
        tickets = await self.call_tool()

        self.assertEqual([ticket["ticket_id"] for ticket in tickets], [101, 102, 103, 104])
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
        self.assertEqual(tickets[0]["client_name"], "Cliente Um")
        self.assertEqual(tickets[0]["created_at"], "2025-02-01T09:00:00Z")
        self.assertEqual(tickets[0]["updated_at"], "2025-02-01T09:00:00Z")

    async def test_filters_each_allowed_status(self) -> None:
        for status in VALID_STATUSES:
            with self.subTest(status=status):
                tickets = await self.call_tool(status=status)
                self.assertTrue(tickets)
                self.assertTrue(all(ticket["status"] == status for ticket in tickets))

    async def test_valid_status_without_matches_returns_empty_list(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM tickets WHERE status = 'fechado'")
        self.assertEqual(await self.call_tool(status="fechado"), [])
        with sqlite3.connect(self.db_path) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'consulta'"
            ).fetchone()[0]
        self.assertEqual(count, 0)

        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM tickets")
        self.assertEqual(await self.call_tool(), [])
        self.assertEqual(await self.call_tool(status="aberto"), [])

    async def test_invalid_status_is_rejected(self) -> None:
        for status in ("pendente", ""):
            with self.subTest(status=status):
                result = await self.client.call_tool(
                    "listar_chamados",
                    {"status": status},
                    raise_on_error=False,
                )
                self.assertTrue(result.is_error)
        with self.assertRaises(ValueError):
            list_tickets(status="")

    async def test_audits_exactly_one_query_per_returned_ticket(self) -> None:
        tickets = await self.call_tool()

        with sqlite3.connect(self.db_path) as connection:
            events = connection.execute(
                """
                SELECT ticket_id, action
                FROM ticket_history
                ORDER BY ticket_id
                """
            ).fetchall()
            ticket_values = connection.execute(
                "SELECT ticket_id, status, updated_at FROM tickets ORDER BY ticket_id"
            ).fetchall()

        self.assertEqual(events, [(101, "consulta"), (102, "consulta"), (103, "consulta"), (104, "consulta")])
        self.assertEqual(len(tickets), len(events))
        self.assertEqual(
            ticket_values,
            [
                (101, "aberto", "2025-02-01T09:00:00Z"),
                (102, "em_andamento", "2025-02-02T10:00:00Z"),
                (103, "resolvido", "2025-02-03T11:00:00Z"),
                (104, "fechado", "2025-02-04T12:00:00Z"),
            ],
        )

    async def test_empty_result_does_not_create_query_events(self) -> None:
        await self.call_tool(status="aberto")
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM ticket_history")
            connection.execute("DELETE FROM tickets")

        self.assertEqual(await self.call_tool(), [])
        with sqlite3.connect(self.db_path) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'consulta'"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    async def test_first_server_start_creates_database_and_initial_tickets(self) -> None:
        fresh_db_path = self.db_path.parent / "fresh" / "helpdesk.db"
        self.assertFalse(fresh_db_path.exists())
        server = create_server(fresh_db_path)

        async with Client(server) as client:
            result = await client.call_tool("listar_chamados")

        self.assertTrue(fresh_db_path.exists())
        self.assertEqual(
            [ticket["status"] for ticket in result.structured_content["result"]],
            ["aberto", "em_andamento", "resolvido", "fechado", "aberto"],
        )
        with sqlite3.connect(fresh_db_path) as connection:
            creation_events = connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'criacao'"
            ).fetchone()[0]
        self.assertEqual(creation_events, 5)

    async def test_initialization_preserves_changes_and_deleted_seed_tickets(self) -> None:
        seed_db_path = self.db_path.parent / "seed.db"
        initialize_database(seed_db_path)
        with sqlite3.connect(seed_db_path) as connection:
            initial_count = connection.execute(
                "SELECT COUNT(*) FROM tickets"
            ).fetchone()[0]
            initial_events = connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'criacao'"
            ).fetchone()[0]
        self.assertEqual(initial_count, 5)
        self.assertEqual(initial_events, 5)

        with sqlite3.connect(seed_db_path) as connection:
            connection.execute(
                "UPDATE tickets SET status = 'fechado' WHERE ticket_id = 1"
            )
            connection.execute("DELETE FROM tickets WHERE ticket_id = 2")

        initialize_database(seed_db_path)
        initialize_database(seed_db_path)

        with sqlite3.connect(seed_db_path) as connection:
            rows = connection.execute(
                "SELECT ticket_id, status FROM tickets ORDER BY ticket_id"
            ).fetchall()
            creation_events = connection.execute(
                "SELECT COUNT(*) FROM ticket_history WHERE action = 'criacao'"
            ).fetchone()[0]
        self.assertEqual(
            rows,
            [(1, "fechado"), (3, "resolvido"), (4, "fechado"), (5, "aberto")],
        )
        self.assertEqual(creation_events, 5)
