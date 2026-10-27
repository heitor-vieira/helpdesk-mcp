# Roadmap

O desenvolvimento está dividido em três fases sequenciais. Cada fase deve ter
requisitos e cenários de validação detalhados antes de sua implementação.
Decisões que se aplicam a mais de uma fase ficam na [missão](./missao.md) ou na
[pilha de tecnologia](./pilha-tecnologia.md), não apenas neste roadmap.

## Fase 1 — Listar chamados — concluída

- **Tool:** `listar_chamados`, com filtro opcional por status.
- **Objetivo:** consultar os chamados existentes, com a opção de restringir a
  lista a um status permitido.
- **Critérios atendidos:** lista todos os chamados sem filtro; filtra por cada
  status permitido; rejeita status inválido; retorna lista vazia quando não há
  correspondências; registra um evento de consulta por chamado retornado.
- **Validação:** os oito testes automatizados passam. A tool foi chamada por um
  cliente MCP e os resultados foram comparados com SQLite e com
  [validacao.md](./01-listar-chamados/validacao.md).

## Fase 2 — Buscar chamados por cliente — concluída

- **Tool:** `buscar_historico_cliente`.
- **Objetivo:** consultar os chamados associados ao nome de cliente informado.
  “Histórico” significa os próprios chamados, não os eventos de
  `ticket_history`.
- **Critérios de conclusão:**
  - usar correspondência exata de `client_name`, sem busca parcial;
  - retornar todos os chamados correspondentes, ordenados por `ticket_id`, com
    os seis campos do modelo `tickets`;
  - retornar `[]` se não houver correspondências;
  - registrar exatamente um evento `consulta` por chamado retornado e nenhum
    evento quando o resultado estiver vazio;
  - não alterar os chamados.
- **Validação:** os seis testes da fase 2 e os oito testes de regressão da
  fase 1 passam. A tool foi chamada por MCP `stdio`: `Ana Souza` retornou os
  chamados 1 e 5, conferidos contra SQLite; `Cliente inexistente` retornou
  `[]`. Os requisitos e demais cenários estão em
  [validacao.md](./02-historico-cliente/validacao.md).

## Fase 3 — Atualizar status

- **Tool:** `atualizar_status`.
- **Objetivo:** alterar o status de um chamado existente para um valor
  permitido.
- **Critérios de conclusão:**
  - validar o identificador do chamado e aceitar somente os status definidos
    na [pilha de tecnologia](./pilha-tecnologia.md); não aplicar matriz de
    transição, permitindo qualquer status válido a partir de qualquer status
    atual;
  - informar erro explícito para status inválido ou chamado inexistente; no
    caso de chamado inexistente, não alterar dados nem registrar evento;
  - em uma atualização efetiva, alterar somente `status` e `updated_at` na
    linha de `tickets`, acrescentar um evento `atualizacao` a
    `ticket_history` sem atualizar ou apagar eventos anteriores e retornar o
    chamado atualizado;
  - registrar em `details`, como texto legível, os valores anterior e novo do
    status;
  - persistir a alteração e seu evento de auditoria atomicamente;
  - se o status solicitado já for o atual, tratar a operação como sem
    alteração: manter `updated_at`, não criar evento e retornar o registro
    atual.
- **Preparação:** detalhar entrada, saída, erros e cenários de validação em
  especificações próprias antes de implementar a tool.
