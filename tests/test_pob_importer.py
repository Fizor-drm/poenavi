import unittest

from src.utils.pob_importer import get_skill_sets_from_xml, parse_pob_xml


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PathOfBuilding>
  <Build className="Duelist" ascendClassName="Slayer" />
  <Skills activeSkillSet="2">
    <SkillSet title="Act 1" id="1">
      <Skill label="Starter" enabled="true">
        <Gem nameSpec="Splitting Steel" skillId="SplittingSteel" gemId="Metadata/Items/Gems/SkillGemSplittingSteel" />
        <Gem nameSpec="Chance to Bleed" skillId="SupportChanceToBleed" gemId="Metadata/Items/Gems/SupportGemChanceToBleed" />
      </Skill>
    </SkillSet>
    <SkillSet title="Endgame" id="2">
      <Skill label="Final" enabled="true">
        <Gem nameSpec="Lacerate" skillId="Lacerate" gemId="Metadata/Items/Gems/SkillGemLacerate" />
      </Skill>
    </SkillSet>
  </Skills>
</PathOfBuilding>
"""


class PoBImporterSkillSetTest(unittest.TestCase):
    def test_get_skill_sets_from_xml_marks_active_set(self):
        skill_sets = get_skill_sets_from_xml(SAMPLE_XML)

        self.assertEqual(
            skill_sets,
            [
                {"id": "1", "title": "Act 1", "active": False, "index": 0},
                {"id": "2", "title": "Endgame", "active": True, "index": 1},
            ],
        )

    def test_parse_pob_xml_filters_selected_skill_sets(self):
        result = parse_pob_xml(SAMPLE_XML, selected_skill_set_ids=["1"])

        self.assertEqual(result["class"], "duelist")
        self.assertEqual(result["ascendancy"], "slayer")
        self.assertEqual(result["selected_skill_set_ids"], ["1"])
        self.assertEqual(result["gem_names"], ["chance to bleed", "splitting steel"])
        self.assertEqual(len(result["gem_groups"]), 1)
        self.assertEqual(result["gem_groups"][0]["skill_set_title"], "Act 1")
        self.assertTrue(result["gem_groups"][0]["gems"][1]["is_support"])

    def test_parse_pob_xml_without_filter_imports_all_skill_sets(self):
        result = parse_pob_xml(SAMPLE_XML)

        self.assertEqual(result["gem_names"], ["chance to bleed", "lacerate", "splitting steel"])
        self.assertEqual(len(result["gem_groups"]), 2)


if __name__ == "__main__":
    unittest.main()
