import drawsvg as draw

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

def write_mard221_excel(show_hex) -> None:
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
    assert worksheet is not None
    worksheet.title = "Sheet1"
    for group_index, group in enumerate(groups):
        column_name = chr(65 + group_index)
        for color_index, name in enumerate(group):
            cell_name = column_name + str(color_index + 1)
            color_rgb = colors.palette[name]
            cell = worksheet[cell_name]
            cell.value = simplify_color_name(name)
            if show_hex:
                cell.value += f",#{color_rgb}"
            cell.alignment = Alignment(horizontal="center")
            cell.font = Font(
                name="Courier New",
                color="000000" if is_color_light(color_rgb) else "FFFFFF"
            )
            cell.fill = PatternFill(fill_type="solid", fgColor=color_rgb)
        if show_hex:
            worksheet.column_dimensions[column_name].width = 14.67
    if show_hex:
        workbook.save("mard221-hex.xlsx")
    else:
        workbook.save("mard221.xlsx")

# e.g. name="mard24"

def write_svg(name) -> None:
    radius = 24
    border_width = 2 # set to zero to hide border
    border_color = "#e0e0e0"

    horizontal_gap = 12
    vertical_gap = horizontal_gap

    horizontal_margin = 20
    vertical_margin = horizontal_margin

    font_family="sans-serif"
    font_size = 12
    # inconsistency:
    #     first three components range 0 to 255
    #     last component range 0.0 to 1.0
    text_color_normal = f"rgba(0, 0, 0, 0.87)"
    text_color_inversed = "rgb(255, 255, 255)"

    diameter = radius * 2

    color_names: list[str] = colors.__dict__[name]
    color_count = len(color_names)

    num_columns = 8
    num_rows = color_count // num_columns
    if color_count % num_columns != 0:
        num_rows += 1

    d = draw.Drawing(
        horizontal_margin * 2 + diameter * num_columns + horizontal_gap * (num_columns - 1),
        vertical_margin * 2 + diameter * num_rows + vertical_gap * (num_rows - 1),
    )

    for color_index, color_name in enumerate(color_names):
        row_index = color_index // num_columns
        column_index = color_index % num_columns

        color_rgb = colors.palette[color_name]

        circle_y = vertical_margin + row_index * (diameter + vertical_gap) + radius
        circle_x = horizontal_margin + column_index * (diameter + horizontal_gap) + radius

        extra_parameters = {}
        extra_parameters["fill"] = "#"+color_rgb.lower()
        if border_width > 0:
            extra_parameters["stroke"] = border_color
            extra_parameters["stroke_width"] = border_width
        d.append(
            draw.Circle(
                circle_x,
                circle_y,
                radius,
                **extra_parameters,
            )
        )

        if is_color_light(color_rgb):
            text_color = text_color_normal
        else:
            text_color = text_color_inversed

        d.append(
            draw.Text(
                simplify_color_name(color_name),
                font_size,
                circle_x,
                circle_y,
                center=True,
                font_family=font_family,
                fill=text_color,
            )
        )

    d.save_svg(f"{name}.svg")

def main() -> None:
    write_svg("mard24")
