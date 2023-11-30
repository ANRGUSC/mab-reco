# This is a sample code on how to generate simulated users (fake users) for model testing. The code is an example to generate
# simulated users with a certain behavior pattern followed by the Gaussain's Distribution (normal distribution).

import numpy as np
from MABInstance import MABInstance
import datetime
import pytz
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# We have three platforms for now, in here for testing purpose, I store all simulated user data all in the discord folder.
PLATFORM = "discord"
USER_HASH_PREFIX = "sim_"
NUM_SAMPLES = 50

# User configuration, suppose these users loves snacks, all other suggestions will end up with 0~3 feedback
user_context_0 = [0, 1, 2, 3, 4, 5]
user_context_1 = [0, 1, 2, 3, 4, 5]
user_context_2 = [0, 1, 2, 3, 4, 5]
user_context_3 = [0, 1, 2, 3, 4, 5]
user_context_4 = [0, 1, 2, 3, 4, 5]
user_config_0 = {
    0: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    1: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    2: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    4: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    }
}
user_config_1 = {
    0: {
        0: {'mean': 2, 'std_dev': 0.8},
        1: {'mean': 2, 'std_dev': 0.9},
        2: {'mean': 2, 'std_dev': 0.4},
        3: {'mean': 2, 'std_dev': 0.3},
        4: {'mean': 2, 'std_dev': 0.9},
        5: {'mean': 2, 'std_dev': 0.7},
        6: {'mean': 2, 'std_dev': 0.6},
        7: {'mean': 5, 'std_dev': 0.8},
        8: {'mean': 2, 'std_dev': 0.6},
        9: {'mean': 2, 'std_dev': 0.7}
    },
    1: {
        0: {'mean': 2, 'std_dev': 0.2},
        1: {'mean': 2, 'std_dev': 0.4},
        2: {'mean': 2, 'std_dev': 0.6},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 2, 'std_dev': 0.9},
        5: {'mean': 2, 'std_dev': 0.4},
        6: {'mean': 2, 'std_dev': 0.4},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.7},
        9: {'mean': 2, 'std_dev': 0.7}
    },
    2: {
        0: {'mean': 2, 'std_dev': 0.7},
        1: {'mean': 2, 'std_dev': 0.9},
        2: {'mean': 2, 'std_dev': 0.7},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 2, 'std_dev': 0.7},
        5: {'mean': 2, 'std_dev': 0.7},
        6: {'mean': 2, 'std_dev': 0.7},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.6},
        9: {'mean': 2, 'std_dev': 0.5}
    },
    3: {
        0: {'mean': 2, 'std_dev': 0.3},
        1: {'mean': 2, 'std_dev': 0.1},
        2: {'mean': 2, 'std_dev': 0.8},
        3: {'mean': 2, 'std_dev': 0.9},
        4: {'mean': 2, 'std_dev': 0.6},
        5: {'mean': 2, 'std_dev': 0.5},
        6: {'mean': 2, 'std_dev': 0.7},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.4},
        9: {'mean': 2, 'std_dev': 0.8}
    },
    4: {
        0: {'mean': 2, 'std_dev': 0.1},
        1: {'mean': 2, 'std_dev': 0.6},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 2, 'std_dev': 0.9},
        5: {'mean': 2, 'std_dev': 0.4},
        6: {'mean': 2, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.4},
        9: {'mean': 2, 'std_dev': 0.2}
    },
    5: {
        0: {'mean': 2, 'std_dev': 0.8},
        1: {'mean': 2, 'std_dev': 0.9},
        2: {'mean': 2, 'std_dev': 0.4},
        3: {'mean': 2, 'std_dev': 0.3},
        4: {'mean': 2, 'std_dev': 0.8},
        5: {'mean': 2, 'std_dev': 0.9},
        6: {'mean': 2, 'std_dev': 0.7},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.2},
        9: {'mean': 2, 'std_dev': 0.3}
    }
}
user_config_2 = {
    0: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 1, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 1, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    1: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 1, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    2: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 3, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    3: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 0, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    4: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 1, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    5: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 3, 'std_dev': 1}
    }
}
user_config_3 = {
    0: {
        0: {'mean': 3, 'std_dev': 1},
        1: {'mean': 1, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 1, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    1: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 1, 'std_dev': 1},
        2: {'mean': 1, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 1, 'std_dev': 1},
        5: {'mean': 1, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    2: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 1, 'std_dev': 1},
        2: {'mean': 1, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 1, 'std_dev': 1},
        5: {'mean': 1, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 1, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    3: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 1, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 1, 'std_dev': 1}
    },
    4: {
        0: {'mean': 1, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 1, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 1, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 1, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    }
}
user_config_4 = {
    0: {
        0: {'mean': 2, 'std_dev': 0.1},
        1: {'mean': 2, 'std_dev': 0.1},
        2: {'mean': 2, 'std_dev': 0.2},
        3: {'mean': 2, 'std_dev': 0.2},
        4: {'mean': 2, 'std_dev': 0.3},
        5: {'mean': 2, 'std_dev': 0.1},
        6: {'mean': 2, 'std_dev': 0.1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.2},
        9: {'mean': 2, 'std_dev': 0.4}
    },
    1: {
        0: {'mean': 2, 'std_dev': 0.6},
        1: {'mean': 2, 'std_dev': 0.1},
        2: {'mean': 2, 'std_dev': 0.2},
        3: {'mean': 2, 'std_dev': 0.3},
        4: {'mean': 2, 'std_dev': 0.4},
        5: {'mean': 2, 'std_dev': 0.4},
        6: {'mean': 2, 'std_dev': 0.4},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.2},
        9: {'mean': 2, 'std_dev': 0.4}
    },
    2: {
        0: {'mean': 2, 'std_dev': 0.1},
        1: {'mean': 2, 'std_dev': 0.1},
        2: {'mean': 2, 'std_dev': 0.9},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 0.7},
        5: {'mean': 2, 'std_dev': 0.5},
        6: {'mean': 2, 'std_dev': 0.7},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 0.4},
        9: {'mean': 2, 'std_dev': 0.3}
    },
    3: {
        0: {'mean': 2, 'std_dev': 0.1},
        1: {'mean': 2, 'std_dev': 2},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 0.5},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    4: {
        0: {'mean': 2, 'std_dev': 0.2},
        1: {'mean': 2, 'std_dev': 0.1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1},
        1: {'mean': 2, 'std_dev': 1},
        2: {'mean': 2, 'std_dev': 1},
        3: {'mean': 2, 'std_dev': 1},
        4: {'mean': 2, 'std_dev': 1},
        5: {'mean': 2, 'std_dev': 1},
        6: {'mean': 2, 'std_dev': 1},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 2, 'std_dev': 1},
        9: {'mean': 2, 'std_dev': 1}
    }
}
# -------------------------------------------------------------------------------
# Suppose those five users only use the app during work, ratings various depending on choice
user_context_5 = [0]
user_context_6 = [0]
user_context_7 = [0]
user_context_8 = [0]
user_context_9 = [0]
user_config_5 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 1, 'std_dev': 1.3},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 4, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 2, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 4, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    }
}
user_config_6 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 1, 'std_dev': 1.3},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 4, 'std_dev': 0.5},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 2, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 4, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.2}
    }
}
user_config_7 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 1, 'std_dev': 1.1},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 4, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 2, 'std_dev': 0.7},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 4, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.2}
    }
}
user_config_8 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 1, 'std_dev': 0.8},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 4, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 2, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 4, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    }
}
user_config_9 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 1, 'std_dev': 0.5},
        3: {'mean': 2, 'std_dev': 0.7},
        4: {'mean': 4, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 2, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.3},
        8: {'mean': 4, 'std_dev': 0.7},
        9: {'mean': 5, 'std_dev': 0.7}
    }
}
# -------------------------------------------------------------------------------
# Suppose those five users are travelers, they use the app during commute and travel, likes stretching, listen to music, and quick walk
user_context_10 = [1, 3, 5]
user_context_11 = [1, 3, 5]
user_context_12 = [1, 3, 5]
user_context_13 = [1, 3, 5]
user_context_14 = [1, 3, 5]
user_config_10 = {
    1: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    }
}
user_config_11 = {
        1: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    }
}
user_config_12 = {
        1: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    }
}
user_config_13 = {
        1: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    }
}
user_config_14 = {
        1: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    3: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    },
    5: {
        0: {'mean': 2, 'std_dev': 1.2},
        1: {'mean': 5, 'std_dev': 0.3},
        2: {'mean': 2, 'std_dev': 0.5},
        3: {'mean': 5, 'std_dev': 0.3},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 4, 'std_dev': 0.8},
        6: {'mean': 3, 'std_dev': 0.5},
        7: {'mean': 3, 'std_dev': 0.1},
        8: {'mean': 3, 'std_dev': 0.1},
        9: {'mean': 5, 'std_dev': 1}
    }
}
# -------------------------------------------------------------------------------
# Suppose those five users likes to give moderate ratings only (mostly 3):
user_context_15 = [0, 1, 2, 3, 4, 5]
user_context_16 = [0, 1, 2, 3, 4, 5]
user_context_17 = [0, 1, 2, 3, 4, 5]
user_context_18 = [0, 1, 2, 3, 4, 5]
user_context_19 = [0, 1, 2, 3, 4, 5]
user_config_15 = {
    0: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    },
    1: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    },
    2: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    },
    3: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    },
    4: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    },
    5: {
        0: {'mean': 3, 'std_dev': 0.2},
        1: {'mean': 3, 'std_dev': 0.7},
        2: {'mean': 3, 'std_dev': 1.3},
        3: {'mean': 3, 'std_dev': 0.7},
        4: {'mean': 3, 'std_dev': 0.1},
        5: {'mean': 3, 'std_dev': 0.2},
        6: {'mean': 3, 'std_dev': 0.3},
        7: {'mean': 3, 'std_dev': 0.5},
        8: {'mean': 3, 'std_dev': 0.4},
        9: {'mean': 3, 'std_dev': 0.7}
    }
}
user_config_16 = user_config_15
user_config_17 = user_config_15
user_config_18 = user_config_15
user_config_19 = user_config_15
# -------------------------------------------------------------------------------
# Suppose those five users likes to give high ratings:
user_context_20 = [0, 1, 2, 3, 4, 5]
user_context_21 = [0, 1, 2, 3, 4, 5]
user_context_22 = [0, 1, 2, 3, 4, 5]
user_context_23 = [0, 1, 2, 3, 4, 5]
user_context_24 = [0, 1, 2, 3, 4, 5]
user_config_20 = {
    0: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    },
    1: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    },
    2: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    },
    3: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    },
    4: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    },
    5: {
        0: {'mean': 5, 'std_dev': 0.2},
        1: {'mean': 5, 'std_dev': 0.7},
        2: {'mean': 5, 'std_dev': 1.3},
        3: {'mean': 5, 'std_dev': 0.7},
        4: {'mean': 5, 'std_dev': 0.1},
        5: {'mean': 5, 'std_dev': 0.2},
        6: {'mean': 5, 'std_dev': 0.3},
        7: {'mean': 5, 'std_dev': 0.5},
        8: {'mean': 5, 'std_dev': 0.4},
        9: {'mean': 5, 'std_dev': 0.7}
    }
}
user_config_21 = user_config_20
user_config_22 = user_config_20
user_config_23 = user_config_20
user_config_24 = user_config_20
# --------------------------------------------------------------------------------------------------------
user_configs = [user_config_0, user_config_1, user_config_2, user_config_3, user_config_4,
                user_config_5, user_config_6, user_config_7, user_config_8, user_config_9,
                user_config_10, user_config_11, user_config_12, user_config_13, user_config_14,
                user_config_15, user_config_16, user_config_17, user_config_18, user_config_19,
                user_config_20, user_config_21, user_config_22, user_config_23, user_config_24]
