# Clarifications — the interviewer's answers

For whoever plays interviewer (a friend, or Claude).
**Candidate: don't read this before your question list is written.**

How to use it:

- Answer only what's asked. Don't volunteer rules. If a question never comes
  up, the tests will show it later — just like rework in the real case.
- Asked something that isn't here? Make a reasonable call and say it out loud.

---

## General

**All violations, or only the first one? In what order?**
Two phases:

- *Input checks* — bad amounts, unknown accounts or keys, bad key format, bad
  schedule time. Stop at the first one that fails and return only that one.
- *Business rules* — everything else. Check them all and return every one that
  fails, in the order of the README table.

| Operation | Input checks (first failure only) | Business rules (all failures) |
|---|---|---|
| `create_account` | `account-already-exists`, `invalid-amount` | — |
| `register_key` | `account-not-found`, `invalid-key` | `key-already-registered`, `key-limit-reached` |
| `transfer` | `invalid-amount`, `account-not-found`, `key-not-found` | `same-account`, `insufficient-balance`, `night-limit-exceeded`, `hourly-limit-exceeded`, `duplicate-transfer` |
| `schedule_transfer` | `invalid-amount`, `account-not-found`, `key-not-found`, `invalid-schedule` | — |
| `cancel_scheduled` | `transfer-not-found`, `not-cancelable` | — |

**Does a rejected operation change anything?**
No. A rejected transfer moves no money and never counts toward any limit or
duplicate check.

**What if a transfer lands exactly on a limit?**
Allowed. Only going *over* a limit is rejected.

**Can the starting balance be 0?** Yes. Negative → `invalid-amount`.

**Things you can assume:** timestamps never go backwards, ids are unique,
there are no deposits or withdrawals, and keys are never deleted.

---

## Part 1 — Accounts and transfers

**Can someone send their whole balance?** Yes. The balance becomes 0.

**What if the key belongs to the sender?** `same-account`.

---

## Part 2 — Keys

**How do I know a key's type?** From its shape, checked in this order:

1. contains `@` → e-mail
2. starts with `+` → phone
3. looks like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (hex digits) → random key
4. anything else → CPF

**What's a valid key?**

| Type | Valid when | Stored as |
|---|---|---|
| E-mail | exactly one `@`, something before it, and the part after it contains a `.` but doesn't start or end with one | lowercase |
| Phone | `+55` followed by exactly 11 digits | as given |
| Random | 8-4-4-4-12 hex digits (`0-9`, `a-f`), upper or lower case | lowercase |
| CPF | after removing every `.` and `-`, exactly 11 digits | the 11 digits |

**Is `Ana@Nubank.com` the same key as `ana@nubank.com`?** Yes. E-mails and
random keys are case-insensitive.

**Is `123.456.789-09` the same key as `12345678909`?** Yes.

**Should I validate the CPF check digits?** No. 11 digits is enough.

**Transfer to a key with a bad format?** `key-not-found` — it can't be
registered, so it can't be found.

**Registering a key the account already owns?** `key-already-registered`.

**Is the 5-key limit per type?** No, 5 keys in total.

---

## Part 3 — Night limit

**R$ 1.000,00 per transfer, or in total?** In total, for that night.

**Exact boundaries?** 20:00:00 is night. 06:00:00 is day.
(Night = hour ≥ 20 or hour < 6.)

**Tuesday 01:00 — which night is that?** The one that started Monday 20:00.
A night runs from 20:00 until 06:00 the next day.

**Do daytime transfers count toward the night?** No. Only transfers made
during that same night.

**Per account or per key?** Per sending account.

---

## Part 4 — Hourly limit and double-tap

**"An hour" — the clock hour (10:00–10:59) or rolling?** Rolling: the 60
minutes before the transfer. A transfer exactly 60 minutes older no longer
counts.

**"Same recipient" — same key or same account?** Same receiving account.
Sending to Bruno's CPF and then to Bruno's e-mail is still a duplicate.

**"Within a minute" — what about exactly 60 seconds?** Less than 60 seconds
apart is a duplicate. Exactly 60 seconds is fine.

**Compare against rejected transfers too?** No, only approved ones.

---

## Part 5 — Scheduled PIX

**There's no clock. When does a scheduled transfer actually run?**
Before handling any operation with timestamp T — any method, even
`get_balance` — run every pending scheduled transfer whose `execute_at` ≤ T.
Then handle the operation.

**What's checked when scheduling, and what's checked when it runs?**
When scheduling: the input checks only (`invalid-amount`, `account-not-found`,
`key-not-found`, `invalid-schedule`). When it runs: everything a normal
transfer checks, as if it were sent at `execute_at` — not at the moment you
noticed it was due.

**Can `execute_at` be equal to the current timestamp?** No →
`invalid-schedule`. It must be strictly later.

**Several due at once — in what order?** By `execute_at`. Ties go in the order
they were scheduled.

**Canceling at exactly `execute_at`?** Too late. Due transfers run first, so it
already ran → `not-cancelable`.

**What can be canceled?** Only a scheduled transfer that hasn't run yet.
Success → `approved`. Any other known id → `not-cancelable`. Unknown id →
`transfer-not-found`.

**What does `get_transfer_status` return?** For any id ever received, regular
or scheduled: `"approved"` or `"rejected"` with its violations, `"scheduled"`
while pending, `"canceled"` if canceled. Unknown id → `None`.

**Do scheduled transfers count toward the limits and the double-tap check?**
Yes, once they run and are approved — same as any transfer.

---

## For the 1:1 breakout (10–12 min)

Let the candidate lead first. Then pick a few:

- Walk me through your data model. Why store the history that way?
- How do you check the hourly limit? What does it cost with 10.000 transfers
  per account? How would you make it cheaper?
- How did you make sure 20:00 and 06:00 behave correctly?
- Why do scheduled transfers run before the current operation?
- What didn't you finish, and how would you do it?
- If keys could be deleted, what would break?
