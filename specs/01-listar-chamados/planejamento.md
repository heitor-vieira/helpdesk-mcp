# Planejamento — listar chamados

As tarefas abaixo são pequenas e estão ordenadas pelas dependências da
funcionalidade.

1. **Preparar persistência e dados iniciais**
   - Criar o diretório e o banco SQLite automaticamente.
   - Criar as tabelas necessárias de forma idempotente e habilitar chaves
     estrangeiras.
   - Inserir chamados fictícios com identificadores estáveis sem sobrescrever
     dados existentes.
2. **Implementar a consulta de chamados**
   - Consultar todos os chamados quando não houver filtro.
   - Aplicar o filtro opcional por status.
   - Rejeitar status fora de `aberto`, `em_andamento`, `resolvido` e `fechado`.
   - Retornar `[]` quando não houver correspondências.
3. **Expor a tool MCP `listar_chamados`**
   - Conectar a entrada e a saída da tool à consulta implementada.
   - Preservar os campos do modelo de chamados na resposta.
4. **Registrar eventos de consulta**
   - Registrar um evento `consulta` por chamado efetivamente retornado.
   - Não registrar eventos quando a consulta não retornar chamados.
5. **Validar os requisitos**
   - Verificar filtros, resultado vazio, validação de status, formato da saída,
     auditoria e comportamento de inicialização/reinicialização.
   - Ajustar a documentação de execução ou uso se a implementação exigir
     instruções adicionais.
