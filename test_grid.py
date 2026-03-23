from maze.grid import create_grid
from maze.pattern import stamp_42_pattern
from maze.generator import generate_maze
from maze.solver import solve_maze
from maze.encoder import format_output

grid = create_grid(10, 10)
forbidden = stamp_42_pattern(grid)
generate_maze(grid, seed=42, perfect=True, forbidden=forbidden)

path = solve_maze(grid, (0, 0), (9, 9))
output = format_output(grid, (0, 0), (9, 9), path)

print(type(path))
print(len(path) > 0)
print(all(c in "NESW" for c in path))
print(isinstance(output, str))
print("0,0" in output)
print("9,9" in output)
print(path in output)