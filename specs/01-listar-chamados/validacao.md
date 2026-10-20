# Validação — listar chamados

Os testes devem usar uma base isolada e dados controlados, para que os
resultados não dependam de alterações feitas durante outras execuções. Além
dos testes automatizados, a tool deve ser chamada por um cliente MCP
compatível para confirmar a entrada e a resposta expostas.

## Cenários de aceitação

| Cenário | Ação | Resultado esperado |
|---|---|---|
| Listagem sem filtro | Criar vários chamados com status diferentes e chamar `listar_chamados` sem `status`. | Retorna todos os chamados uma vez, com os seis campos obrigatórios e valores correspondentes ao banco. |
| Filtro por status | Chamar a tool separadamente com `aberto`, `em_andamento`, `resolvido` e `fechado`. | Cada resposta contém somente chamados com o status solicitado. |
| Status sem correspondências | Consultar com um status permitido para o qual não exista chamado. | Retorna `[]`, sem erro e sem eventos `consulta`. |
| Banco sem chamados | Chamar sem filtro em uma base válida sem registros de chamados. | Retorna `[]`. |
| Status inválido | Consultar com valor como `pendente` ou string vazia. | Rejeita a entrada com erro de validação; não faz uma busca sem filtro e não retorna sucesso vazio. |
| Auditoria da listagem | Consultar chamados que retornem resultados e inspecionar `ticket_history`. | Existe exatamente um evento `consulta` para cada chamado retornado; não há eventos adicionais por uma única resposta. |
| Primeira inicialização | Iniciar o servidor sem diretório ou banco previamente criado. | Diretório, banco, tabelas e registros fictícios são criados automaticamente; a tool pode listar os registros. |
| Inicialização repetida | Reiniciar o servidor e listar novamente. | Não há duplicação de dados fictícios nem restauração de valores sobre dados existentes ou alterados. |

## Verificações técnicas

- Confirmar que os valores persistidos de status respeitam o conjunto definido
  na [pilha tecnológica](../pilha-tecnologia.md).
- Confirmar que `created_at` e `updated_at` são devolvidos em UTC e no formato
  ISO 8601.
- Confirmar que a resposta da tool MCP é uma lista de chamados e que a lista
  vazia é representada como `[]`.
- Confirmar que consultas e inicializações não emitem mensagens de diagnóstico
  em `stdout`, reservado ao transporte MCP `stdio`.

## Critério de conclusão

A funcionalidade atende aos requisitos quando todos os cenários de aceitação
passam, os status inválidos são rejeitados e a tool está acessível via MCP com
a mesma semântica descrita em [requisitos.md](./requisitos.md).
