import unittest
from skills.command_skill.implementation import CommandSkill


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.cmd_skill = CommandSkill()

    def test_locate_commands(self):
        c1 = self.cmd_skill.parse("locate Yadhu")
        self.assertEqual(c1.type, "LOCATE_PERSON")
        self.assertEqual(c1.target, "Yadhu")

        c2 = self.cmd_skill.parse("find Amith")
        self.assertEqual(c2.type, "LOCATE_PERSON")
        self.assertEqual(c2.target, "Amith")

    def test_stop_locating(self):
        c = self.cmd_skill.parse("stop locating")
        self.assertEqual(c.type, "STOP_LOCATING")

    def test_register_command(self):
        c = self.cmd_skill.parse("register Alice")
        self.assertEqual(c.type, "ENROLL_PERSON")
        self.assertEqual(c.target, "Alice")

    def test_dip_toggle(self):
        c = self.cmd_skill.parse("show DIP mode")
        self.assertEqual(c.type, "TOGGLE_DIP")

    def test_sound_toggles(self):
        c1 = self.cmd_skill.parse("enable sound")
        self.assertEqual(c1.type, "TOGGLE_SOUND")
        self.assertTrue(c1.params.get("enabled"))

        c2 = self.cmd_skill.parse("disable sound")
        self.assertEqual(c2.type, "TOGGLE_SOUND")
        self.assertFalse(c2.params.get("enabled"))

    def test_audit_log_command(self):
        c = self.cmd_skill.parse("show audit log")
        self.assertEqual(c.type, "SHOW_AUDIT_LOG")


if __name__ == "__main__":
    unittest.main()
