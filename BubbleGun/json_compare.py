import json


def _sorted_strs(values):
    return tuple(sorted(str(value) for value in values))


def bubble_signature(bubble):
    return {
        "type": bubble["type"],
        "ends": _sorted_strs(bubble["ends"]),
        "inside": _sorted_strs(bubble["inside"]),
    }


def chain_signature(chain):
    forward = tuple(bubble_signature(bubble) for bubble in chain["bubbles"])
    reverse = tuple(reversed(forward))
    forward_key = tuple(json.dumps(bubble, sort_keys=True) for bubble in forward)
    reverse_key = tuple(json.dumps(bubble, sort_keys=True) for bubble in reverse)
    bubbles = forward if forward_key <= reverse_key else reverse
    return {
        "ends": _sorted_strs(chain["ends"]),
        "bubbles": bubbles,
    }


def normalize_bchains_json(data):
    chains_by_signature = {}
    chain_id_to_signature = {}
    bubble_id_to_signature = {}

    for chain_key, chain in data.items():
        signature = chain_signature(chain)
        signature_key = json.dumps(signature, sort_keys=True)
        chains_by_signature[signature_key] = signature
        chain_id_to_signature[str(chain["chain_id"])] = signature_key

        for bubble in chain["bubbles"]:
            bubble_sig = bubble_signature(bubble)
            bubble_sig_key = json.dumps(bubble_sig, sort_keys=True)
            bubble_id_to_signature[str(bubble["id"])] = bubble_sig_key

    normalized = []
    for chain in data.values():
        signature = chain_signature(chain)
        signature_key = json.dumps(signature, sort_keys=True)
        normalized_chain = {
            "chain": chains_by_signature[signature_key],
            "parent_chain": None,
            "parent_sb": None,
        }

        if "parent_chain" in chain:
            normalized_chain["parent_chain"] = chain_id_to_signature[str(chain["parent_chain"])]
        if "parent_sb" in chain:
            normalized_chain["parent_sb"] = bubble_id_to_signature[str(chain["parent_sb"])]

        normalized.append(normalized_chain)

    normalized.sort(
        key=lambda chain: (
            json.dumps(chain["chain"], sort_keys=True),
            "" if chain["parent_chain"] is None else chain["parent_chain"],
            "" if chain["parent_sb"] is None else chain["parent_sb"],
        )
    )
    return normalized


def compare_bchains_json(first_path, second_path):
    with open(first_path, "r") as handle:
        first_data = json.load(handle)
    with open(second_path, "r") as handle:
        second_data = json.load(handle)

    first_normalized = normalize_bchains_json(first_data)
    second_normalized = normalize_bchains_json(second_data)

    return first_normalized == second_normalized, first_normalized, second_normalized
