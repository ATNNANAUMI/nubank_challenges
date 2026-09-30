# Live Case 2 — PIX Authorizer (Autorizador de PIX)

## Context

You're building the service that approves or rejects PIX operations and keeps
account balances up to date. The app, the fraud team and the customer's
statement all trust the decisions your code makes.

All money is **integers in cents** (R$ 1.000,00 = `100000`). Never use floats.

---

## How to run this rehearsal

Some rules below are **deliberately incomplete**, like in the real live case.

1. **Stage 1 — no code (35–40 min).** Read this file twice. Write the rules in
   your own words, list the edge cases you see, and write down your questions.
2. **Ask.** A friend (or Claude) plays interviewer and answers from
   `CLARIFICATIONS.md`. Practicing alone? Open it only after your question
   list is written.
3. **Stage 2 — code (45–50 min).** Timer running, thinking out loud.
4. Run the tests.

Don't open `test_pix_authorizer.py` before step 2 — the test names give the
answers away.

---

## API

Implement the `PixAuthorizer` class in `pix_authorizer.py`.

- Every method receives a `timestamp` first, in local time, like
  `"2026-10-05T21:30:00"`. Calls always arrive in time order.
  (`datetime.fromisoformat` parses it.)
- Operations return a result like:

```python
{"status": "approved", "violations": []}
{"status": "rejected", "violations": ["insufficient-balance"]}
```

| Method | Returns | Part |
|---|---|---|
| `create_account(timestamp, account_id, balance)` | result | 1 |
| `register_key(timestamp, account_id, key)` | result | 1 |
| `get_balance(timestamp, account_id)` | `int`, or `None` if the account doesn't exist | 1 |
| `transfer(timestamp, transfer_id, from_account, to_key, amount)` | result | 1 |
| `schedule_transfer(timestamp, transfer_id, from_account, to_key, amount, execute_at)` | result — status `"scheduled"` when accepted | 5 |
| `cancel_scheduled(timestamp, transfer_id)` | result | 5 |
| `get_transfer_status(timestamp, transfer_id)` | `{"status": ..., "violations": [...]}`, or `None` | 5 |

---

## Business rules

**Accounts.** An account has an id and a starting balance.

**PIX keys.** Money is always sent to a PIX key, never straight to an account.
A key can be a CPF, an e-mail, a phone number or a random key. Each key
belongs to exactly one account, and an account can have at most 5 keys.

**Transfers.** A transfer moves money from the sender to the account that owns
the key. The sender needs enough balance, and can't send money to themselves.

**Night limit.** At night (20h to 6h), an account can send at most R$ 1.000,00.

**Hourly limit.** An account can't send more than R$ 5.000,00 in an hour.

**Double-tap protection.** The same transfer sent twice within a minute — same
sender, same recipient, same amount — is blocked.

**Scheduled PIX (Pix Agendado).** A customer can schedule a transfer for a
future time, and it runs when that time comes. A pending one can be canceled.

---

## Violations

| Operation | Violation | When |
|---|---|---|
| `create_account` | `account-already-exists` | the id is taken |
| | `invalid-amount` | negative starting balance |
| `register_key` | `account-not-found` | unknown account |
| | `invalid-key` | not a valid CPF, e-mail, phone or random key |
| | `key-already-registered` | the key is taken |
| | `key-limit-reached` | the account already has 5 keys |
| `transfer` | `invalid-amount` | amount is zero or negative |
| | `account-not-found` | unknown sender |
| | `key-not-found` | no account owns the key |
| | `same-account` | sending to yourself |
| | `insufficient-balance` | not enough money |
| | `night-limit-exceeded` | night limit |
| | `hourly-limit-exceeded` | hourly limit |
| | `duplicate-transfer` | double-tap |
| `schedule_transfer` | `invalid-amount`, `account-not-found`, `key-not-found` | same as `transfer` |
| | `invalid-schedule` | bad execution time |
| `cancel_scheduled` | `transfer-not-found` | unknown id |
| | `not-cancelable` | can't be canceled |

---

## Parts

Build in order. A clean Part 3 beats a half-broken Part 5.

| Part | What | Level |
|---|---|---|
| 1 | Accounts, keys, basic transfers | warm-up |
| 2 | Key formats and the 5-key limit | core |
| 3 | Night limit | core |
| 4 | Hourly limit and double-tap protection | stretch |
| 5 | Scheduled PIX | hard |

Target: Parts 1–3 in about 45 minutes.

---

## Running the tests

```bash
cd live_case_2
python -m unittest -v                                        # everything
python -m unittest -v test_pix_authorizer.TestPart1Basics    # one part
```

Test classes: `TestPart1Basics`, `TestPart2Keys`, `TestPart3NightLimit`,
`TestPart4FraudRules`, `TestPart5ScheduledPix`.
