# Planejamento — buscar histórico do cliente

As tarefas abaixo detalham a fase 2 do [roadmap](../roadmap.md). A
implementação deve reutilizar o banco e o modelo existentes, sem criar tabela
de clientes nem alterar o esquema.

1. **Implementar a consulta por cliente**
   - Receber `client_name` como texto obrigatório.
   - Consultar `tickets` por correspondência exata de `client_name`, sem
     remover espaços, alterar caixa ou aplicar busca parcial.
   - Selecionar os seis campos do modelo e ordenar por `ticket_id` crescente.
   - Retornar uma lista vazia quando não houver correspondências.
2. **Registrar a auditoria da consulta**
   - Gravar exatamente um evento `consulta` em `ticket_history` para cada
     chamado retornado.
   - Não gravar eventos quando a busca não retornar chamados.
   - Preservar todos os registros e valores da tabela `tickets`.
3. **Expor a tool MCP**
   - Registrar `buscar_historico_cliente` no servidor `FastMCP`.
   - Conectar o argumento obrigatório e a resposta da tool à consulta
     implementada, preservando a validação de entrada.
   - Manter o transporte `stdio` e não escrever diagnósticos em `stdout`.
4. **Validar a funcionalidade e a regressão**
   - Cobrir correspondência exata, múltiplos chamados, ordenação, lista vazia,
     efeitos nos dados, auditoria, validação de entrada e chamada por cliente
     MCP.
   - Executar também os testes da fase 1 para confirmar que `listar_chamados`
     mantém seu comportamento.
