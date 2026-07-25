from __future__ import annotations

from aegis_ueba.explainability.reason_codes import REASON_LIBRARY


def build_explanations(reasons: list[dict[str, str | float]]) -> list[str]:
    outputs = []
    for reason in reasons:
        code = str(reason["code"])
        description = REASON_LIBRARY.get(code, code)
        outputs.append(f"{description} Observed value: {reason['value']}.")
    return outputs
