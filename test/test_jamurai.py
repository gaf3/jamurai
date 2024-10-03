import unittest
import unittest.mock

import json
import yaml

import jamurai
import jinja2
import sphinxter.unittest


class TestEngine(unittest.TestCase):

    def setUp(self):

        self.machine = jamurai.Machine("/opt/service/cnc/sweat", [".git"])

    def test___init__(self):

        init = jamurai.Machine()
        self.assertEqual(init.base, '')
        self.assertEqual(init.skip, [])
        self.assertTrue(init.engine.env.keep_trailing_newline)

        init = jamurai.Machine("people", "stuff", "jamonit", "things")
        self.assertEqual(init.base, "people")
        self.assertEqual(init.skip, "stuff")
        self.assertEqual(init.inject, "jamonit")
        self.assertEqual(init.engine, "things")

    def test_placing(self):

        self.assertEqual(self.machine.placing({"source": None}), "source")
        self.assertEqual(self.machine.placing({}), "destination")

    def test_place(self):

        self.assertEqual(self.machine.place({"source": "ya"}), "ya")
        self.assertEqual(self.machine.place({"destination": "sure"}), "sure")

    def test_exclude(self):

        self.assertFalse(self.machine.exclude({"include": ["a"], "exclude": [], "source": "a"}))
        self.assertFalse(self.machine.exclude({"include": ["a*"], "exclude": [], "source": "ab"}))
        self.assertTrue(self.machine.exclude({"include": [], "exclude": ["a"], "source": "a"}))
        self.assertTrue(self.machine.exclude({"include": [], "exclude": ["a*"], "source": "ab"}))
        self.assertFalse(self.machine.exclude({"include": [], "exclude": [], "source": "a"}))

        self.assertFalse(self.machine.exclude({"include": ["a"], "exclude": [], "destination": "a"}))
        self.assertFalse(self.machine.exclude({"include": ["a*"], "exclude": [], "destination": "ab"}))
        self.assertTrue(self.machine.exclude({"include": [], "exclude": ["a"], "destination": "a"}))
        self.assertTrue(self.machine.exclude({"include": [], "exclude": ["a*"], "destination": "ab"}))
        self.assertFalse(self.machine.exclude({"include": [], "exclude": [], "destination": "a"}))

    def test_preserve(self):

        self.assertFalse(self.machine.preserve({"transform": ["a"], "preserve": [], "source": "a"}))
        self.assertFalse(self.machine.preserve({"transform": ["a*"], "preserve": [], "source": "ab"}))
        self.assertTrue(self.machine.preserve({"transform": [], "preserve": ["a"], "source": "a"}))
        self.assertTrue(self.machine.preserve({"transform": [], "preserve": ["a*"], "source": "ab"}))
        self.assertFalse(self.machine.preserve({"transform": [], "preserve": [], "source": "a"}))

    def test_relative(self):

        self.assertEqual(self.machine.relative("/opt/service/cnc/sweat/a/b/c"), "a/b/c")

    @unittest.mock.patch("jamurai.open", create=True)
    def test_source(self, mock_open):

        self.assertEqual(self.machine.source({"source": {"value": "yep"}}), "yep")

        self.assertRaisesRegex(Exception, "invalid path: ..", self.machine.source, {"source": ".."})

        self.assertEqual(self.machine.source({"source": "stuff"}, path=True), "/opt/service/cnc/sweat/stuff")

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data='src').return_value
        ]

        self.assertEqual(self.machine.source({"source": "stuff"}), "src")

        mock_open.assert_called_once_with("/opt/service/cnc/sweat/stuff", "r", encoding='utf-8')

    @unittest.mock.patch("jamurai.open", create=True)
    @unittest.mock.patch("os.path.exists")
    def test_destination(self, mock_exists, mock_open):

        self.assertRaisesRegex(Exception, "invalid path: ..", self.machine.destination, {"destination": ".."})

        self.assertEqual(self.machine.destination({"destination": "things"}, path=True), "/opt/service/cnc/sweat/things")

        mock_read = unittest.mock.mock_open(read_data='dest').return_value
        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [mock_read, mock_write]

        self.assertEqual(self.machine.destination({"destination": "things"}), "dest")

        mock_open.assert_called_once_with("/opt/service/cnc/sweat/things", "r", encoding='utf-8')

        self.machine.destination({"destination": "things"}, "dest")

        mock_open.assert_called_with("/opt/service/cnc/sweat/things", "w", encoding='utf-8')
        mock_write.write.assert_called_once_with("dest")

        mock_open.reset_mock()
        mock_exists.return_value = False
        mock_open.side_effect = [mock_read, mock_write]

        self.machine.destination({"destination": "things", "replace": False}, "dest")

        mock_open.assert_called_with("/opt/service/cnc/sweat/things", "w", encoding='utf-8')
        mock_write.write.assert_called_once_with("dest")

        mock_open.reset_mock()
        mock_exists.return_value = True

        self.machine.destination({"destination": "things", "replace": False}, "dest")

        mock_open.assert_not_called()

    @unittest.mock.patch("os.path.exists")
    @unittest.mock.patch("shutil.copy")
    def test_copy(self, mock_copy, mock_exists):

        # no replace

        mock_exists.return_value = True

        self.machine.copy({"source": "src", "destination": "dest", "replace": False})

        mock_copy.assert_not_called()

        self.machine.copy({"source": "src", "destination": "dest"})

        mock_copy.assert_called_once_with(
            "/opt/service/cnc/sweat/src",
            "/opt/service/cnc/sweat/dest"
        )

    @unittest.mock.patch("os.path.exists")
    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("shutil.rmtree")
    @unittest.mock.patch("os.remove")
    def test_remove(self, mock_remove, mock_rmtree, mock_isdir, mock_exists):

        # not there

        mock_exists.return_value = False

        self.machine.remove({"destination": "dest"})

        mock_isdir.assert_not_called()

        # dir

        mock_exists.return_value = True
        mock_isdir.return_value = True

        self.machine.remove({"destination": "dest"})

        mock_rmtree.assert_called_once_with(
            "/opt/service/cnc/sweat/dest"
        )

        # file

        mock_isdir.return_value = False

        self.machine.remove({"destination": "dest"})

        mock_remove.assert_called_once_with(
            "/opt/service/cnc/sweat/dest"
        )

    def test_text(self):

        destination = "fee\nfie\n  # jamurai: here  \nfoe\nfum\n"

        # add

        self.assertEqual(self.machine.text("nope\n", destination, False, False), "fee\nfie\n  # jamurai: here  \nfoe\nfum\n")
        self.assertEqual(self.machine.text("foe\n", destination, True, False), "fee\nfie\n  # jamurai: here  \nfoe\nfum\n")
        self.assertEqual(self.machine.text("yep\n", destination, True, False), "fee\nfie\n  # jamurai: here  \nfoe\nfum\nyep\n")
        self.assertEqual(self.machine.text("yep\n", destination, "here", False), "fee\nfie\nyep\n  # jamurai: here  \nfoe\nfum\n")

        # remove

        self.assertEqual(self.machine.text("nope\n", "fee\nfie\n  # jamurai: here  \nfoe\nfum\n", False, True), destination)
        self.assertEqual(self.machine.text("foe\n", "fee\nfie\n  # jamurai: here  \nfoe\nfum\n", True, True), "fee\nfie\n  # jamurai: here  \nfum\n")
        self.assertEqual(self.machine.text("yep\n", "fee\nfie\n  # jamurai: here  \nfoe\nfum\nyep\n", True, True), destination)
        self.assertEqual(self.machine.text("yep", "fee\nfie\nyep\n  # jamurai: here  \nfoe\nfum\n", "here", True), destination)

    def test_json(self):

        # add

        destination = json.dumps({
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"}
                ]
            }
        })
        source = json.dumps({"g": "h"})

        self.assertEqual(json.loads(self.machine.json(source, destination, "a__b", False)), {
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"},
                    {"g": "h"}
                ]
            }
        })

        # remove

        destination = json.dumps({
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"},
                    {"g": "h"}
                ]
            }
        })
        source = json.dumps({"g": "h"})

        self.assertEqual(json.loads(self.machine.json(source, destination, "a__b", True)), {
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"}
                ]
            }
        })

    def test_yaml(self):

        # add

        destination = yaml.safe_dump({
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"}
                ]
            }
        })
        source = yaml.safe_dump({"g": "h"})

        self.assertEqual(yaml.safe_load(self.machine.yaml(source, destination, "a__b", False)), {
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"},
                    {"g": "h"}
                ]
            }
        })

        # remove

        destination = yaml.safe_dump({
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"},
                    {"g": "h"}
                ]
            }
        })
        source = yaml.safe_dump({"g": "h"})

        self.assertEqual(yaml.safe_load(self.machine.yaml(source, destination, "a__b", True)), {
            "a": {
                "b": [
                    {"c": "d"},
                    {"e": "f"}
                ]
            }
        })

    @unittest.mock.patch("os.chmod")
    @unittest.mock.patch("os.stat")
    def test_mode(self, mock_stat, mock_mode):

        mock_stat.return_value.st_mode = "ala"

        self.machine.mode({"source": "src", "destination": "dest"})

        mock_stat.assert_called_once_with(
            "/opt/service/cnc/sweat/src"
        )

        mock_mode.assert_called_once_with(
            "/opt/service/cnc/sweat/dest",
            "ala"
        )

    @unittest.mock.patch("os.listdir")
    def test_directory(self, mock_listdir):

        mock_listdir.return_value = ["c"]

        self.machine.craft = unittest.mock.MagicMock()

        # .git source

        content = {
            "source": "a/b/.git",
            "destination": "a/b/.git",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.directory(content, None)

        self.machine.craft.assert_not_called()

        # .git destination

        content = {
            "destination": "a/b/.git",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.directory(content, None)

        self.machine.craft.assert_not_called()

        # root source

        content = {
            "source": "",
            "destination": "",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.craft(content, None)

        self.machine.craft.assert_called_once_with({
            "source": "",
            "destination": "",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }, None)

        # root destination

        content = {
            "destination": "",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.craft(content, None)

        self.machine.craft.assert_called_with({
            "destination": "",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }, None)

        # regular source

        content = {
            "source": "a/b",
            "destination": "a/b",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.directory(content, None)

        self.machine.craft.assert_called_with({
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }, None)

        # regular destination

        content = {
            "destination": "a/b",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.directory(content, None)

        self.machine.craft.assert_called_with({
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }, None)

    @unittest.mock.patch("shutil.copy")
    @unittest.mock.patch("jamurai.open", create=True)
    @unittest.mock.patch("os.chmod")
    @unittest.mock.patch("os.stat")
    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("os.remove")
    def test_file(self, mock_remove, mock_isdir, mock_stat, mock_mode, mock_open, mock_copy):

        # Copy

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": ["a/b/c"],
            "transform": []
        }

        self.machine.file(content, None)

        mock_copy.assert_called_once_with(
            "/opt/service/cnc/sweat/a/b/c",
            "/opt/service/cnc/sweat/a/b/c"
        )

        # Remove

        mock_isdir.return_value = False

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "remove": ["a/b/c"],
            "transform": []
        }

        self.machine.file(content, None)

        mock_remove.assert_called_once_with(
            "/opt/service/cnc/sweat/a/b/c"
        )

        # Text

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data="{{ sure }}\n").return_value,
            unittest.mock.mock_open(read_data="fee\nfie\n  # jamurai: here  \nfoe\nfum\n").return_value,
            mock_write
        ]

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": [],
            "text": "{{ there }}"
        }

        self.machine.file(content, {"sure": "yep", "there": "here"})

        mock_write.write.assert_called_once_with("fee\nfie\nyep\n  # jamurai: here  \nfoe\nfum\n")

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data="{{ sure }}\n").return_value,
            unittest.mock.mock_open(read_data="fee\nfie\n  # jamurai: here  \nfoe\nfum\n").return_value,
            mock_write
        ]

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": [],
            "text": True
        }

        self.machine.file(content, {"sure": "yep", "there": "here"})

        mock_write.write.assert_called_once_with("fee\nfie\n  # jamurai: here  \nfoe\nfum\nyep\n")

        # JSON

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data='"{{ sure }}"').return_value,
            unittest.mock.mock_open(read_data='{"here": []}').return_value,
            mock_write
        ]

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": [],
            "json": "{{ there }}"
        }

        self.machine.file(content, {"sure": "yep", "there": "here"})

        mock_write.write.assert_called_once_with('{\n    "here": [\n        "yep"\n    ]\n}\n')

        # YAML

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data='"{{ sure }}"').return_value,
            unittest.mock.mock_open(read_data='here: []').return_value,
            mock_write
        ]

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": [],
            "yaml": "{{ there }}"
        }

        self.machine.file(content, {"sure": "yep", "there": "here"})

        mock_write.write.assert_called_once_with('here:\n- yep\n')

        # Value

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            mock_write
        ]

        mock_stat.return_value.st_mode = "ala"

        content = {
            "source": {
                "value": "hey"
            },
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.file(content, {"sure": "yep"})

        mock_write.write.assert_called_once_with('hey')

        mock_mode.assert_not_called()

        # Mode

        mock_write = unittest.mock.mock_open().return_value

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data='{{ sure }}').return_value,
            mock_write
        ]

        mock_stat.return_value.st_mode = "ala"

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": [],
            "transform": []
        }

        self.machine.file(content, {"sure": "yep"})

        mock_write.write.assert_called_once_with('yep')

        mock_stat.assert_called_with(
            "/opt/service/cnc/sweat/a/b/c"
        )

        mock_mode.assert_called_once_with(
            "/opt/service/cnc/sweat/a/b/c",
            "ala"
        )


    @unittest.mock.patch("os.path.exists")
    @unittest.mock.patch("os.makedirs")
    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("os.listdir")
    @unittest.mock.patch("shutil.copy")
    def test_craft(self, mock_copy, mock_listdir, mock_isdir, mock_makedirs, mock_exists):

        # Excluded

        content = {
            "source": "a",
            "include": [],
            "exclude": ["a"]
        }

        self.machine.craft(content, None)

        # Directory source

        mock_exists.return_value = False
        mock_isdir.return_value = True
        mock_listdir.return_value = ["c"]

        content = {
            "source": "a/b",
            "destination": "a/b",
            "include": [],
            "exclude": ["a/b/*"],
            "preserve": [],
            "transform": []
        }

        self.machine.craft(content, None)

        # Directory destination

        content = {
            "destination": "a/b",
            "include": [],
            "exclude": ["a/b/*"],
            "preserve": [],
            "transform": []
        }

        self.machine.craft(content, None)

        # Copy

        mock_exists.return_value = True
        mock_isdir.return_value = False

        content = {
            "source": "a/b/c",
            "destination": "a/b/c",
            "include": [],
            "exclude": [],
            "preserve": ["a/b/c"],
            "transform": []
        }

        self.machine.craft(content, None)

        mock_copy.assert_called_once_with(
            "/opt/service/cnc/sweat/a/b/c",
            "/opt/service/cnc/sweat/a/b/c"
        )

        # Content

        mock_exists.side_effect = Exception("whoops")

        self.assertRaisesRegex(Exception, "whoops", self.machine.craft, content, {"sure": "yep"})

    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("glob.glob")
    def test_places(self, mock_glob, mock_isdir):

        self.machine.craft = unittest.mock.MagicMock()

        mock_glob.return_value = ["/opt/service/cnc/sweat/a/b/c"]
        mock_isdir.return_value = False

        # Root source

        content = {
            "source": "/"
        }

        self.assertEqual(self.machine.places(content, {}), [""])

        # Root destination

        content = {
            "destination": "/"
        }

        self.assertEqual(self.machine.places(content, {}), [""])

        # Glob source

        content = {
            "source": "{{ start }}/*"
        }

        self.assertEqual(self.machine.places(content, {}), ["a/b/c"])

        # Glob destination

        content = {
            "destination": "{{ start }}/*"
        }

        self.assertEqual(self.machine.places(content, {}), ["a/b/c"])

        # Dir source

        mock_isdir.return_value = True

        content = {
            "source": "{{ start }}/"
        }

        self.assertEqual(self.machine.places(content, {"start": "a/b"}), ["a/b/c"])

        # Dir destination

        content = {
            "destination": "{{ start }}/"
        }

        self.assertEqual(self.machine.places(content, {"start": "a/b"}), ["a/b/c"])

        mock_isdir.return_value = False

        # dict source

        content = {
            "source": {
                "value": "template"
            }
        }

        self.assertEqual(self.machine.places(content, {}), [{"value": "template"}])

        # dict destination

        content = {
            "destination": {
                "value": "template"
            }
        }

        self.assertEqual(self.machine.places(content, {}), [{"value": "template"}])

    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("glob.glob")
    def test_build(self, mock_glob, mock_isdir):

        self.machine.craft = unittest.mock.MagicMock()

        mock_glob.return_value = ["/opt/service/cnc/sweat/a/b/c"]
        mock_isdir.return_value = False

        # Converting

        content = {
            "source": "{{ start }}/c",
            "destination": "{{ start }}/d",
            "include": "e/",
            "exclude": "f",
            "preserve": "g",
            "transform": "h"
        }

        self.machine.build(content, {"start": "a/b"})

        self.machine.craft.assert_called_with({
            "source": "a/b/c",
            "destination": "a/b/d",
            "include": ["e"],
            "exclude": ["f"],
            "preserve": ["g"],
            "transform": ["h"]
        }, {"start": "a/b"})

        # As is

        content = {
            "source": "{{ start }}/c",
            "destination": "{{ start }}/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }

        self.machine.build(content, {"start": "a/b"})

        self.machine.craft.assert_called_with({
            "source": "a/b/c",
            "destination": "a/b/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }, {"start": "a/b"})

        # destination

        content = {
            "destination": "{{ start }}/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }

        self.machine.build(content, {"start": "a/b"})

        self.machine.craft.assert_called_with({
            "destination": "a/b/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }, {"start": "a/b"})


class TestJamurai(sphinxter.unittest.TestCase):

    @unittest.mock.patch("os.path.isdir")
    @unittest.mock.patch("glob.glob")
    @unittest.mock.patch("jamurai.Machine.craft")
    def test_build(self, mock_craft, mock_glob, mock_isdir):

        mock_glob.return_value = ["/opt/service/cnc/sweat/a/b/c"]
        mock_isdir.return_value = False

        # Converting

        content = {
            "source": "{{ start }}/c",
            "destination": "{{ start }}/d",
            "include": "e/",
            "exclude": "f",
            "preserve": "g",
            "transform": "h"
        }

        jamurai.build(content, {"start": "a/b"}, "/opt/service/cnc/sweat", [".git"])

        mock_craft.assert_called_with({
            "source": "a/b/c",
            "destination": "a/b/d",
            "include": ["e"],
            "exclude": ["f"],
            "preserve": ["g"],
            "transform": ["h"]
        }, {"start": "a/b"})

        # As is

        content = {
            "source": "{{ start }}/c",
            "destination": "{{ start }}/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }

        jamurai.build(content, {"start": "a/b"}, "/opt/service/cnc/sweat", [".git"])

        mock_craft.assert_called_with({
            "source": "a/b/c",
            "destination": "a/b/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }, {"start": "a/b"})

        # destination

        content = {
            "destination": "{{ start }}/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }

        jamurai.build(content, {"start": "a/b"}, "/opt/service/cnc/sweat", [".git"])

        mock_craft.assert_called_with({
            "destination": "a/b/d",
            "include": ["i"],
            "exclude": ["j"],
            "preserve": ["k"],
            "transform": ["l"]
        }, {"start": "a/b"})

    def test_module(self):

        self.assertSphinxter(jamurai)
