# Requisitos — listar chamados

## Contexto

Esta funcionalidade corresponde à primeira fase do [roadmap](../roadmap.md):
expor a tool MCP `listar_chamados` para consultar os chamados fictícios
persistidos em `data/helpdesk.db`. Ela respeita a [missão](../missao.md) do
servidor, que limita o exemplo à gestão local de chamados, e a
[pilha tecnológica](../pilha-tecnologia.md), que define SQLite e o modelo
inicial de dados.

## Comportamentos esperados

1. A tool `listar_chamados` retorna os chamados existentes.
2. A tool aceita um filtro opcional por status:
   - sem filtro, retorna todos os chamados;
   - com filtro, retorna somente os chamados cujo status corresponda ao
     informado.
3. Os únicos status aceitos são `aberto`, `em_andamento`, `resolvido` e
   `fechado`. Um status diferente desses deve ser rejeitado, não tratado como
   uma busca válida sem resultados.
4. Se nenhum chamado corresponder à consulta, o resultado é uma lista vazia.
   Isso vale tanto para um banco sem chamados quanto para um filtro válido sem
   correspondências.
5. A consulta não altera os chamados.
6. Conforme a pilha tecnológica, registrar na tabela `ticket_history` um evento
   `consulta` para cada chamado retornado. Uma consulta sem resultados não gera
   eventos de consulta.
7. A consulta de listagem não deve ser confundida com a busca de chamados por
   cliente nem com a leitura dos eventos de auditoria.

## Entrada

| Campo | Obrigatório | Regras |
|---|---|---|
| `status` | Não | Se informado, deve ser exatamente um dos valores `aberto`, `em_andamento`, `resolvido` ou `fechado`. Se omitido, não restringe a consulta. |

Não há outros filtros nesta fase.

## Saída

Uma lista de chamados, possivelmente vazia. Cada item contém todos os campos
obrigatórios do modelo `tickets`:

| Campo | Significado |
|---|---|
| `ticket_id` | Identificador único do chamado. |
| `client_name` | Nome fictício do cliente associado. |
| `description` | Descrição do problema ou solicitação. |
| `status` | Situação atual do chamado. |
| `created_at` | Data e hora de criação em UTC, em ISO 8601. |
| `updated_at` | Data e hora da última atualização em UTC, em ISO 8601. |

Para status válido sem correspondências, retornar `[]`; não retornar erro nem
um resultado que pareça conter chamados. Para status inválido, informar erro
de validação de entrada.

## Casos relevantes

- Chamada sem `status`, com vários chamados no banco: retorna todos.
- Chamada com cada um dos quatro status permitidos: retorna apenas os
  chamados daquele status.
- Chamada com status válido sem correspondências: retorna `[]`.
- Chamada em banco sem chamados: retorna `[]`.
- Chamada com status fora da lista permitida: rejeita a entrada.
- Chamados retornados: preservar os valores armazenados e registrar exatamente
  um evento `consulta` por chamado retornado.
- Reinicialização do servidor: não duplicar nem restaurar por cima dos dados
  fictícios existentes, inclusive chamados já alterados.

## Inicialização dos dados fictícios

Na primeira inicialização, o servidor cria automaticamente o diretório do
banco, as tabelas necessárias e os registros fictícios iniciais, sem exigir
uma etapa manual. A criação deve ser idempotente: inicializações posteriores
não podem duplicar registros, substituir alterações existentes ou recriar
chamados removidos. Os dados são fictícios e destinados apenas à demonstração
local.
