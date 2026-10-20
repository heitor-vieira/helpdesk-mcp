# Roadmap

O desenvolvimento será dividido em três fases pequenas e sequenciais. Cada
fase será detalhada e implementada individualmente quando chegar sua vez.

## Fase 1 — Listar chamados

- **Tool:** `listar_chamados`, com filtro opcional por status.
- **Objetivo:** permitir consultar os chamados existentes, com a opção de
  restringir a lista a um status.
- **Critério geral de conclusão:** a tool lista os chamados e, quando
  informada, aplica corretamente o filtro por status.

## Fase 2 — Buscar histórico de cliente

- **Tool:** `buscar_historico_cliente`.
- **Objetivo:** consultar o histórico de chamados associado a um cliente; aqui,
  “histórico” significa os chamados desse cliente, não os eventos internos de
  auditoria.
- **Critério geral de conclusão:** a tool retorna os chamados correspondentes
  ao cliente informado.

## Fase 3 — Atualizar status

- **Tool:** `atualizar_status`.
- **Objetivo:** alterar o status de um chamado existente.
- **Critério geral de conclusão:** a tool atualiza o status do chamado
  identificado e permite confirmar o novo status.
