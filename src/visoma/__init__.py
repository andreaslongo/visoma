from datetime import datetime
import cattrs

from visoma.client import VisomaClient

cattrs.register_structure_hook(datetime, lambda v, _: datetime.fromisoformat(v))
cattrs.register_unstructure_hook(datetime, lambda v: v.isoformat(sep=" "))

__all__ = ["VisomaClient"]
