from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = ("aberto", "em_andamento", "resolvido", "fechado")
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "helpdesk.db"

_INITIAL_TICKETS = (
    (
        1,
        "Ana Souza",
        "Não consigo acessar o sistema de folha de pagamento.",
        "aberto",
        "2025-01-10T09:00:00Z",
        "2025-01-10T09:00:00Z",
    ),
    (
        2,
        "Bruno Lima",
        "Solicitação de instalação do editor de texto.",
        "em_andamento",
        "2025-01-11T10:30:00Z",
        "2025-01-12T14:15:00Z",
    ),
    (
        3,
        "Carla Mendes",
        "A impressora do departamento está apresentando falhas.",
        "resolvido",
        "2025-01-08T08:45:00Z",
        "2025-01-09T16:20:00Z",
    ),
    (
        4,
        "Diego Costa",
        "Pedido de acesso ao compartilhamento da equipe.",
        "fechado",
        "2025-01-07T11:00:00Z",
        "2025-01-10T17:30:00Z",
    ),
    (
        5,
        "Ana Souza",
        "O monitor da estação de trabalho está piscando.",
        "aberto",
        "2025-01-13T13:10:00Z",
        "2025-01-13T13:10:00Z",
    ),
)


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY,
                client_name TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('aberto', 'em_andamento', 'resolvido', 'fechado')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ticket_history (
                event_id INTEGER PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(ticket_id),
                action TEXT NOT NULL
                    CHECK (action IN ('consulta', 'atualizacao', 'criacao')),
                occurred_at TEXT NOT NULL,
                details TEXT
            );

            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        initialized = connection.execute(
            "SELECT 1 FROM schema_metadata WHERE key = 'initial_tickets_seeded'"
        ).fetchone()
        if initialized is None:
            for ticket in _INITIAL_TICKETS:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO tickets (
                        ticket_id, client_name, description, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ticket,
                )
                if cursor.rowcount:
                    connection.execute(
                        """
                        INSERT INTO ticket_history (ticket_id, action, occurred_at, details)
                        VALUES (?, 'criacao', ?, 'Chamado fictício inicial')
                        """,
                        (ticket[0], _utc_now()),
                    )
            connection.execute(
                "INSERT INTO schema_metadata (key, value) VALUES (?, ?)",
                ("initial_tickets_seeded", "true"),
            )


def list_tickets(
    status: str | None = None, db_path: Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    if status is not None and status not in VALID_STATUSES:
        allowed = ", ".join(VALID_STATUSES)
        raise ValueError(f"Status inválido: {status!r}. Valores aceitos: {allowed}.")

    with _connect(Path(db_path)) as connection:
        if status is None:
            rows = connection.execute(
                """
                SELECT ticket_id, client_name, description, status, created_at, updated_at
                FROM tickets
                ORDER BY ticket_id
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT ticket_id, client_name, description, status, created_at, updated_at
                FROM tickets
                WHERE status = ?
                ORDER BY ticket_id
                """,
                (status,),
            ).fetchall()

        occurred_at = _utc_now()
        connection.executemany(
            """
            INSERT INTO ticket_history (ticket_id, action, occurred_at)
            VALUES (?, 'consulta', ?)
            """,
            ((row["ticket_id"], occurred_at) for row in rows),
        )
        return [dict(row) for row in rows]


def find_tickets_by_client(
    client_name: str, db_path: Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    with _connect(Path(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT ticket_id, client_name, description, status, created_at, updated_at
            FROM tickets
            WHERE client_name = ?
            ORDER BY ticket_id
            """,
            (client_name,),
        ).fetchall()

        occurred_at = _utc_now()
        connection.executemany(
            """
            INSERT INTO ticket_history (ticket_id, action, occurred_at)
            VALUES (?, 'consulta', ?)
            """,
            ((row["ticket_id"], occurred_at) for row in rows),
        )
        return [dict(row) for row in rows]
