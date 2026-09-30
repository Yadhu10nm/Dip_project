import unittest
from skills.command_skill.implementation import CommandSkill
from skills.common.types import Command


class TestCommandSkill(unittest.TestCase):
    def setUp(self):
        self.parser = CommandSkill()

    def test_locate_commands(self):
        cmd1 = self.parser.parse("locate Yadhu")
        self.assertEqual(cmd1.type, "LOCATE_PERSON")
        self.assertEqual(cmd1.target, "Yadhu")

        cmd2 = self.parser.parse("where is Alice?")
        self.assertEqual(cmd2.type, "LOCATE_PERSON")
        self.assertEqual(cmd2.target, "Alice")

    def test_stop_locating(self):
        cmd = self.parser.parse("stop locating")
        self.assertEqual(cmd.type, "STOP_LOCATING")

    def test_toggle_dip(self):
        cmd = self.parser.parse("show DIP mode")
        self.assertEqual(cmd.type, "TOGGLE_DIP")

    def test_toggle_sound(self):
        cmd_on = self.parser.parse("enable sound")
        self.assertEqual(cmd_on.type, "TOGGLE_SOUND")
        self.assertTrue(cmd_on.params.get("enabled"))

        cmd_off = self.parser.parse("disable sound")
        self.assertEqual(cmd_off.type, "TOGGLE_SOUND")
        self.assertFalse(cmd_off.params.get("enabled"))


if __name__ == "__main__":
    unittest.main()
