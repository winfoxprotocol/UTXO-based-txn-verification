"""
Main entry: verify a transaction and update UTXO set.
"""

from utxo import get_output, spend_output, add_output
from script import execute_script
from transaction import tx_id, get_signing_message


def verify_transaction(tx: dict, utxo_set: dict) -> bool:
    """
    Validate tx against utxo_set.
    """
    #structure check
    if len(tx.get("inputs", [])) < 1 or len(tx.get("outputs", [])) < 1:
        return False

    #duplicate input check
    input_refs = [(inp["txid"], inp["vout"]) for inp in tx["inputs"]]
    if len(set(input_refs)) != len(input_refs):
        return False

    #UTXO existence check
    collected_utxos = []
    for inp in tx["inputs"]:
        utxo=get_output(utxo_set, inp["txid"], inp["vout"])
        if utxo is None:
            return False
        collected_utxos.append(utxo)

    #output value check
    if any(out["value"] < 0 for out in tx["outputs"]):
        return False

    #fee check
    total_in=sum(utxo["value"] for utxo in collected_utxos)
    total_out= sum(out["value"] for out in tx["outputs"])
    if total_in < total_out:
        return False

    #script verification
    for i, inp in enumerate(tx["inputs"]):
        script_pubkey = collected_utxos[i]["script_pubkey"]
        message = get_signing_message(tx, i, script_pubkey)
        if not execute_script(inp["script_sig"], script_pubkey, message):
            return False

    #atomic UTXO update
    for inp in tx["inputs"]:
        spend_output(utxo_set, inp["txid"], inp["vout"])

    new_txid= tx_id(tx)
    for vout, out in enumerate(tx["outputs"]):
        add_output(utxo_set, new_txid, vout, out["value"], out["script_pubkey"])

    return True
