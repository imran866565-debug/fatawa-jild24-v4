#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 24 easy-Urdu tashreeh v4 chunks into jild-24.json.

Reads the 17 leaf chunk files listed in chunks-manifest-v4-jild24.json,
concatenates them in order 01 -> 02 -> ... -> 10 -> 11a -> 11b -> 12
-> ... -> 16, JOINS the 3 simple duplicate-id groups (masala-18
[120]+[121-125], sawal CONCAT; masala-166 [416-417]+[418-450], sawal
FIRST; masala-250 [571-600]+[601-643], sawal FIRST) and the 1
cross-id group (masala-84: head jild24-masala-84 [216-250] +
jild24-risala-139 tail [251-284]) into single items, STABLE SORTS by
start_page (mirroring the v3 merge), derives start_page = min(pages)
where the field is absent (0 derived: all chunks carry start_page),
normalises page markers, validates, and writes {"masail": [...]} to
jild-24.json.

ORDER -- chunk order is the order, then a stable sort by start_page:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-24.json
  has ID order == stable sort by start_page of the concatenation
  (verified locally by the coordinator: the v3 order IS the stable
  sort, including its tied start_pages). Do NOT sort or reorder before
  the joins. Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit 17-leaf list (11a/11b break the numeric
  range pattern).

JOINS: parts are found BY ID anywhere in the list. Parts must be in
  ascending page order. Sawal modes: "concat" (masala-18 — BOTH parts
  carry a sawal; joined sawal = " ".join of both stripped sawals),
  "first" (masala-166, masala-250 — the single non-empty sawal, in
  the first part), "head_only" (masala-84 — the head's sawal; the
  tail has an empty sawal). Titles: the joined title is the
  FIRST/HEAD part's title, asserted against the embedded merged-v3
  title (V3_TITLES). title_must_match is deliberately NOT used: the
  two halves' titles differ by design in the v3 chunks (the tail
  titles carry the risala continuation wording).
  masala-18 [120, 121-125], masala-166 [416-417, 418-450],
  masala-250 [571-600, 601-643].
CROSS-ID JOIN (1):
  masala-84: c04 head jild24-masala-84 [216-250] (sawal) + c05
    jild24-risala-139 [251-284] (sawal empty) -> ONE item
    jild24-masala-84 [216-284], 69 pages; title from the HEAD (==
    merged-v3 title); the rename is effected by the combine.
    Net -1 item.
  After the joins there are 207 items and 207 unique ids — the
  duplicate-id assertion runs AFTER the joins, not before.
  NO renames at merge: the tail id is absorbed by its cross-id join;
  no print-error renames were applied in the leaves.
  All chunks carry start_page == min(pages) (0 derived).
  Pages are shared between items by design (a boundary page belongs
  to two items): item-page sum is 804, unique pages 640. Every page
  assertion uses SETS.
  EMPTY JAWAB: exactly one item, jild24-masala-64 [196], has an empty
  jawab — empty in the v3 merged file / source itself. It is
  allow-listed below; every other item must have a jawab.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild24.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = ["jild-24-chunk-01.json", "jild-24-chunk-02.json", "jild-24-chunk-03.json", "jild-24-chunk-04.json", "jild-24-chunk-05.json", "jild-24-chunk-06.json", "jild-24-chunk-07.json", "jild-24-chunk-08.json", "jild-24-chunk-09.json", "jild-24-chunk-10.json", "jild-24-chunk-11a.json", "jild-24-chunk-11b.json", "jild-24-chunk-12.json", "jild-24-chunk-13.json", "jild-24-chunk-14.json", "jild-24-chunk-15.json", "jild-24-chunk-16.json"]

EXPECTED_ITEMS = 207
EXPECTED_PAGES = 640
EXPECTED_MIN_PAGE = 6
EXPECTED_MAX_PAGE = 720
EXPECTED_VOLUME_IDS = {39}
EXPECTED_FIRST_ID = "jild24-pesh-lafz"
EXPECTED_LAST_ID = "jild24-masala-284"

