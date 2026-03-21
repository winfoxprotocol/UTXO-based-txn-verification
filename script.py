"""
Stack-based script interpreter.

Execute script_sig first, then script_pubkey.
`message` is the signing message for OP_CHECKSIG / OP_CHECKMULTISIG.

Supported opcodes (all required):
  OP_DUP
  OP_HASH160
  OP_EQUAL
  OP_EQUALVERIFY
  OP_CHECKSIG
  OP_VERIFY
  OP_CHECKMULTISIG

Data encoding rules (see the assignment instructions):
- Script elements are either:
  * One of the opcodes above, OR
  * Hex-encoded strings representing raw bytes (signatures, pubkeys, hashes), OR
  * Small Python ints (only for m and n in multisig).
- Non-opcode strings MUST be treated as hex; do NOT guess ASCII.
"""

# Import crypto for OP_HASH160, OP_CHECKSIG, OP_CHECKMULTISIG
from crypto import hash160, verify_signature

OPCODES = {
    "OP_DUP",
    "OP_HASH160",
    "OP_EQUAL",
    "OP_EQUALVERIFY",
    "OP_CHECKSIG",
    "OP_VERIFY",
    "OP_CHECKMULTISIG",
}


def execute_script(script_sig: list, script_pubkey: list, message: bytes) -> bool:
    """
    Run script_sig then script_pubkey on a fresh stack.
    """
    stack= []
    combined= list(script_sig) + list(script_pubkey)

    try:
        for elem in combined:
            if isinstance(elem, str) and elem in OPCODES:
                #handle opcodes
                if elem== "OP_DUP":
                    if len(stack) < 1:
                        return False
                    stack.append(stack[-1])

                elif elem== "OP_HASH160":
                    if len(stack) < 1:
                        return False
                    data= stack.pop()
                    stack.append(hash160(data))

                elif elem== "OP_EQUAL":
                    if len(stack) < 2:
                        return False
                    a= stack.pop()
                    b= stack.pop()
                    stack.append(1 if a == b else 0)

                elif elem== "OP_EQUALVERIFY":
                    if len(stack) < 2:
                        return False
                    a= stack.pop()
                    b= stack.pop()
                    if a != b:
                        return False

                elif elem== "OP_CHECKSIG":
                    if len(stack) < 2:
                        return False
                    pubkey= stack.pop()
                    sig= stack.pop()
                    if verify_signature(pubkey, message, sig):
                        stack.append(1)
                    else:
                        stack.append(0)

                elif elem== "OP_VERIFY":
                    if len(stack) < 1:
                        return False
                    top= stack.pop()
                    if not top:
                        return False

                elif elem== "OP_CHECKMULTISIG":
                    if len(stack) < 1:
                        return False
                    n= stack.pop()
                    if len(stack) < n:
                        return False
                    pubkeys= [stack.pop() for _ in range(n)]
                    pubkeys.reverse()
                    if len(stack) < 1:
                        return False
                    m= stack.pop()
                    if len(stack) < m:
                        return False
                    sigs= [stack.pop() for _ in range(m)]
                    sigs.reverse()

                    pub_idx= 0
                    matched= True
                    for sig in sigs:
                        found= False
                        while pub_idx < n:
                            if verify_signature(pubkeys[pub_idx], message, sig):
                                pub_idx += 1
                                found= True
                                break
                            pub_idx += 1
                        if not found:
                            matched= False
                            break
                    stack.append(1 if matched else 0)

                else:
                    return False
            elif isinstance(elem, int):
                stack.append(elem)
            elif isinstance(elem, str):
                #non-opcode string: try hex, fall back to int
                try:
                    stack.append(bytes.fromhex(elem))
                except ValueError:
                    stack.append(int(elem))
            else:
                return False

        return len(stack)== 1 and bool(stack[0])
    except Exception:
        return False


def _is_opcode(elem) -> bool:
    """True if elem is an opcode string (e.g. OP_DUP)."""
    return isinstance(elem, str) and elem.startswith("OP_")


def _to_bytes(elem: str) -> bytes:
    """
    Convert a non-opcode string element to bytes.
    MUST treat elem as hex; no ASCII guessing.
    """
    return bytes.fromhex(elem)
