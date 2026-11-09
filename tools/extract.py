from pathlib import Path
repo_dir = Path(r"D:\monokaro\pindou-project\pindou")
source_file = repo_dir / r"packages\pindou\lib\features\blueprint\palette.dart"
lines = source_file.read_text(encoding="utf-8").splitlines()
colors = [(line[17:17+3], line[44:44+6]) for line in lines[314:605]]
source_file = repo_dir / r"packages\pindou\lib\features\blueprint\mard_colors.dart"
lines = source_file.read_text(encoding="utf-8").splitlines()
mard221 = []
for line in lines[72:95]:
    mard221.extend(line.replace("'", "").replace(",", "").strip().split())
mard221.sort()
with open("colors.py", "w", encoding="utf-8") as output_file:
    print("palette = {", file=output_file)
    for name, value in colors:
        print(f'    "{name}": "{value}",', file=output_file)
    print("}", file=output_file)
    print(file=output_file)
    print("mard221 = [", file=output_file)
    for name in mard221:
        print(f'    "{name}",', file=output_file)
    print("]", file=output_file)
