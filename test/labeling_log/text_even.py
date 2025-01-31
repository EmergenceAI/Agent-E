run_name = "agent_e_text_validator"
rerun_name = None
base_directory = "/Users/ruhana/Agent-E/ruhana_notes/temp/All"

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
    57,
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
    113,
    115,
    121,
    123,
    129,
    131,
    137,
    139,
    145,
    155,
    161,
    163,
    169,
    179,
    185,
    187,
    193,
    195,
    201,
    203,
    209,
    211,
    217,
    219,
    225,
    227,
    233,
    235,
    241,
    243,
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
]
missing_screenshots = [41, 49, 57, 65, 73, 91, 99, 107, 115, 123, 131, 139, 155, 163, 193]
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

# 58 labeled here
# Missing 248 from this half!
