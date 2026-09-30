# Simulado — Banking System (estilo CodeSignal ICA / "Filesystem with Unit Tests")

Mesmo formato do teste real do Nubank: **1 questão, 4 níveis progressivos**, cada
nível reaproveita e estende o código do anterior. Implemente **tudo em
`banking_system/banking_system_impl.py`**. Não altere os arquivos de teste nem as
assinaturas dos métodos em `banking_system.py`.

Todos os valores são inteiros não-negativos. `timestamp` é estritamente crescente:
cada chamada recebe um timestamp maior que o de qualquer chamada anterior. Saldo
inicial de toda conta é 0.

## Como rodar

```bash
bash run_tests.sh                                  # todos os níveis
bash run_single_test.sh "test_level_1_case_01_create_account"   # um caso
```

(Requer Python 3.10+ por causa do type hint `int | None`.)

---

## Level 1 — Contas básicas

- `create_account(timestamp, account_id) -> bool`
  Cria a conta com saldo 0. Retorna `True` se criou, ou `False` se já existe uma
  conta com esse `account_id`.
- `deposit(timestamp, account_id, amount) -> int | None`
  Deposita e retorna o novo saldo. Retorna `None` se a conta não existe.
- `pay(timestamp, account_id, amount) -> int | None`
  Saca `amount` (pagamento) e retorna o novo saldo. Retorna `None` se a conta não
  existe **ou** não tem saldo suficiente (nesse caso o saldo não muda).

## Level 2 — Ranking de gastos

- `top_spenders(timestamp, n) -> list[str]`
  Retorna os `n` account_ids que mais gastaram (soma de `pay` + transferências de
  saída), em ordem **decrescente** de valor gasto. Empate → ordem **alfabética
  crescente** do id. Formato de cada item: `"<account_id>(<total_gasto>)"`. Se há
  menos de `n` contas, retorna todas.

## Level 3 — Transferências e pagamentos agendados

- `transfer(timestamp, source_id, target_id, amount) -> int | None`
  Transfere e retorna o saldo do `source` após a operação. Retorna `None` se
  algum dos dois não existe, se `source_id == target_id`, ou se falta saldo.
  Transferência de saída conta como gasto (para o `top_spenders`).
- `schedule_payment(timestamp, account_id, amount, delay) -> str | None`
  Agenda um pagamento de `amount` para o instante `timestamp + delay`. Retorna um
  id único `"payment<N>"` (N começa em 1 e cresce global, entre todas as contas),
  ou `None` se a conta não existe.
  Pagamentos vencidos (due <= timestamp atual) são processados **no início de toda
  chamada seguinte**, na ordem (instante de vencimento, depois ordem de criação).
  Um agendamento vencido só executa se houver saldo; senão é descartado sem mudar
  o saldo. Agendamento executado conta como gasto.
- `cancel_payment(timestamp, account_id, payment_id) -> bool`
  Cancela o agendamento se ainda estiver pendente. `False` se não existe, não
  pertence à conta, ou já foi executado/cancelado.

## Level 4 — Fusão de contas e saldo histórico

- `merge_accounts(timestamp, account_id_1, account_id_2) -> bool`
  Funde a conta 2 na conta 1: soma saldos, soma o total gasto, reatribui os
  agendamentos pendentes da conta 2 para a conta 1, e remove a conta 2.
  `False` se alguma não existe ou se `account_id_1 == account_id_2`.
- `get_balance(timestamp, account_id, time_at) -> int | None`
  Retorna o saldo da conta como estava em `time_at` (considerando toda operação
  com timestamp <= time_at). `None` se a conta não existia em `time_at`. Se a
  conta foi fundida em outra, o saldo continua consultável para qualquer
  `time_at` **estritamente antes** da fusão.

---

## Dicas (valem pro teste real)

1. **Leia os 4 níveis antes de codar.** Modele a conta como uma classe já
   prevendo o que vem depois (gasto acumulado, histórico de saldo, agendamentos).
   Refatorar do zero no Level 3/4 é o que faz a maioria estourar o tempo.
2. **Submeta cada nível assim que passar**, antes de mexer no próximo. O
   CodeSignal pontua o último *submit*, não o último código na tela.
3. Encapsule em classes (`Account`, `Payment`) em vez de dicts soltos — Level 3 e 4
   ficam bem mais fáceis.

Solução de referência em `solucao_referencia/` — só olhe depois de tentar.
