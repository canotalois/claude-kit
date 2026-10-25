"""Run with: python3 -m unittest discover -s hooks/tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOKS = os.path.join(os.path.dirname(__file__), "..")


def run_hook(name, payload):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, name)],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    return proc.returncode, proc.stderr


class GateDestructive(unittest.TestCase):
    def setUp(self):
        # Outside the temp dirs on purpose: the guard treats those as safe roots.
        self.project = tempfile.mkdtemp(dir=os.path.expanduser("~"), prefix=".hooktest-")
        subprocess.run(["git", "init", "-q", "-b", "feat/x", self.project], check=True)

    def tearDown(self):
        subprocess.run(["rm", "-r", "-f", self.project], check=True)

    def gate(self, command, tool_name="Bash"):
        payload = {"tool_name": tool_name, "cwd": self.project, "tool_input": {"command": command}}
        return run_hook("gate-destructive.py", payload)[0]

    def assertBlocked(self, command):
        self.assertEqual(self.gate(command), 2, command)

    def assertAllowed(self, command):
        self.assertEqual(self.gate(command), 0, command)

    def test_blocks_recursive_delete_of_root_in_every_flag_spelling(self):
        for cmd in ("rm -rf /", "rm -Rf /", "rm -r -f /", "rm -fr /*", "rm --recursive --force /", "rm -rf -- /"):
            self.assertBlocked(cmd)

    def test_blocks_home_project_root_and_outside_paths(self):
        for cmd in ("rm -rf ~", "rm -rf $HOME", 'rm -rf "${HOME}"', "rm -rf .", "rm -rf ..",
                    "rm -rf ../sibling", "rm -rf /usr/local", "rm -rf ~/Documents"):
            self.assertBlocked(cmd)

    def test_blocks_unresolvable_targets(self):
        self.assertBlocked("rm -rf $UNSET_KIT_TEST_VAR/")
        self.assertBlocked("rm -rf $(pwd)/..")

    def test_blocks_through_wrappers_and_chains(self):
        self.assertBlocked("sudo rm -rf /")
        self.assertBlocked("cd src && rm -rf /")
        self.assertBlocked("FOO=1 rm -rf ~")

    def test_allows_project_and_temp_deletes(self):
        for cmd in ("rm -rf node_modules", "rm -rf dist/*", "rm -rf ./build", "rm -rf /tmp/kit-build",
                    f"rm -rf {self.project}/target", "rm file.txt", "rm -f /etc/hosts.bak"):
            self.assertAllowed(cmd)

    def test_blocks_force_push_to_main_in_every_form(self):
        for cmd in ("git push --force origin main", "git push -f origin master", "git push origin +main",
                    "git push --force-with-lease origin main", "git push origin :main",
                    "git push --delete origin main", "git push -fu origin HEAD:main", "git push --mirror"):
            self.assertBlocked(cmd)

    def test_blocks_bare_force_push_when_on_main(self):
        subprocess.run(["git", "-C", self.project, "checkout", "-q", "-b", "main"], check=True)
        self.assertBlocked("git push --force")
        self.assertBlocked("git push -f origin HEAD")

    def test_allows_force_push_to_feature_branches(self):
        for cmd in ("git push --force origin my-branch", "git push -f origin feat/x",
                    "git push --force-with-lease", "git push origin main", "git push -u origin feat/x"):
            self.assertAllowed(cmd)

    def test_ignores_other_tools_and_bad_input(self):
        self.assertEqual(self.gate("rm -rf /", tool_name="Read"), 0)
        proc = subprocess.run([sys.executable, os.path.join(HOOKS, "gate-destructive.py")],
                              input="not json", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)


class CheckAiTells(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_flags_dashes_middot_and_emoji_from_claude_payload(self):
        path = self.write("a.md", "ok\nbad " + chr(0x2014) + " dash\n" + chr(0x1F680) + "\n")
        code, err = run_hook("check-ai-tells.py", {"tool_name": "Write", "tool_input": {"file_path": path}})
        self.assertEqual(code, 2)
        self.assertIn("a.md:2: em-dash", err)
        self.assertIn("a.md:3: emoji", err)

    def test_passes_clean_files_arrows_and_unknown_extensions(self):
        clean = self.write("c.md", "plain - text, arrows " + chr(0x2192) + " and checks " + chr(0x2713) + "\n")
        binary = self.write("d.bin", chr(0x2014))
        for path in (clean, binary):
            self.assertEqual(run_hook("check-ai-tells.py", {"tool_input": {"file_path": path}})[0], 0)

    def test_cli_mode_scans_arguments(self):
        bad = self.write("e.md", chr(0x2013) + "\n")
        clean = self.write("f.md", "fine\n")
        cli = [sys.executable, os.path.join(HOOKS, "check-ai-tells.py")]
        self.assertEqual(subprocess.run(cli + [clean]).returncode, 0)
        proc = subprocess.run(cli + [clean, bad], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("e.md:1: en-dash", proc.stderr)


if __name__ == "__main__":
    unittest.main()
