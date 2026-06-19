from typing import Any


class BiometricNormalizer:
    """Normalize raw biometric inputs to 1-10 score ranges."""

    @staticmethod
    def _to_float(value: Any, default: float) -> float:
        try:
            if value is None:
                return default
            if isinstance(value, str):
                cleaned = value.strip().lower()
                cleaned = cleaned.replace("hours", "").replace("hour", "")
                cleaned = cleaned.replace("liters", "").replace("liter", "")
                cleaned = cleaned.replace("ml", "")
                if not cleaned:
                    return default
                return float(cleaned)
            return float(value)
        except Exception:
            return default

    @classmethod
    def parse_sleep_hours(cls, value: Any, default: float = 7.0) -> float:
        if isinstance(value, str):
            text = value.strip().lower().replace("hours", "").replace("hour", "")
            if "h" in text and "m" in text:
                try:
                    hours_part, minutes_part = text.split("h", 1)
                    minutes_part = minutes_part.replace("m", "").strip()
                    hours = float(hours_part.strip() or "0")
                    minutes = float(minutes_part or "0")
                    return max(0.0, hours + (minutes / 60.0))
                except Exception:
                    return default
        return max(0.0, cls._to_float(value, default))

    @classmethod
    def parse_water_liters(cls, value: Any, default: float = 2.5) -> float:
        liters = cls._to_float(value, default)
        if liters > 100:
            liters = liters / 1000.0
        return max(0.0, liters)

    @classmethod
    def normalize_sleep(cls, value: Any) -> float:
        hours = cls.parse_sleep_hours(value)

        # Pass through plausible score-style inputs.
        if 1.0 <= hours <= 10.0 and not isinstance(value, str):
            return round(max(1.0, min(10.0, hours)), 2)

        if hours < 6.0:
            score = 1.0 + (hours / 6.0) * 3.0  # 1-4
        elif hours < 7.0:
            score = 4.0 + (hours - 6.0) * 3.0  # 4-7
        elif hours <= 9.0:
            score = 8.0 + ((hours - 7.0) / 2.0) * 2.0  # 8-10
        elif hours <= 12.0:
            score = 8.0 - ((hours - 9.0) / 3.0) * 2.0  # 8-6
        else:
            score = 6.0 - ((hours - 12.0) / 8.0) * 2.0  # taper to 4

        return round(max(1.0, min(10.0, score)), 2)

    @classmethod
    def normalize_hydration(cls, value: Any) -> float:
        liters = cls.parse_water_liters(value)

        # Pass through plausible score-style inputs.
        if 1.0 <= liters <= 10.0 and not isinstance(value, str):
            # Distinguish likely liters from explicit score values: tiny hydration values
            # like 1.2L should still map through hydration logic.
            if liters <= 1.8:
                pass
            else:
                return round(max(1.0, min(10.0, liters)), 2)

        if liters < 1.5:
            score = 1.0 + (liters / 1.5) * 2.0  # 1-3
        elif liters < 2.0:
            score = 3.0 + ((liters - 1.5) / 0.5) * 2.0  # 3-5
        elif liters <= 3.5:
            score = 7.0 + ((liters - 2.0) / 1.5) * 3.0  # 7-10
        elif liters <= 5.0:
            score = 7.0 - ((liters - 3.5) / 1.5) * 1.0  # 7-6
        else:
            score = 6.0 - ((liters - 5.0) / 5.0) * 2.0  # taper to 4

        return round(max(1.0, min(10.0, score)), 2)
