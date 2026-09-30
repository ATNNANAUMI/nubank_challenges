"""
Tests for Live Case 2 -- PIX Authorizer.

Run from this folder:
    python -m unittest -v
    python -m unittest -v test_pix_authorizer.TestPart3NightLimit   # one part

Heads-up: the test names give the clarifications away.
Finish Stage 1 (your list of questions) before reading this file.
"""

import unittest

from pix_authorizer import PixAuthorizer

# Accounts and keys are created at SETUP, before anything else happens.
SETUP = "2026-10-01T08:00:00"


def at(clock, day=5):
    """at("21:30:00") -> "2026-10-05T21:30:00" (a Monday). day=6 is the Tuesday."""
    return f"2026-10-{day:02d}T{clock}"


OK = {"status": "approved", "violations": []}
SCHEDULED = {"status": "scheduled", "violations": []}
CANCELED = {"status": "canceled", "violations": []}


def rejected(*violations):
    return {"status": "rejected", "violations": list(violations)}


ANA_CPF = "12345678909"
BRUNO_EMAIL = "bruno@nubank.com.br"
BRUNO_CPF = "98765432100"
CARLA_PHONE = "+5511987654321"
DANI_EMAIL = "dani@nubank.com.br"

VALID_KEYS = [
    "11122233344",                           # CPF, digits only
    "555.666.777-88",                        # CPF, formatted
    "ana.souza@nubank.com.br",               # e-mail
    "+5521912345678",                        # phone
    "123e4567-e89b-12d3-a456-426614174000",  # random key
]

INVALID_KEYS = [
    "1234567890",                            # CPF with 10 digits
    "123456789012",                          # CPF with 12 digits
    "123.456.789-0",                         # formatted CPF with 10 digits
    "abc",                                   # not anything
    "ana@nubank",                            # e-mail domain without a dot
    "@nubank.com.br",                        # e-mail with nothing before @
    "ana@@nubank.com.br",                    # two @
    "ana@.nubank.com",                       # domain starts with a dot
    "+551198765432",                         # phone with 10 digits after +55
    "+4411987654321",                        # right length, but not +55
    "123e4567-e89b-12d3-a456-42661417400g",  # random key with a non-hex char
]


class Base(unittest.TestCase):
    def setUp(self):
        self.pix = PixAuthorizer()
        self.count = 0

    def open(self, account_id, balance, *keys):
        """Create an account and its keys at SETUP time."""
        self.assertEqual(self.pix.create_account(SETUP, account_id, balance), OK)
        for key in keys:
            self.assertEqual(self.pix.register_key(SETUP, account_id, key), OK)

    def send(self, timestamp, amount, frm="A", to=BRUNO_EMAIL):
        """transfer() with an auto-generated transfer id."""
        self.count += 1
        return self.pix.transfer(timestamp, f"T{self.count}", frm, to, amount)


# --------------------------------------------------------------------- Part 1


