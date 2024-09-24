import os
import glob
import json
import yaml
import shutil
import fnmatch

import jinja2
import overscore
import yaes

class Machine:
    """
    Class that processes the transformation
    """

    def __init__(self, base='', skip=None, inject="jamurai", engine=None):
        """
        Store the daemon
        """

        self.base = base
        self.skip = skip or []
        self.inject = inject
        self.engine = engine or yaes.Engine(jinja2.Environment(keep_trailing_newline=True))

    @staticmethod
    def placing(content):
        """
        Get either source of destination
        """

        return "source" if "source" in content else "destination"

    @classmethod
    def place(cls, content):
        """
        Get either source of destination
        """

        return content[cls.placing(content)]

    @classmethod
    def exclude(cls, content):
        """
        Exclude content from being copied from source to destination based on pattern
        """

        # Check override to include no matter what first

        for pattern in content['include']:
            if fnmatch.fnmatch(cls.place(content), pattern):
                return False

        # Now exclude

        for pattern in content['exclude']:
            if fnmatch.fnmatch(cls.place(content), pattern):
                return True

        return False

    @staticmethod
    def preserve(content):
        """
        Preserve content as is without transformation based on pattern
        """

        # Check override first to transform no matter what

        for pattern in content['transform']:
            if fnmatch.fnmatch(content['source'], pattern):
                return False

        # Now preserve

        for pattern in content['preserve']:
            if fnmatch.fnmatch(content['source'], pattern):
                return True

        return False

    def relative(self, path):
        """
        Gets the relative path based on base and whether source or destnation
        """
        return path.split(self.base, 1)[-1].split("/", 2)[-1]

    def source(self, content, path=False):
        """
        Retrieves the content of a source file
        """

        if isinstance(content['source'], dict):
            return content['source']['value']

        source = os.path.abspath(f"{self.base}/source/{content['source']}")

        if not source.startswith(f"{self.base}/source"):
            raise Exception(f"invalid path: {source}")

        if path:
            return source

        with open(source, "r") as source_file:
            return source_file.read()

    def destination(self, content, data=None, path=False):
        """
        Retrieve or store the content of a destination file
        """

        destination = os.path.abspath(f"{self.base}/destination/{content['destination']}")

        if not destination.startswith(f"{self.base}/destination"):
            raise Exception(f"invalid path: {destination}")

        if path:
            return destination

        if not content.get("replace", True) and os.path.exists(destination):
            return

        if data is None:
            with open(destination, "r") as destination_file:
                return destination_file.read()

        with open(destination, "w") as destination_file:
            return destination_file.write(data)

    def copy(self, content):
        """
        Copies the content of source to desintation unchanged
        """

        source = self.source(content, path=True)
        destination = self.destination(content, path=True)

        if not content.get("replace", True) and os.path.exists(destination):
            return

        shutil.copy(source, destination)

    def remove(self, content):
        """
        Removes the content of desintation
        """

        destination = self.destination(content, path=True)

        if not os.path.exists(destination):
            return

        if os.path.isdir(destination):
            shutil.rmtree(destination)
            return

        os.remove(destination)

    def text(self, source, destination, location, remove):
        """
        Inserts destination into source at location if not present
        """

        if remove:

            if source not in destination:
                return destination

            if isinstance(location, bool) and location:
                return "".join(destination.split(source))

            if f"{self.inject}: {location}" in destination:

                if source[-1] != "\n":
                    source = f"{source}\n"

                sections = destination.split(f"{self.inject}: {location}")
                sections[0] = "".join(sections[0].split(source))
                return f"{self.inject}: {location}".join(sections)


        if source in destination:
            return destination

        if isinstance(location, bool) and location:
            return destination + source

        if source[-1] == "\n":
            source = source[:-1]

        lines = []

        for line in destination.split("\n"):
            if f"{self.inject}: {location}" in line:
                lines.append(source)
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def json(source, destination, location, remove):
        """
        Inserts destination into source at location if not present
        """

        source = json.loads(source)
        destination = json.loads(destination)

        value = overscore.get(destination, location)

        if source not in value and not remove:
            value.append(source)

        if source in value and remove:
            value.remove(source)

        return json.dumps(destination, indent=4) + "\n"

    @staticmethod
    def yaml(source, destination, location, remove):
        """
        Inserts destination into source at location if not present
        """

        source = yaml.safe_load(source)
        destination = yaml.safe_load(destination)

        value = overscore.get(destination, location)

        if source not in value and not remove:
            value.append(source)

        if source in value and remove:
            value.remove(source)

        return yaml.safe_dump(destination, default_flow_style=False)

    def mode(self, content):
        """
        Have the desination mode match the source mode
        """

        os.chmod(
            self.destination(content, path=True),
            os.stat(self.source(content, path=True)).st_mode
        )

    def directory(self, content, values):
        """
        Craft a directory
        """

        # Iterate though the items found

        if self.place(content).split("/")[-1] in self.skip:
            return

        for item in os.listdir(getattr(self, self.placing(content))(content, path=True)):
            if self.placing(content) == "source":
                self.craft({**content,
                    "source": f"{content['source']}/{item}" if content['source'] else item,
                    "destination": f"{content['destination']}/{item}" if content['destination'] else item
                }, values)
            else:
                self.craft({**content,
                    "destination": f"{content['destination']}/{item}" if content['destination'] else item
                }, values)

    def file(self, content, values):
        """
        Craft a file
        """

        # If we're preserving, just copy, else load source and transformation to destination

        remove = content.get("remove", False)

        if remove and "text" not in content and "json" not in content and "yaml" not in content:
            self.remove(content)
            return

        if self.preserve(content):
            self.copy(content)
            return

        source = self.engine.transform(self.source(content), values)

        # See if we're injecting anywhere, else just overwrite

        mode = False

        if "text" in content:
            destination = self.text(
                source, self.destination(content),
                self.engine.transform(content["text"], values) if isinstance(content["text"], str) else content["text"],
                remove
            )
        elif "json" in content:
            destination = self.json(source, self.destination(content), self.engine.transform(content["json"], values), remove)
        elif "yaml" in content:
            destination = self.yaml(source, self.destination(content), self.engine.transform(content["yaml"], values), remove)
        else:
            mode = isinstance(content['source'], str)
            destination = source

        self.destination(content, destination)

        if mode:
            self.mode(content)

    def craft(self, content, values):
        """
        Craft changes, the actual work of creating desitnations from sources
        """

        # Skip if we're to exclude

        if self.exclude(content):
            return

        # Make sure the directory exists

        if not os.path.exists(os.path.dirname(self.destination(content, path=True))):
            os.makedirs(os.path.dirname(self.destination(content, path=True)))

        # If source is a directory

        if (
            (isinstance(content.get('source'), str) and os.path.isdir(self.source(content, path=True))) or
            (isinstance(content.get('destination'), str) and os.path.isdir(self.destination(content, path=True)))
        ):

            self.directory(content, values)

        else:

            self.file(content, values)

    def places(self, content, values):
        """
        Expands a place to sources or desintations
        """

        content[self.placing(content)] = self.engine.transform(self.place(content), values)

        if isinstance(self.place(content), dict):

            places = [self.place(content)]

        else:

            if self.place(content) == "/":
                places = [""]
            else:

                path = getattr(self, self.placing(content))(content, path=True)

                if '*' in path or os.path.isdir(path):
                    places = [self.relative(source) for source in glob.glob(path)]
                else:
                    places = [self.relative(path)]

        return places

    def build(self, content, values):
        """
        Bulids from a content
        """

        # Transform exclude, include, preserve, and transforma and ensure they're lists

        for collection in ["exclude", "include", "preserve", "transform"]:
            content[collection] = self.engine.transform(content.get(collection, []), values)
            if isinstance(content[collection], str):
                content[collection] = [content[collection]]
            content[collection] = [pattern[:-1] if pattern[-1] == "/" else pattern for pattern in content[collection]]

        # Transform the source on templating, using destination if it doesn't exist for remove

        if self.placing(content) == "source":

            # Go through the source as glob, transforming destination accordingly, assuming source if missing

            for place in self.places(content, values):
                self.craft({**content,
                    "source": place,
                    "destination": self.engine.transform(content.get("destination", place), values)
                }, values)

        else:

            for place in self.places(content, values):
                self.craft({**content,
                    "destination": place
                }, values)

def build(content, values, base='', skip=None, inject="jamurai", engine=None):
    """
    Bulids from a content
    """

    Machine(base, skip, inject, engine).build(content, values)