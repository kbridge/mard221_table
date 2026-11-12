from pathlib import Path

class LineLoader:
    def __init__(self, file: Path):
        self.lines = file.read_text(encoding="utf-8").splitlines()
        self.start_index = None
        self.end_index = None

    def locate_start(self, expected: str):
        for index, line in enumerate(self.lines):
            if line == expected:
                self.start_index = index + 1
                return self
        raise Exception('start line not found')

    def skip_line(self):
        assert self.start_index is not None
        self.start_index += 1
        return self

    def locate_end(self, expected: str):
        assert self.start_index is not None
        for index in range(self.start_index, len(self.lines)):
            line = self.lines[index]
            if line == expected:
                self.end_index = index
                return self
        raise Exception('end line not found')

    @property
    def result(self):
        assert self.start_index is not None
        assert self.end_index is not None
        return self.lines[self.start_index:self.end_index]

def find_all_strings(text):
    collected = []
    start = 0
    while True:
        # 34 double quote
        # 39 single quote
        begin_index = -1
        matching_quote = None
        for quote_char in (chr(34), chr(39)):
            new_index = text.find(quote_char, start)
            if new_index >= 0:
                if begin_index < 0 or new_index < begin_index:
                    begin_index = new_index
                    matching_quote = quote_char
        if begin_index < 0:
            break
        end_index = text.find(matching_quote, begin_index + 1)
        if end_index < 0:
            break
        inside = text[begin_index+1:end_index]
        collected.append(inside)
        start = end_index + 1
    return collected

class Subset:
    def __init__(self):
        self.names = []

    def load(self, lines):
        """Read and sort color names from Dart source file."""
        for line in lines:
            self.names.extend(line.replace("'", "").replace(",", "").strip().split())
        self.names.sort()

    def dump(self, output_file, subset_name):
        """Write color names as Python list."""
        print(f"{subset_name} = [", file=output_file)
        for name in self.names:
            print(f'    "{name}",', file=output_file)
        print("]", file=output_file)    

REPO_DIR = Path(r"D:\monokaro\pindou-project\pindou")
PALETTE_FILE = REPO_DIR / r"packages\pindou\lib\features\blueprint\palette.dart"
SUBSET_FILE = REPO_DIR / r"packages\pindou\lib\features\blueprint\mard_colors.dart"

colors: list[tuple[str, str]] = []

for line in (
    LineLoader(PALETTE_FILE)
    .locate_start("final List<BeadColor> beadPalette = [")
    .skip_line()
    .locate_end("];")
    .result
):
    pair = find_all_strings(line)
    if len(pair) != 2:
        raise Exception('expect exact two strings in current line')
    name, rgb = pair
    assert rgb.startswith("#")
    rgb = rgb[1:]
    colors.append((name, rgb))

subsets: list[tuple[int, Subset]] = []
for n in [24, 48, 72, 96, 120, 144, 221]:
    subset = Subset()
    subset.load(
        LineLoader(SUBSET_FILE)
        .locate_start(f"const List<String> mard{n} = [")
        .locate_end("];")
        .result
    )
    subsets.append((n, subset))

output_file_path = Path(__file__).resolve().parent.parent / "src" / "mard221_table" / "colors.py"
print(output_file_path)

with output_file_path.open("w", encoding="utf-8") as output_file:
    print("palette = {", file=output_file)
    for name, value in colors:
        print(f'    "{name}": "{value}",', file=output_file)
    print("}", file=output_file)

    for n, subset in subsets:
        print(file=output_file)
        subset.dump(output_file, f"mard{n}")