# v3 ID sequence, verbatim from content/tashreeh/jild-24.json.
V3_IDS = ["jild24-pesh-lafz", "jild24-masala-1", "jild24-masala-2", "jild24-masala-3", "jild24-masala-4-12", "jild24-masala-13", "jild24-masala-14", "jild24-masala-15", "jild24-masala-16", "jild24-masala-17", "jild24-masala-18", "jild24-masala-19", "jild24-masala-20", "jild24-masala-21", "jild24-masala-22", "jild24-masala-23", "jild24-masala-24", "jild24-masala-25-27", "jild24-masala-28", "jild24-masala-29", "jild24-masala-30", "jild24-masala-31", "jild24-masala-32", "jild24-masala-33", "jild24-masala-34", "jild24-masala-35", "jild24-masala-36", "jild24-masala-37", "jild24-masala-38", "jild24-masala-39-41", "jild24-masala-42-46", "jild24-masala-47", "jild24-masala-48", "jild24-masala-49", "jild24-masala-50", "jild24-masala-51", "jild24-masala-52", "jild24-masala-53", "jild24-masala-54", "jild24-masala-55", "jild24-masala-56", "jild24-masala-57", "jild24-masala-58", "jild24-masala-59", "jild24-masala-60", "jild24-masala-61", "jild24-masala-62", "jild24-masala-63", "jild24-masala-64", "jild24-masala-65", "jild24-masala-66", "jild24-masala-67", "jild24-masala-68", "jild24-masala-70", "jild24-masala-71", "jild24-masala-72", "jild24-masala-73", "jild24-masala-74", "jild24-masala-75", "jild24-masala-76", "jild24-masala-77", "jild24-masala-78", "jild24-masala-79", "jild24-masala-80", "jild24-masala-81", "jild24-masala-82", "jild24-masala-83", "jild24-masala-84", "jild24-masala-85-93", "jild24-masala-94", "jild24-masala-95", "jild24-masala-96", "jild24-masala-97", "jild24-masala-98", "jild24-masala-99", "jild24-masala-100", "jild24-masala-101", "jild24-masala-102", "jild24-masala-103", "jild24-masala-104", "jild24-masala-105", "jild24-masala-106", "jild24-masala-107", "jild24-masala-108", "jild24-masala-109", "jild24-masala-110", "jild24-masala-111", "jild24-masala-112", "jild24-masala-113", "jild24-masala-114", "jild24-masala-115", "jild24-masala-116", "jild24-masala-117", "jild24-masala-121", "jild24-masala-122", "jild24-masala-123", "jild24-masala-124", "jild24-masala-125", "jild24-masala-126", "jild24-masala-127", "jild24-masala-128", "jild24-masala-129", "jild24-masala-130", "jild24-masala-136", "jild24-masala-137", "jild24-masala-138", "jild24-masala-139", "jild24-masala-140", "jild24-masala-142", "jild24-masala-143", "jild24-masala-145", "jild24-masala-146", "jild24-masala-148", "jild24-masala-150", "jild24-masala-151", "jild24-masala-153", "jild24-masala-155", "jild24-masala-156", "jild24-masala-157", "jild24-masala-158", "jild24-masala-159", "jild24-masala-160", "jild24-masala-161", "jild24-masala-162", "jild24-masala-163", "jild24-masala-164", "jild24-masala-165", "jild24-masala-166", "jild24-masala-167", "jild24-masala-168", "jild24-masala-169-171", "jild24-masala-172", "jild24-masala-173", "jild24-masala-174", "jild24-masala-175-178", "jild24-masala-179", "jild24-masala-180", "jild24-masala-181", "jild24-masala-182-183", "jild24-masala-184", "jild24-masala-185", "jild24-masala-186", "jild24-masala-187-191", "jild24-masala-192", "jild24-masala-193", "jild24-masala-194", "jild24-masala-195", "jild24-masala-196", "jild24-masala-197-203", "jild24-masala-204", "jild24-masala-205", "jild24-masala-206", "jild24-masala-207-219", "jild24-masala-220", "jild24-masala-221", "jild24-masala-222", "jild24-masala-223", "jild24-masala-224", "jild24-masala-225", "jild24-masala-226", "jild24-masala-227", "jild24-masala-228", "jild24-masala-229", "jild24-masala-230-232", "jild24-masala-233", "jild24-masala-234", "jild24-masala-235", "jild24-masala-236", "jild24-masala-237-241", "jild24-masala-242", "jild24-masala-243", "jild24-masala-244", "jild24-masala-245", "jild24-masala-246", "jild24-masala-247", "jild24-masala-248", "jild24-masala-249", "jild24-masala-250", "jild24-masala-251", "jild24-masala-252", "jild24-masala-253", "jild24-masala-254", "jild24-masala-255", "jild24-masala-256", "jild24-masala-257", "jild24-masala-258-260", "jild24-masala-261", "jild24-masala-262", "jild24-masala-263", "jild24-masala-264", "jild24-masala-265", "jild24-masala-266", "jild24-masala-267", "jild24-masala-268", "jild24-masala-269", "jild24-masala-270-272", "jild24-masala-273", "jild24-masala-274", "jild24-masala-275", "jild24-masala-276-277", "jild24-masala-278", "jild24-masala-279", "jild24-masala-280", "jild24-masala-281", "jild24-masala-282", "jild24-masala-283", "jild24-masala-284"]

