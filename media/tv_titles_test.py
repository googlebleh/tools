#!/usr/bin/env python3

import time
from titlecase import titlecase

from tv_titles import get_episode_title

def unittest_eps_title_lu(show, season, eps, expected):
    print(' '*4, "{} S{:02}E{:02}:".format(titlecase(show), season, eps), end=' ')
    retval = get_episode_title(show, season, eps)
    print(retval.encode('utf-8'))
    assert(retval == expected)

def test_eps_title_lu():
    print(' '*2, "Testing get_episode_title()...")
    start = time.time()

    unittest_eps_title_lu("adventure time", 6, 13, "Thanks for the Crabapples, Giuseppe!")
    # unittest_eps_title_lu("adventure time", 5, 52, "Billy's Bucket List")

    print(' '*4, "The Legend of Korra S02E08:", end=' ')
    r = get_episode_title("the legend of korra", "two", 8)
    print(r)
    assert(r == "Beginnings, Part 2")

    # unittest_eps_title_lu("adventure time", 5, 51, "Lemonhope (Part 1)")
    # unittest_eps_title_lu("gintama", 1, 4, "Watch Out! Weekly Shonen JUMP Sometimes Comes Out On Saturdays!")

    # Demoing the cache
    unittest_eps_title_lu("silicon valley", 2, 9, "Binding Arbitration")
    unittest_eps_title_lu("the big bang theory", 5, 21, "The Hawking Excitation")
    unittest_eps_title_lu("archer", 2, 11, "Jeu Monégasque")

    unittest_eps_title_lu("archer", 3, 1, "Heart of Archness: Part I")
    unittest_eps_title_lu("the big bang theory", 6, 9, "The Parking Spot Escalation")
    unittest_eps_title_lu("silicon valley", 2, 10, "Two Days of the Condor")
    unittest_eps_title_lu("the big bang theory", 4, 8, "The 21-Second Excitation")
    # unittest_eps_title_lu("the big bang theory", 2, 6, "The Cooper-Nowitzki Theorem")
    unittest_eps_title_lu("the big bang theory", 2, 6, "The Cooper–Nowitzki Theorem")
    unittest_eps_title_lu("archer", 5, 13, "Arrivals/Departures")
    unittest_eps_title_lu("archer", 3, 13, "Space Race: Part II")
    unittest_eps_title_lu("silicon valley", 1, 7, "Proof of Concept")
    unittest_eps_title_lu("archer", 3, 3, "Heart of Archness: Part III")
    unittest_eps_title_lu("the big bang theory", 8, 24, "The Commitment Determination")
    unittest_eps_title_lu("archer", 3, 12, "Space Race: Part I")
    unittest_eps_title_lu("archer", 3, 2, "Heart of Archness: Part II")

    elapsed = time.time() - start
    print(' '*2, "Passed in {:.3f} seconds".format(elapsed))

def runtests():
    print("Testing...")
    test_eps_title_lu()
    print("All tests passed")

def main():
    runtests()
    return 0

if __name__ == "__main__":
    main()
