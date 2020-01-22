import random
from contextlib import suppress


def fair_random_generator(items):
    for _ in range(2):
        for item in items:
            yield item
    while True:
        yield random.choice(items)


def parse_int(value):
    with suppress(TypeError, ValueError):
        return int(value)
    return None


COLORS = (
    ("#FC766AFF", "#5B84B1FF"),
    ("#5F4B8BFF", "#E69A8DFF"),
    ("#42EADDFF", "#CDB599FF"),
    ("#000000FF", "#FFFFFFFF"),
    ("#00A4CCFF", "#F95700FF"),
    ("#00203FFF", "#ADEFD1FF"),
    ("#606060FF", "#D6ED17FF"),
    ("#ED2B33FF", "#D85A7FFF"),
    ("#2C5F2D", "#97BC62FF"),
    ("#00539CFF", "#EEA47FFF"),
    ("#0063B2FF", "#9CC3D5FF"),
    ("#D198C5FF", "#E0C568FF"),
    ("#101820FF", "#FEE715FF"),
    ("#CBCE91FF", "#EA738DFF"),
    ("#B1624EFF", "#5CC8D7FF"),
    ("#89ABE3FF", "#FCF6F5FF"),
    ("#E3CD81FF", "#B1B3B3FF"),
    ("#101820FF", "#F2AA4CFF"),
    ("#A07855FF", "#D4B996FF"),
    ("#195190FF", "#A2A2A1FF"),
    ("#603F83FF", "#C7D3D4FF"),
    ("#2BAE66FF", "#FCF6F5FF"),
    ("#FAD0C9FF", "#6E6E6DFF"),
    ("#2D2926FF", "#E94B3CFF"),
    ("#DAA03DFF", "#616247FF"),
    ("#990011FF", "#FCF6F5FF"),
    ("#435E55FF", "#D64161FF"),
    ("#CBCE91FF", "#76528BFF"),
    ("#FAEBEFFF", "#333D79FF"),
    ("#F93822FF", "#FDD20EFF"),
    ("#F2EDD7FF", "#755139FF"),
    ("#006B38FF", "#101820FF"),
    ("#F95700FF", "#FFFFFFFF"),
    ("#FFD662FF", "#00539CFF"),
    ("#D7C49EFF", "#343148FF"),
    ("#FFA177FF", "#F5C7B8FF"),
    ("#DF6589FF", "#3C1053FF"),
    ("#FFE77AFF", "#2C5F2DFF"),
    ("#DD4132FF", "#9E1030FF"),
    ("#F1F4FFFF", "#A2A2A1FF"),
    ("#FCF951FF", "#422057FF"),
    ("#4B878BFF", "#D01C1FFF"),
    ("#1C1C1BFF", "#CE4A7EFF"),
    ("#00B1D2FF", "#FDDB27FF"),
    ("#79C000FF", "#FF7F41FF"),
    ("#BD7F37FF", "#A13941FF"),
    ("#E3C9CEFF", "#9FC131FF"),
    ("#00239CFF", "#E10600FF"),
)
