"""
UTXO set maintenance.
Keys: (txid: str, vout: int)
Values: {"value": int, "script_pubkey": list}
"""


def get_output(utxo_set: dict, txid: str, vout: int) -> dict | None:
    """
    Return the UTXO entry for (txid, vout), or None if not present.
    """
    return utxo_set.get((txid, vout))


def spend_output(utxo_set: dict, txid: str, vout: int) -> None:
    """
    Remove the output (txid, vout) from utxo_set. Idempotent if missing.
    """
    utxo_set.pop((txid, vout), None)


def add_output(utxo_set: dict, txid: str, vout: int, value: int, script_pubkey: list) -> None:
    """
    Add a new unspent output to utxo_set.
    """
    utxo_set[(txid, vout)] = {"value": value, "script_pubkey": script_pubkey}
