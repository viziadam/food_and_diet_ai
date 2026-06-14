```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RecipeMetrics:
    calories_per_serving: float
```
