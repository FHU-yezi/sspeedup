from typing import Any, Dict, Literal, Optional

from qrcode import QRCode

ERROR_CORRECT_STR_TO_LEVEL: Dict[str, int] = {
    "L": 1,
    "M": 0,
    "Q": 3,
    "H": 2,
}


def make_qrcode(
    data: str,
    *,
    version: Optional[int] = None,
    error_correction: Literal[0, 1, 2, 3] = 0,
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white"
) -> Any:
    qrcode_obj = QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qrcode_obj.make(fit=version is None)
    return qrcode_obj.make_image(fill_color=fill_color, back_color=back_color)._img
