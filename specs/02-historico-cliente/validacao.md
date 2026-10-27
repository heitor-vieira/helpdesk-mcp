# Validação — buscar histórico do cliente

Os testes automatizados devem usar bancos SQLite temporários e dados
controlados, sem depender do conteúdo de `data/helpdesk.db` nem de execuções
anteriores. A tool também deve ser chamada por um cliente MCP compatível para
confirmar o contrato realmente exposto pelo servidor.

## Cenários de aceitação

| Cenário | Ação | Resultado esperado |
|---|---|---|
| Correspondência exata | Criar chamados para `Ana Souza` e consultar por `Ana Souza`. | Retorna somente chamados cujo `client_name` é exatamente `Ana Souza`. |
| Nome repetido | Criar dois ou mais chamados com o mesmo `client_name` e consultar pelo nome. | Retorna todos os chamados correspondentes, uma única vez cada. |
| Correspondência não parcial | Consultar usando apenas parte de um nome existente. | Não retorna o chamado cujo nome completo não seja igual ao argumento. |
| Diferenças no texto | Consultar usando variação de caixa, espaços adicionais ou outro texto diferente do armazenado. | Não retorna chamados que não tenham igualdade exata; o argumento não é normalizado. |
| Ordenação e formato | Preparar chamados correspondentes com `ticket_id` fora de ordem de inserção e consultar. | Retorna os chamados em ordem crescente de `ticket_id`; cada item contém os seis campos `ticket_id`, `client_name`, `description`, `status`, `created_at` e `updated_at`, com valores iguais aos persistidos. |
| Sem correspondências | Consultar um nome que não exista no banco. | Retorna `[]`, sem erro e sem evento `consulta`. |
| Nome vazio | Consultar com `client_name` igual a texto vazio. | Trata o valor como texto fornecido e faz a comparação exata; não executa uma busca sem filtro. |
| Entrada inválida | Chamar sem `client_name` ou fornecer valor que não seja texto. | Rejeita a entrada com erro de validação; não converte a chamada em resultado vazio ou busca geral. |
| Chamados inalterados | Capturar os seis campos dos chamados antes e depois de uma consulta que retorna resultados. | Todos os chamados mantêm os mesmos valores; nenhum registro de `tickets` é criado, atualizado ou excluído. |
| Auditoria com resultados | Consultar vários chamados correspondentes e inspecionar `ticket_history`. | É registrado exatamente um evento `consulta` para cada `ticket_id` retornado e nenhum evento adicional para essa chamada. |
| Auditoria sem resultados | Consultar nome sem correspondências e comparar os eventos antes e depois. | Não é inserido nenhum evento `consulta`. |
| Chamada MCP | Conectar um cliente MCP ao servidor e invocar `buscar_historico_cliente` com um nome válido. | A tool está listada e invocável, recebe o argumento `client_name` e retorna a lista no formato especificado. |

## Regressão

- Executar a suíte existente da fase 1 junto com os novos testes.
- Confirmar que `listar_chamados` mantém a listagem sem filtro, os filtros
  válidos por status, a rejeição de status inválido, a ordenação e a auditoria
  por chamado retornado.
- Confirmar que o uso da nova tool não altera resultados ou dados necessários
  aos testes de `listar_chamados`.
- Confirmar que o cliente MCP continua usando `stdio` sem mensagens de
  diagnóstico em `stdout`.

## Critério de conclusão

A fase atende a esta especificação quando todos os cenários de aceitação e de
regressão passam, a tool está efetivamente acessível via MCP e cada chamada
observa a correspondência exata, a ordenação, a ausência de mutação de
chamados e as regras de auditoria definidas em
[requisitos.md](./requisitos.md).