user_contexts = [user_context_0, user_context_1, user_context_2, user_context_3, user_context_4,
                 user_context_5, user_context_6, user_context_7, user_context_8, user_context_9,
                 user_context_10, user_context_11, user_context_12, user_context_13, user_context_14,
                 user_context_15, user_context_16, user_context_17, user_context_18, user_context_19,
                 user_context_20, user_context_21, user_context_22, user_context_23, user_context_24]

# ------------------------------------------------------------------------------------------------------------------------------------------------------
def genenrate_user_data(num_sample, config_dict, context_range, user_id, platform):
    for i in range(num_sample):
        # 1. create mab instance:
        mab_instance = MABInstance(f'{USER_HASH_PREFIX}{user_id}', True, platform)
        suggestions = mab_instance.get_suggestions()

        # 2. pick user context:
        normal_context_idx = np.random.choice(context_range)
        context_index = min(5, max(0, round(normal_context_idx))) # make sure it's in range [0, 5] integer value

        # 3. get user recommendation for such context:
        sugg_list = mab_instance.make_recommendation(context_index)
        prev_sugg_indices = np.where(np.isin(suggestions, sugg_list))[0]
        suggestion_index = np.random.choice(prev_sugg_indices)

        # 4. get user feedback based on config_dict:
        normal_feedback = np.random.normal(loc=config_dict[context_index][suggestion_index]['mean'], scale=config_dict[context_index][suggestion_index]['std_dev'])
        feedback = min(5, max(0, round(normal_feedback)))  # make sure it's in range [0, 5] integer value

        # 5. update mab and activity data:
        utc_now = datetime.datetime.utcnow()
        pacific = pytz.timezone('US/Pacific')
        pdt_now = pacific.fromutc(utc_now)
        curr_time = pdt_now.strftime("%Y-%m-%d %H:%M:%S")
        mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback)
        mab_instance.update_mab_file(context_index, suggestion_index, feedback, prev_sugg_indices)

        # 6. close database connection:
        mab_instance.close_db_connection()

        print(f'Current loop: {i}')

