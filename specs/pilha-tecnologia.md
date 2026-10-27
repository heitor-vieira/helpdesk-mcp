# Constituição técnica

Este documento registra as decisões técnicas para a implementação inicial do
servidor Helpdesk MCP. A solução é local e demonstrativa, conforme os limites
descritos em [missao.md](./missao.md).

## Tecnologias e execução

- **Python:** implementar o servidor em Python e usar um ambiente virtual
  (`.venv`) para isolar as dependências. O README deve documentar a versão do
  Python utilizada e testada, a criação e ativação do ambiente virtual e a
  instalação das dependências.
- **Dependências:** manter as dependências externas documentadas em
  `requirements.txt`. A biblioteca `sqlite3` faz parte da biblioteca padrão
  do Python e não precisa ser instalada separadamente.
- **Servidor MCP:** usar a biblioteca `fastmcp` para implementar o servidor e
  expor as tools `listar_chamados`, `buscar_historico_cliente` e
  `atualizar_status`, conforme a ordem e o escopo do
  [roadmap](./roadmap.md).
- **Transporte:** executar localmente usando o transporte MCP `stdio`. Não
  escrever logs ou mensagens de diagnóstico em `stdout`, pois ele é usado
  pelo protocolo.

## Persistência e dados

Usar **SQLite** para persistir os chamados em um arquivo local ao projeto,
`data/helpdesk.db`. O banco deve ser criado automaticamente na inicialização,
incluindo as tabelas e registros fictícios iniciais quando ainda não existirem.
O esquema atual atende às fases de busca por cliente e atualização de status;
essas fases não exigem uma tabela `clients` nem uma migração de esquema.

O modelo inicial deve conter:

### `tickets`

| Campo | Finalidade |
|---|---|
| `ticket_id` (`INTEGER`) | Identificador único do chamado e chave primária. |
| `client_name` (`TEXT`) | Nome fictício do cliente associado ao chamado. |
| `description` (`TEXT`) | Descrição do problema ou solicitação. |
| `status` (`TEXT`) | Situação atual do chamado. |
| `created_at` (`TEXT`) | Data e hora de criação em UTC, no formato ISO 8601. |
| `updated_at` (`TEXT`) | Data e hora da última atualização em UTC, no formato ISO 8601. |

Todos os campos de `tickets` são obrigatórios.

Os valores de status permitidos são `aberto`, `em_andamento`, `resolvido` e
`fechado`. A implementação deve rejeitar estados fora dessa lista.
Não há uma matriz de transições nesta versão: qualquer status permitido pode
ser definido a partir de qualquer status atual.

A busca de histórico por cliente consulta os chamados associados ao
`client_name`; ela não representa a consulta dos eventos de auditoria da
tabela `ticket_history`. A atualização prevista no escopo inicial altera o
somente o `status` e o `updated_at` da linha do chamado existente. Não há uma
matriz de transições: qualquer status permitido pode suceder qualquer outro
status permitido.

Como não há uma entidade separada de cliente, a busca por cliente deve usar
correspondência exata do texto de `client_name`, sem correspondência parcial.
Nomes repetidos são permitidos e a busca retorna todos os chamados com o nome
correspondente. A busca não cria, altera ou exclui dados.

### `ticket_history`

| Campo | Finalidade |
|---|---|
| `event_id` (`INTEGER`) | Identificador único do evento e chave primária. |
| `ticket_id` (`INTEGER`) | Chamado relacionado e chave estrangeira para `tickets`. |
| `action` (`TEXT`) | Tipo de evento: `consulta`, `atualizacao` ou `criacao`. |
| `occurred_at` (`TEXT`) | Data e hora do evento em UTC, no formato ISO 8601. |
| `details` (`TEXT`, opcional) | Detalhes do evento; em atualizações, informar os campos alterados e seus valores anterior e novo. |

Todos os campos de `ticket_history`, exceto `details`, são obrigatórios.

Registrar no histórico a criação dos chamados, as consultas que retornem
chamados e cada atualização realizada. Em consultas que retornem vários
chamados, registrar um evento por chamado retornado. Uma atualização deve
acrescentar um evento `atualizacao` ao histórico, preservando todos os eventos
anteriores. Para operações normais, `ticket_history` é append-only: eventos
existentes nunca são atualizados nem apagados. Como não há autenticação real,
o histórico não deve presumir uma identidade de usuário.

Uma atualização efetiva de status e seu evento `atualizacao` devem ser
persistidos na mesma transação: ou ambos são confirmados, ou nenhum deles é.
O evento deve identificar em `details`, como texto legível, o status anterior
e o novo, e registrar o horário em UTC. Se o chamado solicitado não existir,
a operação deve informar erro explícito, sem alterar dados nem registrar
evento. Se o status solicitado já for o atual, a operação é sem alteração:
não modifica `updated_at`, não registra evento de atualização e retorna o
registro atual do chamado.

Para manter o exemplo simples, `client_name` fica diretamente no chamado,
sem uma tabela separada de clientes. `details` é texto legível, sem exigir um
formato de eventos ou payload JSON mais elaborado.

## Inicialização do banco

- Criar as tabelas com operações idempotentes, como `CREATE TABLE IF NOT
  EXISTS`, e habilitar a integridade das chaves estrangeiras.
- Usar identificadores estáveis para os registros fictícios e inseri-los sem
  sobrescrever dados existentes. Reiniciar o servidor não deve recriar,
  duplicar ou restaurar por cima de chamados já alterados.
- Criar o diretório do banco se necessário. O banco e os registros de exemplo
  devem ser preparados automaticamente, sem etapa manual de migração para a
  primeira execução.