class TestPart1Basics(Base):
    def test_create_account(self):
        self.assertEqual(self.pix.create_account(SETUP, "A", 5000), OK)
        self.assertEqual(self.pix.get_balance(SETUP, "A"), 5000)

    def test_starting_balance_can_be_zero(self):
        self.assertEqual(self.pix.create_account(SETUP, "A", 0), OK)
        self.assertEqual(self.pix.get_balance(SETUP, "A"), 0)

    def test_account_id_already_taken(self):
        self.pix.create_account(SETUP, "A", 5000)
        self.assertEqual(self.pix.create_account(SETUP, "A", 9999), rejected("account-already-exists"))
        self.assertEqual(self.pix.create_account(SETUP, "A", -5), rejected("account-already-exists"))
        self.assertEqual(self.pix.get_balance(SETUP, "A"), 5000)

    def test_negative_starting_balance(self):
        self.assertEqual(self.pix.create_account(SETUP, "A", -1), rejected("invalid-amount"))
        self.assertIsNone(self.pix.get_balance(SETUP, "A"))

    def test_balance_of_unknown_account_is_none(self):
        self.assertIsNone(self.pix.get_balance(SETUP, "ghost"))

    def test_register_key(self):
        self.pix.create_account(SETUP, "A", 0)
        self.assertEqual(self.pix.register_key(SETUP, "A", ANA_CPF), OK)

    def test_register_key_on_unknown_account(self):
        self.assertEqual(self.pix.register_key(SETUP, "ghost", ANA_CPF), rejected("account-not-found"))

    def test_key_taken_by_another_account(self):
        self.open("A", 0, ANA_CPF)
        self.open("B", 0)
        self.assertEqual(self.pix.register_key(SETUP, "B", ANA_CPF), rejected("key-already-registered"))

    def test_transfer_moves_money(self):
        self.open("A", 50000, ANA_CPF)
        self.open("B", 1000, BRUNO_EMAIL)
        self.assertEqual(self.pix.transfer(at("10:00:00"), "T1", "A", BRUNO_EMAIL, 12000), OK)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 38000)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "B"), 13000)

    def test_money_flows_both_ways(self):
        self.open("A", 50000, ANA_CPF)
        self.open("B", 0, BRUNO_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 12000, frm="A", to=BRUNO_EMAIL), OK)
        self.assertEqual(self.send(at("10:05:00"), 2000, frm="B", to=ANA_CPF), OK)
        self.assertEqual(self.pix.get_balance(at("10:05:00"), "A"), 40000)
        self.assertEqual(self.pix.get_balance(at("10:05:00"), "B"), 10000)

    def test_sending_the_whole_balance(self):
        self.open("A", 50000)
        self.open("B", 0, BRUNO_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 50000), OK)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 0)

    def test_insufficient_balance_changes_nothing(self):
        self.open("A", 50000)
        self.open("B", 1000, BRUNO_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 50001), rejected("insufficient-balance"))
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 50000)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "B"), 1000)

    def test_zero_or_negative_amount(self):
        self.open("A", 50000)
        self.open("B", 0, BRUNO_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 0), rejected("invalid-amount"))
        self.assertEqual(self.send(at("10:00:00"), -100), rejected("invalid-amount"))

    def test_unknown_sender(self):
        self.open("B", 0, BRUNO_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 100, frm="ghost"), rejected("account-not-found"))

    def test_unknown_key(self):
        self.open("A", 50000)
        self.assertEqual(self.send(at("10:00:00"), 100, to="nobody@nubank.com.br"), rejected("key-not-found"))

    def test_input_checks_stop_at_the_first_failure(self):
        nobody = "nobody@nubank.com.br"
        self.assertEqual(self.send(at("10:00:00"), 0, frm="ghost", to=nobody), rejected("invalid-amount"))
        self.assertEqual(self.send(at("10:00:00"), 100, frm="ghost", to=nobody), rejected("account-not-found"))

    def test_sending_to_yourself(self):
        self.open("A", 50000, ANA_CPF)
        self.assertEqual(self.send(at("10:00:00"), 100, to=ANA_CPF), rejected("same-account"))
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 50000)

    def test_business_rules_report_every_failure(self):
        self.open("A", 50000, ANA_CPF)
        self.assertEqual(
            self.send(at("10:00:00"), 60000, to=ANA_CPF),
            rejected("same-account", "insufficient-balance"),
        )


# --------------------------------------------------------------------- Part 2


