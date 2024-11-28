run_name = "agent_e_text_vision"
rerun_name = "agent_e_text_rerun"
base_directory = "/Users/ruhana/Agent-E/ruhana_notes/All/"

should_be_labeled = set(range(1, 642, 2))
originally_labeled = [
    1,
    3,
    9,
    11,
    17,
    25,
    27,
    33,
    35,
    41,
    43,
    49,
    51,
    59,
    65,
    67,
    73,
    75,
    81,
    83,
    89,
    91,
    97,
    99,
    105,
    107,
    115,
    121,
    129,
    131,
    137,
    139,
    145,
    147,
    153,
    155,
    161,
    169,
    171,
    179,
    187,
    193,
    195,
    201,
    209,
    211,
    217,
    233,
    249,
    251,
    257,
    259,
    265,
    267,
    273,
    275,
    281,
    283,
    289,
    291,
    299,
    305,
    313,
    315,
    321,
    323,
    329,
    331,
    337,
    339,
    345,
    347,
    353,
    355,
    361,
    363,
    369,
    371,
    377,
    379,
    385,
    387,
    393,
    395,
    401,
    403,
    409,
    411,
    417,
    419,
    425,
    427,
    433,
    435,
    441,
    443,
    457,
    459,
    467,
    473,
    475,
    481,
    489,
    491,
    497,
    499,
    505,
    507,
    513,
    515,
    521,
    523,
    529,
    531,
    537,
    539,
    545,
    547,
    553,
    555,
    561,
    563,
    569,
    571,
    579,
    585,
    587,
    593,
    595,
    609,
    617,
    627,
    635,
]
missing_screenshots = [137, 217]
validation_zero = []
timeouts = []
never_labeled = sorted(should_be_labeled - set(originally_labeled))
# print(f"Never Labled: {never_labeled}") # some one person's labeled are missing!!!!

should_be_relabeled = validation_zero + timeouts + never_labeled


actually_relabeled = []

# relabel assignments
amal = []
lakshmi = []
ramya = []
shalini = []
jyostna = []
satendra = []
asked_to_relabel = lakshmi + ramya + satendra + jyostna + amal + shalini

annototaed_by_someone = sorted(set(actually_relabeled) - set(asked_to_relabel))  # idk when or why
asked_to_relabel = asked_to_relabel + annototaed_by_someone


# where_annotators_fucked_up = sorted(set(asked_to_relabel) - set(actually_relabeled))
# print(f"Annotators messed up {len(where_annotators_fucked_up)} times! \n\t{where_annotators_fucked_up}]\n")

# where_i_fucked_up =  sorted(set(should_be_relabeled) - set(asked_to_relabel))
# print(f"I messed up {len(where_i_fucked_up)} times! \n\t{where_i_fucked_up}\n")

# what_is_actually_missing =  set(should_be_labeled) - set(originally_labeled + actually_relabeled)
# print(f"Data fully missing (with errors), {len(what_is_actually_missing)} times: {what_is_actually_missing}")


# labeled proper might not be 100% correct if reruns need to be done again...
labeled_proper = (set(originally_labeled) - set(should_be_relabeled)) | set(actually_relabeled)
should_be_redone = sorted(set(should_be_labeled) - labeled_proper)
print(f"{len(should_be_redone)} tasks still need to be run for proper results, : {should_be_redone}")
print(f"{len(labeled_proper)} is finished")

# 1 items need to be relabeled (actually)
# 4 items are fully missing
# 5 items should be relabeled
