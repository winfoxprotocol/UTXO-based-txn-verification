# UTXO-Based Transaction Verification

A Bitcoin-style transaction verification system implemented in Python. It features a stack-based script interpreter, deterministic transaction serialization, and UTXO set management — covering the core mechanics behind how Bitcoin validates transactions.

## Architecture

```
verifier.py            Main entry point — validates transactions and updates the UTXO set
  ├── transaction.py   Deterministic serialization, transaction IDs, signing messages
  │     └── crypto.py  Cryptographic primitives (hash160, hash256, ECDSA verify)
  ├── script.py        Stack-based script interpreter (Bitcoin Script subset)
  │     └── crypto.py
  └── utxo.py          UTXO set operations (get / spend / add)
```

## Supported Opcodes

| Opcode | Description |
|---|---|
| `OP_DUP` | Duplicate the top stack element |
| `OP_HASH160` | Replace top element with its RIPEMD160(SHA256()) hash |
| `OP_EQUAL` | Pop two elements, push `1` if equal, else `0` |
| `OP_EQUALVERIFY` | Same as `OP_EQUAL` but immediately fails the script if not equal |
| `OP_CHECKSIG` | Verify an ECDSA signature against a public key |
| `OP_CHECKMULTISIG` | M-of-N multi-signature verification (stack: `...sigs M pubkeys N`) |
| `OP_VERIFY` | Pop top element, fail the script if falsy |

## Verification Pipeline

`verify_transaction(tx, utxo_set)` runs these checks in order:

1. **Structure** — transaction must have at least one input and one output
2. **No duplicate inputs** — no two inputs may reference the same `(txid, vout)`
3. **UTXO existence** — every referenced output must exist in the UTXO set
4. **Non-negative outputs** — all output values must be >= 0
5. **Sufficient funds** — total input value >= total output value (difference is the fee)
6. **Script execution** — for each input, `script_sig + script_pubkey` must leave a single truthy value on the stack
7. **Atomic UTXO update** — spent outputs are removed and new outputs are added

## Transaction Format

```python
{
    "inputs": [
        {"txid": "<hex-string>", "vout": 0, "script_sig": ["<sig-hex>", "<pubkey-hex>"]}
    ],
    "outputs": [
        {"value": 5000, "script_pubkey": ["OP_DUP", "OP_HASH160", "<hash-hex>", "OP_EQUALVERIFY", "OP_CHECKSIG"]}
    ]
}
```

## Setup

```bash
pip install ecdsa pycryptodome
```

> `pycryptodome` is only needed if your system's OpenSSL lacks RIPEMD160 support.

**Python 3.10+** is required (uses `X | Y` union type syntax).

## Usage

```python
from verifier import verify_transaction

# UTXO set: keys are (txid, vout) tuples, values are {"value": int, "script_pubkey": list}
utxo_set = {
    ("aabb...ff", 0): {"value": 10000, "script_pubkey": ["OP_DUP", "OP_HASH160", "<hash>", "OP_EQUALVERIFY", "OP_CHECKSIG"]}
}

tx = { ... }  # transaction dict (see format above)

is_valid = verify_transaction(tx, utxo_set)  # also updates utxo_set on success
```

## Serialization

Transaction IDs are computed via deterministic JSON serialization:

```
tx_id = SHA256(SHA256(json.dumps(tx, sort_keys=True, separators=(",", ":")).encode("utf-8"))).hex()
```

Signing messages substitute the spent output's `script_pubkey` into the input being signed and blank out all other inputs' `script_sig` fields — mirroring Bitcoin's `SIGHASH_ALL` approach.