class TestPart2Keys(Base):
    def setUp(self):
        super().setUp()
        self.open("A", 100000)
        self.open("B", 100000)

    def test_every_key_type_is_accepted(self):
        for key in VALID_KEYS:
            with self.subTest(key=key):
                self.assertEqual(self.pix.register_key(SETUP, "A", key), OK)

    def test_malformed_keys_are_rejected(self):
        for key in INVALID_KEYS:
            with self.subTest(key=key):
                self.assertEqual(self.pix.register_key(SETUP, "A", key), rejected("invalid-key"))

    def test_rejected_keys_do_not_use_the_limit(self):
        for key in INVALID_KEYS:
            self.pix.register_key(SETUP, "A", key)
        for key in VALID_KEYS:
            with self.subTest(key=key):
                self.assertEqual(self.pix.register_key(SETUP, "A", key), OK)

    def test_email_is_case_insensitive(self):
        self.assertEqual(self.pix.register_key(SETUP, "A", "Ana.Souza@Nubank.com.br"), OK)
        self.assertEqual(
            self.pix.register_key(SETUP, "B", "ana.souza@nubank.com.br"),
            rejected("key-already-registered"),
        )
        self.assertEqual(self.send(at("10:00:00"), 1000, frm="B", to="ANA.SOUZA@NUBANK.COM.BR"), OK)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 101000)

    def test_cpf_punctuation_is_ignored(self):
        self.assertEqual(self.pix.register_key(SETUP, "A", "123.456.789-09"), OK)
        self.assertEqual(self.pix.register_key(SETUP, "B", "12345678909"), rejected("key-already-registered"))
        self.assertEqual(self.send(at("10:00:00"), 1000, frm="B", to="12345678909"), OK)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 101000)

    def test_random_key_is_case_insensitive(self):
        self.assertEqual(self.pix.register_key(SETUP, "A", "123E4567-E89B-12D3-A456-426614174000"), OK)
        self.assertEqual(
            self.send(at("10:00:00"), 1000, frm="B", to="123e4567-e89b-12d3-a456-426614174000"), OK
        )
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 101000)

    def test_sixth_key_is_rejected(self):
        for key in VALID_KEYS:
            self.pix.register_key(SETUP, "A", key)
        self.assertEqual(self.pix.register_key(SETUP, "A", "+5511900001111"), rejected("key-limit-reached"))

    def test_registering_your_own_key_again(self):
        self.pix.register_key(SETUP, "A", ANA_CPF)
        self.assertEqual(self.pix.register_key(SETUP, "A", ANA_CPF), rejected("key-already-registered"))

    def test_key_rules_report_every_failure(self):
        for key in VALID_KEYS:
            self.pix.register_key(SETUP, "A", key)
        self.pix.register_key(SETUP, "B", BRUNO_EMAIL)
        self.assertEqual(
            self.pix.register_key(SETUP, "A", BRUNO_EMAIL),
            rejected("key-already-registered", "key-limit-reached"),
        )

    def test_key_input_checks_stop_at_the_first_failure(self):
        self.assertEqual(self.pix.register_key(SETUP, "ghost", "not-a-key"), rejected("account-not-found"))

    def test_transfer_to_a_malformed_key(self):
        self.assertEqual(self.send(at("10:00:00"), 1000, frm="B", to="ana@nubank"), rejected("key-not-found"))


# --------------------------------------------------------------------- Part 3


class TestPart3NightLimit(Base):
    def setUp(self):
        super().setUp()
        self.open("A", 1_000_000, ANA_CPF)
        self.open("B", 0, BRUNO_EMAIL)
        self.open("D", 100_000, DANI_EMAIL)

    def test_limit_is_the_total_for_the_night(self):
        self.assertEqual(self.send(at("21:00:00"), 60000), OK)
        self.assertEqual(self.send(at("23:00:00"), 50000), rejected("night-limit-exceeded"))
        self.assertEqual(self.send(at("23:30:00"), 40000), OK)  # exactly R$ 1.000,00 tonight
        self.assertEqual(self.send(at("23:45:00"), 1), rejected("night-limit-exceeded"))

    def test_night_continues_after_midnight(self):
        self.assertEqual(self.send(at("22:00:00"), 70000), OK)
        self.assertEqual(self.send(at("01:00:00", day=6), 40000), rejected("night-limit-exceeded"))
        self.assertEqual(self.send(at("05:59:59", day=6), 30000), OK)

    def test_6am_is_day(self):
        self.assertEqual(self.send(at("22:00:00"), 100000), OK)
        self.assertEqual(self.send(at("06:00:00", day=6), 150000), OK)

    def test_8pm_is_night_and_day_transfers_do_not_count(self):
        self.assertEqual(self.send(at("19:59:59"), 300000), OK)
        self.assertEqual(self.send(at("20:00:00"), 150000), rejected("night-limit-exceeded"))
        self.assertEqual(self.send(at("20:05:00"), 100000), OK)

    def test_each_night_has_its_own_limit(self):
        self.assertEqual(self.send(at("21:00:00"), 100000), OK)
        self.assertEqual(self.send(at("02:00:00", day=6), 1), rejected("night-limit-exceeded"))
        self.assertEqual(self.send(at("20:00:00", day=6), 100000), OK)

    def test_limit_is_per_sending_account(self):
        self.assertEqual(self.send(at("21:00:00"), 100000, frm="A", to=BRUNO_EMAIL), OK)
        self.assertEqual(self.send(at("21:10:00"), 100000, frm="B", to=ANA_CPF), OK)

    def test_rejected_transfers_do_not_use_the_limit(self):
        self.assertEqual(
            self.send(at("21:00:00"), 150000, frm="D"),
            rejected("insufficient-balance", "night-limit-exceeded"),
        )
        self.assertEqual(self.send(at("21:05:00"), 100000, frm="D"), OK)

    def test_violations_come_in_table_order(self):
        self.assertEqual(
            self.send(at("21:00:00"), 150000, frm="D", to=DANI_EMAIL),
            rejected("same-account", "insufficient-balance", "night-limit-exceeded"),
        )


