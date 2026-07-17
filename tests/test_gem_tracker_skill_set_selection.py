import unittest

from src.ui.gem_tracker_widget import PoBSkillSetSelectionDialog


class PoBSkillSetSelectionDialogTest(unittest.TestCase):
    def test_act_like_title_selection_prioritizes_act_and_excludes_early_mid_map(self):
        cases = {
            "Act 1": True,
            "Act early map": True,
            "early act": True,
            "early game": False,
            "early map": False,
            "earlygame": False,
            "midgame": False,
            "Mid Game": False,
            "Endgame Mapping": False,
            "Leveling 1-28": True,
            "1-12": True,
            "Late 68-90": False,
        }

        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertIs(
                    PoBSkillSetSelectionDialog._is_act_like_skill_set_title(title),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
