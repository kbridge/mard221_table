from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from . import colors

def linearize_color_component(component: float) -> float:
    if component <= 0.03928:
        return component / 12.92
    return ((component + 0.055) / 1.055) ** 2.4

def is_color_light(rgb: str) -> bool:
    r = linearize_color_component(int(rgb[0:2], 16) / 255)
    g = linearize_color_component(int(rgb[2:4], 16) / 255)
    b = linearize_color_component(int(rgb[4:6], 16) / 255)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    threshold = 0.15
    return (luminance + 0.05) ** 2 > threshold

def simplify_color_name(name: str) -> str:
    s = name[0]
    t = name[1:].lstrip("0")
    return s + t

SHOW_HEX = True

def main() -> None:
    groups = []
    last_letter = None
    for name in colors.mard221:
        letter = name[0]
        if letter != last_letter:
            groups.append([])
            last_letter = letter
        groups[-1].append(name)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sheet1"
    for group_index, group in enumerate(groups):
        column_name = chr(65 + group_index)
        for color_index, name in enumerate(group):
            cell_name = column_name + str(color_index + 1)
            color_rgb = colors.palette[name]
            cell = worksheet[cell_name]
            cell.value = simplify_color_name(name)
            if SHOW_HEX:
                cell.value += f",#{color_rgb}"
            cell.alignment = Alignment(horizontal="center")
            cell.font = Font(
                name="Courier New",
                color="000000" if is_color_light(color_rgb) else "FFFFFF"
            )
            cell.fill = PatternFill(fill_type="solid", fgColor=color_rgb)
        if SHOW_HEX:
            worksheet.column_dimensions[column_name].width = 14.67
    if SHOW_HEX:
        workbook.save("mard221-hex.xlsx")
    else:
        workbook.save("mard221.xlsx")