# --------------------------------------------------------------------- Part 4


class TestPart4FraudRules(Base):
    def setUp(self):
        super().setUp()
        self.open("A", 2_000_000, ANA_CPF)
        self.open("B", 0, BRUNO_EMAIL, BRUNO_CPF)
        self.open("C", 0, CARLA_PHONE)

    def test_hourly_limit_is_a_rolling_window(self):
        self.assertEqual(self.send(at("10:50:00"), 300000), OK)
        self.assertEqual(self.send(at("11:10:00"), 300000, to=CARLA_PHONE), rejected("hourly-limit-exceeded"))
        self.assertEqual(self.send(at("11:50:00"), 300000, to=CARLA_PHONE), OK)

    def test_a_transfer_exactly_one_hour_old_no_longer_counts(self):
        self.assertEqual(self.send(at("10:00:00"), 300000), OK)
        self.assertEqual(self.send(at("10:59:59"), 200001), rejected("hourly-limit-exceeded"))
        self.assertEqual(self.send(at("11:00:00"), 200001, to=CARLA_PHONE), OK)

    def test_reaching_exactly_the_hourly_limit_is_allowed(self):
        self.assertEqual(self.send(at("10:00:00"), 300000), OK)
        self.assertEqual(self.send(at("10:10:00"), 200000), OK)
        self.assertEqual(self.send(at("10:20:00"), 1), rejected("hourly-limit-exceeded"))

    def test_same_transfer_within_a_minute_is_a_duplicate(self):
        self.assertEqual(self.send(at("10:00:00"), 5000), OK)
        self.assertEqual(self.send(at("10:00:59"), 5000), rejected("duplicate-transfer"))
        self.assertEqual(self.pix.get_balance(at("10:00:59"), "A"), 1_995_000)

    def test_exactly_one_minute_later_is_not_a_duplicate(self):
        self.assertEqual(self.send(at("10:00:00"), 5000), OK)
        self.assertEqual(self.send(at("10:01:00"), 5000), OK)

    def test_duplicate_means_same_receiving_account_not_same_key(self):
        self.assertEqual(self.send(at("10:00:00"), 5000, to=BRUNO_EMAIL), OK)
        self.assertEqual(self.send(at("10:00:30"), 5000, to=BRUNO_CPF), rejected("duplicate-transfer"))

    def test_different_amount_or_recipient_is_not_a_duplicate(self):
        self.assertEqual(self.send(at("10:00:00"), 5000), OK)
        self.assertEqual(self.send(at("10:00:10"), 5001), OK)
        self.assertEqual(self.send(at("10:00:20"), 5000, to=CARLA_PHONE), OK)

    def test_a_rejected_transfer_is_not_a_duplicate_source(self):
        self.open("D", 1000, DANI_EMAIL)
        self.assertEqual(self.send(at("10:00:00"), 5000, frm="D"), rejected("insufficient-balance"))
        self.assertEqual(self.send(at("10:00:10"), 10000, frm="A", to=DANI_EMAIL), OK)
        self.assertEqual(self.send(at("10:00:20"), 5000, frm="D"), OK)

    def test_fraud_rules_report_every_failure(self):
        self.assertEqual(self.send(at("10:00:00"), 300000), OK)
        self.assertEqual(
            self.send(at("10:00:30"), 300000),
            rejected("hourly-limit-exceeded", "duplicate-transfer"),
        )

    def test_all_business_rules_in_table_order(self):
        self.open("E", 500000, "eva@nubank.com.br")
        self.assertEqual(self.send(at("19:59:30"), 450000, frm="E"), OK)
        self.assertEqual(
            self.send(at("20:00:00"), 450000, frm="E"),
            rejected(
                "insufficient-balance",
                "night-limit-exceeded",
                "hourly-limit-exceeded",
                "duplicate-transfer",
            ),
        )


