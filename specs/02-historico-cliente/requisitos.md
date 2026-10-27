# Requisitos — buscar histórico do cliente

## Contexto

Esta funcionalidade corresponde à fase 2 do [roadmap](../roadmap.md): expor a
tool MCP `buscar_historico_cliente` para consultar os chamados associados a um
cliente. Conforme a [missão](../missao.md) e a
[Constituição técnica](../pilha-tecnologia.md), “histórico do cliente” significa
os próprios chamados associados a `client_name`, não os eventos de auditoria
da tabela `ticket_history`.

## Comportamentos esperados

1. A tool `buscar_historico_cliente` recebe o nome do cliente e retorna todos
   os chamados cujo `client_name` corresponda exatamente ao texto informado.
   Não deve fazer busca parcial nem normalizar o nome: diferenças de caixa,
   espaços ou outros caracteres não são ignoradas.
2. Nomes de cliente repetidos são permitidos. A busca retorna todos os
   chamados com correspondência exata.
3. Os resultados são ordenados por `ticket_id` em ordem crescente e cada item
   contém os seis campos do modelo `tickets`.
4. Se não houver correspondências, retorna `[]`.
5. A consulta não altera nenhum campo nem exclui ou cria chamados.
6. Para cada chamado retornado, registra exatamente um evento `consulta` em
   `ticket_history`. Se não houver resultados, não registra evento `consulta`.
7. A tool deve estar disponível para chamada por clientes MCP compatíveis,
   usando o transporte `stdio` definido na Constituição técnica.

## Entrada

| Campo | Obrigatório | Regras |
|---|---|---|
| `client_name` | Sim | Texto usado sem alteração na comparação exata com `tickets.client_name`. Não remover espaços, alterar caixa ou aceitar correspondência parcial. |

O nome vazio, se fornecido, é comparado como texto vazio; não deve ser
interpretado como ausência do filtro. Campo ausente ou valor que não seja texto
deve ser rejeitado como entrada inválida, nunca convertido em uma busca sem
filtro.

## Saída

Uma lista de chamados, possivelmente vazia. Cada item contém exatamente os
campos do modelo `tickets`:

| Campo | Significado |
|---|---|
| `ticket_id` | Identificador único do chamado. |
| `client_name` | Nome fictício do cliente associado. |
| `description` | Descrição do problema ou solicitação. |
| `status` | Situação atual do chamado. |
| `created_at` | Data e hora de criação em UTC, em ISO 8601. |
| `updated_at` | Data e hora da última atualização em UTC, em ISO 8601. |

O resultado deve preservar os valores armazenados e ser ordenado por
`ticket_id` crescente. Nenhuma correspondência é representada por `[]`, sem
erro e sem evento `consulta`.

## Auditoria e efeitos

- Registrar um evento `consulta` para cada chamado efetivamente retornado,
  relacionando-o pelo respectivo `ticket_id`.
- Registrar exatamente um evento por chamado retornado nesta chamada; não
  registrar eventos para chamados não retornados.
- Não registrar eventos `consulta` quando a lista de resultados estiver
  vazia.
- A auditoria não autoriza mudanças nos chamados: os seis campos de cada
  registro devem permanecer inalterados pela consulta.
- Não confundir a resposta desta tool com os registros de
  `ticket_history`; a tabela é usada somente para a auditoria prevista na
  Constituição técnica.

## Erros

Campo `client_name` ausente ou entrada que não seja texto deve produzir erro
de validação explícito, não uma lista vazia nem a execução de uma consulta
mais ampla. Falhas de persistência não devem ser ocultadas como resultado
vazio.