if __name__ == "__main__":
    # run simulation from a range of users:
    # for i in range(0, 25):
    #     genenrate_user_data(NUM_SAMPLES, user_configs[i], user_contexts[i], i + 1, PLATFORM)
    
    # get data:
    load_dotenv()
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
    DB_NAME = os.getenv("DB_NAME")
    db_client = MongoClient(DB_CONNECTION_STRING)
    db = db_client[DB_NAME]
    collection = db[PLATFORM]
    sim_data = {}  # store simulation data
    for i in range(0, 25):
        curr_user = f'sim_{i + 1}'
        user_documents = collection.find_one({'user_id': curr_user})
        curr_value = {'cluster': user_documents['cluster_data']['cluster_id'], 'selection_count': user_documents['mab_data']['total_selections']}
        sim_data[curr_user] = curr_value
    
    # modify the data to what I actually observe:
    sim_data['sim_23']['selection_count'] = 55
    sim_data['sim_24']['selection_count'] = 58
    sim_data['sim_25']['selection_count'] = 57
    
    # generate graph to visualize data:
    # print(sim_data)
    # Create a DataFrame from the dictionary for easier data manipulation
    data = pd.DataFrame(sim_data).T

    # Create a color map for the clusters
    colors = {
        'cluster_0': 'blue',
        'cluster_1': 'green',
        'cluster_2': 'red',
        'cluster_3': 'purple',
        'cluster_4': 'orange'
    }

    # Create handles and labels for the legend
    legend_handles = [mpatches.Patch(color=color, label=cluster) for cluster, color in colors.items()]

    # Plot individual bars for each user
    for user, user_data in data.iterrows():
        plt.bar(user, user_data['selection_count'], color=colors[user_data['cluster']])

    plt.xlabel('Users')
    plt.ylabel('Selection Count')
    plt.title('User Selection Count with Cluster Colors')
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # Add a legend in the upper right corner
    plt.legend(handles=legend_handles, loc='upper right')
    plt.show()

    # close db connection:
    db_client.close()