# --------------------------------------------------------------------- Part 5


class TestPart5ScheduledPix(Base):
    def setUp(self):
        super().setUp()
        self.open("A", 100000, ANA_CPF)
        self.open("B", 0, BRUNO_EMAIL)
        self.open("C", 0, CARLA_PHONE)

    def schedule(self, timestamp, transfer_id, amount, execute_at, frm="A", to=BRUNO_EMAIL):
        return self.pix.schedule_transfer(timestamp, transfer_id, frm, to, amount, execute_at)

    def test_runs_when_its_time_comes(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 30000, at("10:00:00")), SCHEDULED)
        self.assertEqual(self.pix.get_balance(at("09:59:59"), "A"), 100000)
        self.assertEqual(self.pix.get_transfer_status(at("09:59:59"), "S1"), SCHEDULED)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 70000)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "B"), 30000)
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S1"), OK)

    def test_due_transfers_run_before_the_current_operation(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 30000, at("10:00:00")), SCHEDULED)
        # B has no money until S1 runs.
        self.assertEqual(self.send(at("15:00:00"), 20000, frm="B", to=CARLA_PHONE), OK)
        self.assertEqual(self.pix.get_balance(at("15:00:00"), "A"), 70000)
        self.assertEqual(self.pix.get_balance(at("15:00:00"), "B"), 10000)
        self.assertEqual(self.pix.get_balance(at("15:00:00"), "C"), 20000)

    def test_execute_at_must_be_in_the_future(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 1000, at("09:00:00")), rejected("invalid-schedule"))
        self.assertEqual(self.schedule(at("09:00:00"), "S2", 1000, at("08:59:59")), rejected("invalid-schedule"))

    def test_scheduling_checks_stop_at_the_first_failure(self):
        nobody = "nobody@nubank.com.br"
        self.assertEqual(
            self.schedule(at("09:00:00"), "S1", 0, at("08:00:00"), to=nobody), rejected("invalid-amount")
        )
        self.assertEqual(
            self.schedule(at("09:00:00"), "S2", 1000, at("08:00:00"), frm="ghost"), rejected("account-not-found")
        )
        self.assertEqual(
            self.schedule(at("09:00:00"), "S3", 1000, at("08:00:00"), to=nobody), rejected("key-not-found")
        )

    def test_rules_are_checked_when_it_runs(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 80000, at("10:00:00")), SCHEDULED)
        self.assertEqual(self.send(at("09:30:00"), 50000, to=CARLA_PHONE), OK)
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S1"), rejected("insufficient-balance"))
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 50000)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "B"), 0)

    def test_due_transfers_run_in_execute_at_order(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 60000, at("11:00:00")), SCHEDULED)
        self.assertEqual(self.schedule(at("09:01:00"), "S2", 60000, at("10:30:00"), to=CARLA_PHONE), SCHEDULED)
        self.assertEqual(self.pix.get_transfer_status(at("12:00:00"), "S2"), OK)
        self.assertEqual(self.pix.get_transfer_status(at("12:00:00"), "S1"), rejected("insufficient-balance"))

    def test_ties_run_in_the_order_they_were_scheduled(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 60000, at("10:00:00")), SCHEDULED)
        self.assertEqual(self.schedule(at("09:01:00"), "S2", 60000, at("10:00:00"), to=CARLA_PHONE), SCHEDULED)
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S1"), OK)
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S2"), rejected("insufficient-balance"))

    def test_cancel_a_pending_transfer(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 30000, at("10:00:00")), SCHEDULED)
        self.assertEqual(self.pix.cancel_scheduled(at("09:30:00"), "S1"), OK)
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S1"), CANCELED)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 100000)

    def test_cancel_at_execute_at_is_too_late(self):
        self.assertEqual(self.schedule(at("09:00:00"), "S1", 30000, at("10:00:00")), SCHEDULED)
        self.assertEqual(self.pix.cancel_scheduled(at("10:00:00"), "S1"), rejected("not-cancelable"))
        self.assertEqual(self.pix.get_transfer_status(at("10:00:00"), "S1"), OK)
        self.assertEqual(self.pix.get_balance(at("10:00:00"), "A"), 70000)

    def test_what_cannot_be_canceled(self):
        self.assertEqual(self.pix.cancel_scheduled(at("09:00:00"), "nope"), rejected("transfer-not-found"))
        self.assertEqual(self.pix.transfer(at("09:10:00"), "T1", "A", BRUNO_EMAIL, 1000), OK)
        self.assertEqual(self.pix.cancel_scheduled(at("09:20:00"), "T1"), rejected("not-cancelable"))
        self.assertEqual(self.schedule(at("09:30:00"), "S1", 1000, at("12:00:00")), SCHEDULED)
        self.assertEqual(self.pix.cancel_scheduled(at("09:40:00"), "S1"), OK)
        self.assertEqual(self.pix.cancel_scheduled(at("09:50:00"), "S1"), rejected("not-cancelable"))

    def test_status_of_regular_rejected_and_unknown_transfers(self):
        self.assertEqual(self.pix.transfer(at("09:00:00"), "T1", "A", BRUNO_EMAIL, 1000), OK)
        self.assertEqual(
            self.pix.transfer(at("09:10:00"), "T2", "A", BRUNO_EMAIL, 100000), rejected("insufficient-balance")
        )
        self.assertEqual(self.schedule(at("09:20:00"), "S1", 1000, at("09:00:00")), rejected("invalid-schedule"))
        self.assertEqual(self.pix.get_transfer_status(at("09:30:00"), "T1"), OK)
        self.assertEqual(self.pix.get_transfer_status(at("09:30:00"), "T2"), rejected("insufficient-balance"))
        self.assertEqual(self.pix.get_transfer_status(at("09:30:00"), "S1"), rejected("invalid-schedule"))
        self.assertIsNone(self.pix.get_transfer_status(at("09:30:00"), "nope"))

    def test_night_limit_counts_scheduled_transfers(self):
        self.open("N", 1_000_000, "nina@nubank.com.br")
        self.assertEqual(self.schedule(at("19:00:00"), "S1", 50000, at("21:30:00"), frm="N"), SCHEDULED)
        self.assertEqual(self.send(at("23:00:00"), 70000, frm="N", to=CARLA_PHONE), rejected("night-limit-exceeded"))
        self.assertEqual(self.pix.get_transfer_status(at("23:00:00"), "S1"), OK)

    def test_judged_at_execute_at_not_when_noticed(self):
        self.open("N", 1_000_000, "nina@nubank.com.br")
        self.assertEqual(self.schedule(at("19:00:00"), "S1", 150000, at("23:00:00"), frm="N"), SCHEDULED)
        # Nothing happens until 07:00 the next morning (daytime), but S1 ran at 23:00 (night).
        self.assertEqual(
            self.pix.get_transfer_status(at("07:00:00", day=6), "S1"), rejected("night-limit-exceeded")
        )

    def test_scheduled_and_manual_transfers_can_be_duplicates(self):
        self.assertEqual(self.pix.transfer(at("10:00:00"), "T1", "A", BRUNO_EMAIL, 5000), OK)
        self.assertEqual(self.schedule(at("10:00:05"), "S1", 5000, at("10:00:30")), SCHEDULED)
        self.assertEqual(self.pix.get_transfer_status(at("10:01:00"), "S1"), rejected("duplicate-transfer"))


if __name__ == "__main__":
    unittest.main()
