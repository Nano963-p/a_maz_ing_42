# a-maze-ing

## Reusable package

This project includes a reusable maze generation package: `mazegen_core`.

```python
from mazegen_core import MazeGenerator

generator = MazeGenerator(width=20, height=10, seed=42)
grid, path, forbidden = generator.generate()
generator.write_output("maze.txt", grid, path)
```
