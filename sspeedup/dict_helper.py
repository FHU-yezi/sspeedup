from typing import Dict


def unfold(dict_obj: Dict, prefix: str = "") -> Dict:
    result: Dict = {}
    for k, v in dict_obj.items():
        if isinstance(v, dict):
            # 合并字典
            result = dict(result, **unfold(v, prefix=f"{prefix}{k}."))
        else:
            result[prefix + k] = v

    return result


def filter_null_value(item: Dict) -> Dict:
    return {k: v for k, v in item.items() if v is not None}
