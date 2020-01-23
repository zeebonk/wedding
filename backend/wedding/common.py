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


COLORS = [
    ("#c2e3a4", "#61c692", "#47ac88", "#101f35", "#f11f25"),
    ("#0cb5c2", "#ebe0ca", "#f08e52", "#d5262b", "#c71442"),
    ("#70c29a", "#a3c596", "#d1742d", "#a8612a", "#c6323b"),
    ("#401c24", "#97734b", "#cfd997", "#578d70", "#2d3a4f"),
    ("#356f63", "#f4ecbf", "#e4eaea", "#d00e65", "#383234"),
    ("#577960", "#719b7c", "#dfb85e", "#db9550", "#e8843c"),
    ("#16252f", "#204252", "#6c7760", "#cac49a", "#b1cd76"),
    ("#d22531", "#cd9154", "#70715b", "#306872", "#0b9891"),
    ("#e24f4b", "#f7f0dc", "#e9ede9", "#77bab0", "#415744"),
    ("#a9374a", "#ec8c4b", "#f4e35b", "#4e7847", "#1ab29c"),
    ("#1a5169", "#c4d10d", "#fc8613", "#ef4618", "#9d1608"),
    ("#206f91", "#2c8b98", "#ddd346", "#f9bf21", "#faae32"),
    ("#2e3437", "#43665b", "#e9dd81", "#e9b882", "#b45e55"),
    ("#0c343b", "#27868a", "#bedfd5", "#88e4e1", "#f44e4f"),
    ("#4f3f47", "#67ada5", "#e8e4b3", "#f4b457", "#e97359"),
    ("#264767", "#dcdac8", "#be976a", "#ac5642", "#593028"),
    ("#e5e09c", "#c3c074", "#787c5f", "#424e4d", "#2f2a26"),
    ("#2f2233", "#38375b", "#435752", "#a89f86", "#efdabc"),
    ("#487362", "#1eaea3", "#64cf60", "#feee72", "#383337"),
    ("#fc703d", "#e99b5e", "#70ad80", "#3ec3b3", "#2eabae"),
    ("#436f3c", "#8b5737", "#e7be61", "#a63f2a", "#743021"),
    ("#f9f9e7", "#d0be81", "#b5943c", "#ae7f28", "#663d39"),
    ("#323d37", "#7c784c", "#c69838", "#d9d371", "#b7daa8"),
    ("#24656c", "#348680", "#dbde85", "#fda55b", "#d84e32"),
    ("#0f4557", "#109697", "#d3d9cd", "#f5f2e3", "#e53c41"),
    ("#563532", "#ddddcd", "#a3a6a7", "#8ba6aa", "#4d5859"),
    ("#27445a", "#527f82", "#babaa1", "#beb691", "#bf8e65"),
    ("#0a3b4a", "#1f6780", "#32a7b3", "#b9dfc9", "#ede8d0"),
    ("#fcfcfc", "#f37b77", "#fe7d88", "#975b4a", "#3c4334"),
    ("#073a49", "#04a896", "#efe053", "#f16625", "#a02633"),
    ("#b1146b", "#ca0a41", "#fbd514", "#78af0b", "#143830"),
    ("#815a4a", "#a98980", "#d9a187", "#dfa05f", "#537e62"),
    ("#253538", "#46896f", "#79cdb0", "#f1f2e9", "#fb501d"),
    ("#18343e", "#123d57", "#68a1a8", "#d0ddb5", "#ddb54a"),
    ("#d4e9a3", "#f3ac35", "#e0aabb", "#42aecf", "#5990b4"),
    ("#4c1a34", "#995368", "#f1a948", "#cbb759", "#3e5453"),
    ("#e76b1b", "#ee9f5e", "#eed8ab", "#7f8790", "#506f86"),
    ("#1e272a", "#465a37", "#96693b", "#cd9945", "#f9cb46"),
    ("#1e3038", "#4e2934", "#b40f17", "#fdf9d1", "#b93719"),
    ("#1f3843", "#507f80", "#6cbe78", "#d0dc57", "#c5d526"),
    ("#b53839", "#c6943a", "#aed76e", "#5d9e69", "#28654e"),
    ("#1f3153", "#336b73", "#508889", "#c2c0b8", "#dfd6be"),
    ("#ddd9ad", "#91a786", "#4e7763", "#2d4145", "#1e2631"),
    ("#423d47", "#777273", "#db9729", "#f2da9b", "#f9f8db"),
    ("#537576", "#e6ccb2", "#f0d294", "#bce0c2", "#5d9d99"),
    ("#304b37", "#66ad5c", "#fad088", "#dcab4b", "#a24b3f"),
    ("#b6e4ed", "#67cbab", "#cfc375", "#f9cb2e", "#df925a"),
    ("#677d0d", "#dab620", "#fd9e26", "#ed4135", "#97374e"),
    ("#6a4a75", "#422a64", "#6d2f98", "#745e94", "#b783ca"),
    ("#d4280e", "#fa9e29", "#e89158", "#67b07a", "#172b29"),
    ("#b2a749", "#849648", "#60732b", "#5d6b3f", "#564f38"),
    ("#a44940", "#b09956", "#ddd49a", "#8f8b8f", "#5d7761"),
    ("#312b33", "#454a69", "#686665", "#bba1ad", "#e6c17d"),
    ("#59a095", "#c6e1d0", "#e3e3c4", "#d3bb8e", "#cd7f71"),
    ("#2b2e2c", "#6c9b9d", "#faf9f5", "#838983", "#22201c"),
    ("#224347", "#378a43", "#cabf40", "#e3f339", "#99bb67"),
    ("#2c252e", "#464046", "#b9b1c4", "#f3f1ec", "#db575c"),
    ("#1d1f35", "#181f2b", "#242a5a", "#293356", "#353e73"),
    ("#60c6e5", "#25759c", "#c275a8", "#fcc945", "#c35329"),
    ("#4f301b", "#71913e", "#bdc658", "#4c4c28", "#581d0c"),
    ("#316694", "#6fa2be", "#f5edd9", "#e89751", "#ec624e"),
    ("#302638", "#584558", "#a29593", "#c0b6a4", "#d2b992"),
    ("#e43a2f", "#cc9665", "#94e1ce", "#0ab9d8", "#373223"),
    ("#fdb306", "#e3985d", "#965629", "#112e40", "#0c1522"),
    ("#ecd167", "#fef4be", "#5adbc6", "#a1a980", "#706b57"),
    ("#8c965d", "#d4a286", "#d86040", "#503f2e", "#3d2e26"),
    ("#f8680c", "#fba60d", "#f8e943", "#18f7f8", "#1b829a"),
    ("#f29f97", "#f24c50", "#dc554c", "#243340", "#edefe3"),
    ("#45444c", "#7e817d", "#c7a58b", "#f7f1ca", "#d14c3f"),
    ("#85a3cb", "#ccc7ee", "#e3d9da", "#c27776", "#917b37"),
    ("#2d3046", "#83735d", "#b9b62d", "#a9c418", "#c9cb28"),
    ("#221f26", "#2f3451", "#454f74", "#6792ba", "#e0e0d2"),
    ("#8ca685", "#edeaba", "#cc7665", "#5e5857", "#5f3b3c"),
    ("#bba039", "#decf86", "#aa9951", "#3e3f41", "#1d2524"),
    ("#fe2f0a", "#f09b76", "#e0ca9e", "#3aa479", "#1e534b"),
    ("#68d4e6", "#58c3c3", "#e39e44", "#ee8530", "#fc6d09"),
    ("#11242c", "#353a45", "#535e5c", "#afb8b2", "#f2f4ed"),
    ("#df5034", "#f88f68", "#d6dd6c", "#17846c", "#12674f"),
    ("#06192f", "#095573", "#0987a7", "#dfded1", "#eee8cf"),
    ("#669ba6", "#33384a", "#6a8c9d", "#efefe2", "#403739"),
    ("#10233f", "#1b6475", "#548075", "#d6b56b", "#cfe048"),
    ("#383a3a", "#808364", "#cac295", "#d2cea4", "#b2b587"),
    ("#d9cbaa", "#d7ce94", "#b49f6e", "#653f35", "#343328"),
    ("#cff5f5", "#b5c78e", "#787051", "#554035", "#58324d"),
    ("#4e4f2c", "#715e43", "#3a4c30", "#acb333", "#e3f589"),
    ("#c1c371", "#b2cd8c", "#7ba65e", "#5e976e", "#59535d"),
    ("#2e4259", "#f4493b", "#eaac9d", "#eab4a3", "#86a490"),
    ("#5eaca9", "#4ca2b2", "#8b8053", "#b8a77b", "#f8f7f0"),
    ("#342121", "#523255", "#8b7a68", "#a79e94", "#e8d4d2"),
    ("#fd6415", "#f7ce22", "#888646", "#307657", "#1a342b"),
    ("#b2b2a3", "#87a271", "#b8a664", "#d8b65d", "#ece5b3"),
    ("#2a2323", "#4f5a54", "#9bd29c", "#edd3a1", "#e77354"),
    ("#d35d55", "#dca278", "#d29c7b", "#89877e", "#608070"),
    ("#b99f86", "#faad11", "#f86c17", "#beb920", "#18aaa6"),
    ("#392238", "#59234b", "#9f2a3c", "#d9453f", "#ddab5b"),
    ("#de6234", "#5a8985", "#bbb2b1", "#dfb492", "#937b4a"),
    ("#3a444b", "#306d6d", "#2c8783", "#9fd7b1", "#dde8bf"),
    ("#442224", "#9f6852", "#cdc29f", "#7b9175", "#272b2a"),
    ("#542535", "#d5523f", "#fbb440", "#e2ba69", "#46a67f"),
    ("#19707a", "#7fa56c", "#d4be3f", "#ebba58", "#ea6350"),
]