# v3 pages per item id, verbatim from content/tashreeh/jild-24.json.
V3_PAGES = {
    "jild24-pesh-lafz": [6, 7, 8, 9, 10, 11],
    "jild24-masala-1": [76, 77, 78, 79],
    "jild24-masala-2": [79, 80, 81, 82, 83, 84, 85, 86],
    "jild24-masala-3": [86, 87],
    "jild24-masala-4-12": [87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
    "jild24-masala-13": [111, 112, 113],
    "jild24-masala-14": [113],
    "jild24-masala-15": [113, 114],
    "jild24-masala-16": [114, 115, 116, 117, 118, 119, 120],
    "jild24-masala-17": [120],
    "jild24-masala-18": [120, 121, 122, 123, 124, 125],
    "jild24-masala-19": [125, 126, 127, 128],
    "jild24-masala-20": [128, 129, 130, 131, 132, 133, 134],
    "jild24-masala-21": [134],
    "jild24-masala-22": [134],
    "jild24-masala-23": [135],
    "jild24-masala-24": [135],
    "jild24-masala-25-27": [135, 136, 137],
    "jild24-masala-28": [137, 138],
    "jild24-masala-29": [138],
    "jild24-masala-30": [139],
    "jild24-masala-31": [139, 140],
    "jild24-masala-32": [140],
    "jild24-masala-33": [140, 141],
    "jild24-masala-34": [141, 142],
    "jild24-masala-35": [142],
    "jild24-masala-36": [142],
    "jild24-masala-37": [142, 143],
    "jild24-masala-38": [143, 144],
    "jild24-masala-39-41": [144, 145],
    "jild24-masala-42-46": [146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166],
    "jild24-masala-47": [168],
    "jild24-masala-48": [169],
    "jild24-masala-49": [169, 170, 171, 172, 173],
    "jild24-masala-50": [173, 174],
    "jild24-masala-51": [174, 175],
    "jild24-masala-52": [175],
    "jild24-masala-53": [175],
    "jild24-masala-54": [176],
    "jild24-masala-55": [178, 179],
    "jild24-masala-56": [179, 180],
    "jild24-masala-57": [180, 181, 182],
    "jild24-masala-58": [182, 183, 184, 185, 186, 187],
    "jild24-masala-59": [188, 189, 190],
    "jild24-masala-60": [190, 191, 192, 193],
    "jild24-masala-61": [193, 194],
    "jild24-masala-62": [194, 195],
    "jild24-masala-63": [195, 196],
    "jild24-masala-64": [196],
    "jild24-masala-65": [197],
    "jild24-masala-66": [197, 198],
    "jild24-masala-67": [198],
    "jild24-masala-68": [198, 199],
    "jild24-masala-70": [199, 200, 201],
    "jild24-masala-71": [201, 202],
    "jild24-masala-72": [202],
    "jild24-masala-73": [202, 203],
    "jild24-masala-74": [204, 205],
    "jild24-masala-75": [205, 206],
    "jild24-masala-76": [206, 207],
    "jild24-masala-77": [207],
    "jild24-masala-78": [207],
    "jild24-masala-79": [207, 208],
    "jild24-masala-80": [208],
    "jild24-masala-81": [208, 209],
    "jild24-masala-82": [209],
    "jild24-masala-83": [209, 210, 211, 212, 213, 214, 215],
    "jild24-masala-84": [216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284],
    "jild24-masala-85-93": [286, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312],
    "jild24-masala-94": [313, 314, 315, 316, 317, 318, 319, 320, 321],
    "jild24-masala-95": [322, 323],
    "jild24-masala-96": [323, 324],
    "jild24-masala-97": [324, 325],
    "jild24-masala-98": [325],
    "jild24-masala-99": [325, 326, 327],
    "jild24-masala-100": [327, 328],
    "jild24-masala-101": [328, 329],
    "jild24-masala-102": [329, 330],
    "jild24-masala-103": [330],
    "jild24-masala-104": [330],
    "jild24-masala-105": [330, 331],
    "jild24-masala-106": [331],
    "jild24-masala-107": [331],
    "jild24-masala-108": [332, 333, 334, 335, 336, 337, 338],
    "jild24-masala-109": [339, 340],
    "jild24-masala-110": [340, 341],
    "jild24-masala-111": [340, 341, 342],
    "jild24-masala-112": [342, 343],
    "jild24-masala-113": [343, 344],
    "jild24-masala-114": [345],
    "jild24-masala-115": [345, 346],
    "jild24-masala-116": [346, 347],
    "jild24-masala-117": [347, 348, 349, 350],
    "jild24-masala-121": [350, 351],
    "jild24-masala-122": [351, 352],
    "jild24-masala-123": [351, 352],
    "jild24-masala-124": [353, 354],
    "jild24-masala-125": [354, 355, 356, 357],
    "jild24-masala-126": [357, 358],
    "jild24-masala-127": [358],
    "jild24-masala-128": [358, 359],
    "jild24-masala-129": [359, 360],
    "jild24-masala-130": [361, 362, 363],
    "jild24-masala-136": [363, 364],
    "jild24-masala-137": [364, 365],
    "jild24-masala-138": [366, 368, 369, 370],
    "jild24-masala-139": [370],
    "jild24-masala-140": [370, 371],
    "jild24-masala-142": [371, 372],
    "jild24-masala-143": [372, 373],
    "jild24-masala-145": [372, 373],
    "jild24-masala-146": [373],
    "jild24-masala-148": [374],
    "jild24-masala-150": [374, 375, 376, 377, 378, 379],
    "jild24-masala-151": [379, 380],
    "jild24-masala-153": [380, 381],
    "jild24-masala-155": [381],
    "jild24-masala-156": [381, 382],
    "jild24-masala-157": [382, 383, 384],
    "jild24-masala-158": [385, 386, 387, 388],
    "jild24-masala-159": [388, 389],
    "jild24-masala-160": [389, 390, 391, 392, 393],
    "jild24-masala-161": [393],
    "jild24-masala-162": [393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404],
    "jild24-masala-163": [404, 405, 406, 407, 408, 409],
    "jild24-masala-164": [409, 410, 411, 412, 413, 414],
    "jild24-masala-165": [414, 415, 416],
    "jild24-masala-166": [416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450],
    "jild24-masala-167": [451, 452, 454, 455, 456, 457, 458],
    "jild24-masala-168": [459, 460, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477],
    "jild24-masala-169-171": [478, 479, 480, 481, 482, 483, 484, 485],
    "jild24-masala-172": [486, 487],
    "jild24-masala-173": [487, 488, 489],
    "jild24-masala-174": [489],
    "jild24-masala-175-178": [489],
    "jild24-masala-179": [490],
    "jild24-masala-180": [490, 491, 492, 493],
    "jild24-masala-181": [493, 494, 495, 496, 497],
    "jild24-masala-182-183": [498, 499],
    "jild24-masala-184": [499, 500],
    "jild24-masala-185": [500],
    "jild24-masala-186": [500, 501],
    "jild24-masala-187-191": [501, 502],
    "jild24-masala-192": [502],
    "jild24-masala-193": [502, 503],
    "jild24-masala-194": [504],
    "jild24-masala-195": [504],
    "jild24-masala-196": [504, 505, 506],
    "jild24-masala-197-203": [506, 507, 508],
    "jild24-masala-204": [508],
    "jild24-masala-205": [508],
    "jild24-masala-206": [509],
    "jild24-masala-207-219": [509, 510, 511],
    "jild24-masala-220": [512, 513, 514],
    "jild24-masala-221": [514, 515, 516, 517],
    "jild24-masala-222": [517, 518, 519, 520, 521],
    "jild24-masala-223": [521, 522, 523, 524],
    "jild24-masala-224": [524],
    "jild24-masala-225": [524, 525, 526, 527],
    "jild24-masala-226": [527],
    "jild24-masala-227": [528],
    "jild24-masala-228": [529, 530, 532, 533, 534, 535, 536],
    "jild24-masala-229": [536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553],
    "jild24-masala-230-232": [554],
    "jild24-masala-233": [555, 556],
    "jild24-masala-234": [556],
    "jild24-masala-235": [556],
    "jild24-masala-236": [556, 557],
    "jild24-masala-237-241": [557, 558],
    "jild24-masala-242": [558, 559],
    "jild24-masala-243": [559],
    "jild24-masala-244": [560, 561, 562],
    "jild24-masala-245": [562, 563, 564, 565, 566, 567],
    "jild24-masala-246": [567, 568],
    "jild24-masala-247": [568, 569],
    "jild24-masala-248": [569],
    "jild24-masala-249": [569, 570],
    "jild24-masala-250": [571, 572, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643],
    "jild24-masala-251": [644, 645, 646],
    "jild24-masala-252": [646, 647, 648, 649, 650, 651, 652, 653, 654],
    "jild24-masala-253": [654, 655],
    "jild24-masala-254": [655, 656, 657, 658, 659],
    "jild24-masala-255": [659, 660],
    "jild24-masala-256": [660],
    "jild24-masala-257": [660],
    "jild24-masala-258-260": [661],
    "jild24-masala-261": [661],
    "jild24-masala-262": [662],
    "jild24-masala-263": [662],
    "jild24-masala-264": [662, 663],
    "jild24-masala-265": [664, 665],
    "jild24-masala-266": [665],
    "jild24-masala-267": [665, 666],
    "jild24-masala-268": [666, 667, 668, 669],
    "jild24-masala-269": [669, 670],
    "jild24-masala-270-272": [670, 671],
    "jild24-masala-273": [671, 672],
    "jild24-masala-274": [672, 673],
    "jild24-masala-275": [673],
    "jild24-masala-276-277": [673, 674, 675, 676],
    "jild24-masala-278": [677, 678, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708],
    "jild24-masala-279": [709, 710, 712, 713, 714],
    "jild24-masala-280": [714],
    "jild24-masala-281": [714, 715],
    "jild24-masala-282": [716, 717],
    "jild24-masala-283": [717, 718, 719],
    "jild24-masala-284": [719, 720],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 17, f"expected 17 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

        # SIMPLE JOINS (3): parts found BY ID anywhere. Sawal modes:
    # "concat" (masala-18 — both parts carry a sawal; joined sawal
    # is " ".join of both stripped sawals) and "first" (masala-166,
    # masala-250 — the single non-empty sawal, in the first part).
    # CROSS-ID JOIN (1): masala-84 (head + risala-139 tail). Sawal = head.

    def join_consecutive(item_id, expected_parts, seam_checks, sawal_mode="first", title_suffix=None):
        idxs = [i for i, it in enumerate(all_items) if it["id"] == item_id]
        assert len(idxs) == expected_parts, (
            f"{item_id}: expected {expected_parts} parts, found {len(idxs)}"
        )
        parts = [all_items[i] for i in idxs]
        assert [min(p["pages"]) for p in parts] == sorted(min(p["pages"]) for p in parts), (
            f"{item_id}: parts not in page order"
        )
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{item_id}: volume mismatch {vols}"
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{item_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{item_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        if sawal_mode == "first":
            sawals = [p.get("tashreeh_sawal") for p in parts if p.get("tashreeh_sawal")]
            assert len(sawals) <= 1, f"{item_id}: {len(sawals)} non-empty sawals"
            if sawals:
                assert parts[0].get("tashreeh_sawal"), f"{item_id}: non-empty sawal not in first part"
            sawal = sawals[0] if sawals else ""
        elif sawal_mode == "concat":
            assert all(p.get("tashreeh_sawal") for p in parts), f"{item_id}: concat needs all sawals"
            sawal = " ".join(p["tashreeh_sawal"].strip() for p in parts)
        else:
            raise AssertionError(f"{item_id}: unknown sawal_mode {sawal_mode}")
        title = parts[0]["title"]
        if title_suffix:
            assert title.endswith(title_suffix), f"{item_id}: first-part title lacks suffix {title_suffix!r}"
            assert all(p["title"].endswith(title_suffix) for p in parts), f"{item_id}: a part title lacks the suffix"
            title = title[: -len(title_suffix)]
        assert title == V3_TITLES[item_id], f"{item_id}: joined title != v3 title"
        pages = sorted({p for part in parts for p in part["pages"]})
        # No simple join in Jild 24 is also a CROSS-JOIN head:
        # cross tails belong to the cross join only.
        cross_tails = {}
        cross_tail_pages = {p for t in cross_tails.get(item_id, []) for it in all_items if it["id"] == t for p in it["pages"]}
        assert pages == sorted(set(V3_PAGES[item_id]) - cross_tail_pages), f"{item_id}: joined pages != v3"
        joined = {
            "id": item_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": sawal,
            "tashreeh_jawab": " ".join(p["tashreeh_jawab"].strip() for p in parts if p.get("tashreeh_jawab")),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"joined {item_id}: {expected_parts} parts -> 1 item, {len(pages)} pages")

    def join_cross_id(result_id, head_id, tail_ids, sawal_mode, seam_checks):
        seq = [head_id] + tail_ids
        idxs = [i for i, it in enumerate(all_items) if it["id"] in seq]
        assert [all_items[i]["id"] for i in idxs] == seq, (
            f"{result_id}: cross-id order mismatch"
        )
        parts = [all_items[i] for i in idxs]
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{result_id}: volume mismatch {vols}"
        if sawal_mode == "head_only":
            assert parts[0].get("tashreeh_sawal"), f"{result_id}: head sawal empty"
            assert all(not p.get("tashreeh_sawal") for p in parts[1:]), (
                f"{result_id}: a tail sawal is non-empty"
            )
            sawal = parts[0]["tashreeh_sawal"]
        else:
            raise AssertionError(f"{result_id}: unknown sawal_mode {sawal_mode}")
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{result_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{result_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        pages = sorted({p for part in parts for p in part["pages"]})
        assert pages == V3_PAGES[result_id], f"{result_id}: joined pages != v3"
        title = parts[0]["title"]
        assert title == V3_TITLES[result_id], f"{result_id}: joined title != v3 title"
        joined = {
            "id": result_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": sawal,
            "tashreeh_jawab": " ".join(p["tashreeh_jawab"].strip() for p in parts if p.get("tashreeh_jawab")),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"joined {result_id}: {1 + len(tail_ids)} parts -> 1 item, {len(pages)} pages")

    V3_TITLES = {
        "jild24-masala-18": "مسئلہ ۱۸: فونوگراف سے مغنیہ کا گانا سننا",
        "jild24-masala-166": "مسئلہ ۱۶۶: استاد کو ہٹا کر شاگرد کا امام بننا (سوال)",
        "jild24-masala-250": "رسالہ العطایا القدیر فی حکم التصویر — پیر ابراہیم بغدادی کی فوٹو تبرکاً رکھنا اور برزخ جمانا",
        "jild24-masala-84": "مسئلہ ۸۴: بیماری کے شکار شخص سے اجتناب کا حکم (رسالہ الحق المجتلٰی فی حکم المبتلٰی)",
    }

    join_consecutive(
        "jild24-masala-18", 2,
        [
            (1, "start", "جواب میں اعلیٰ حضرت فرماتے ہیں کہ یہ مضمون کہ منہ پر کپڑا ڈال کر رنڈیوں اور ڈومن"),
        ],
        sawal_mode="concat",
        title_suffix=None,
    )
    join_consecutive(
        "jild24-masala-166", 2,
        [
            (1, "start", "صفحہ ۴۱۸ سے جواب شروع ہوتا ہے، اور اعلیٰ حضرت رحمۃ اللہ علیہ پہلے اللہ تعالیٰ سے"),
        ],
        sawal_mode="first",
        title_suffix=None,
    )
    join_consecutive(
        "jild24-masala-250", 2,
        [
            (0, "end", "ا۔ اور یہ حدیث یہیں صفحہ ۶۰۰ پر ادھوری رہ جاتی ہے اور جواب chunk 14 میں جاری ہے۔"),
            (1, "start", "جواب کا یہ حصہ اسی تحقیق کو آگے بڑھاتا ہے جو رسالے کے پہلے حصے میں شروع ہوئی تھی"),
        ],
        sawal_mode="first",
        title_suffix=None,
    )
    join_cross_id(
        "jild24-masala-84",
        "jild24-masala-84",
        ["jild24-risala-139"],
        "head_only",
        [
            (0, "end", "یہ وسلم نے دونوں کلاموں کو ایک ترتیب (نسق واحد) میں جمع فرمایا، پھر نسخ کہاں ہے۔"),
            (1, "start", "اعلیٰ حضرت رحمۃ اللہ علیہ اس حصے میں سب سے پہلے یہ واضح فرماتے ہیں کہ حضور صلی ا"),
        ],
    )
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS after joins: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )

    print(f"after joins: {len(all_items)} items (211 concatenated)")
    # NO renames at merge: the tail id (jild24-risala-139)
    # is absorbed by its cross-id join.
    print("renames applied: [] (tail absorbed by cross-id join)")
    # STABLE SORT by start_page, mirroring the v3 merge.
    all_items.sort(key=lambda it: it["start_page"])
    print(f"sorted by start_page: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    # jild24-masala-64 [196] has an empty jawab in the v3 merged
    # file / source itself (allow-listed); every other item must
    # have a jawab.
    assert set(empty) == {"jild24-masala-64"}, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-24.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-24.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
