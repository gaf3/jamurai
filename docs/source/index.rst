.. created by sphinxter
.. default-domain:: py

jamurai
=======

.. toctree::
    :maxdepth: 1
    :glob:
    :hidden:

    self
    *

.. module:: jamurai

Jinja wrapper for file and directory transformation and injection

As a single content::

    import os
    import yaml
    import jamurai

    with open("/tmp/from.txt", "w") as from_file:
        from_file.write("{{ foo }}")

    content = {
        "source": "from.txt",
        "destination": "to.txt"
    }

    values = {
        "foo": "bar"
    }

    jamurai.build(content, values, "/tmp")

    with open("/tmp/to.txt", "r") as to_file:
        data = to_file.read()

    data
    # "bar"

For multiple content::

    machine = jamurai.Machine("/tmp")

    with open("/tmp/this.txt", "w") as from_file:
        from_file.write("{{ this }}")

    with open("/tmp/that.txt", "w") as from_file:
        from_file.write("{{ that }}")

    contents = [
        {
            "source": "this.txt",
            "destination": "these.txt"
        },
        {
            "source": "that.txt",
            "destination": "those.txt"
        }
    ]

    values = {
        "this": "yin",
        "that": "yang"
    }

    for content in contents:
        machine.build(content, values)

    with open("/tmp/these.txt", "r") as to_file:
        data = to_file.read()

    data
    # "yin"

    with open("/tmp/those.txt", "r") as to_file:
        data = to_file.read()

    data
    # "yang"

Look at the content docs at the 'CnC Forge https://github.com/gaf3/cnc-forge/blob/main/Output.md#content'_

The only difference is the base is the same direcctory unlike transforming from one repo to enother.

.. function:: build(content, values, base='', skip=None, inject='jamurai', engine=None)

    Builds a content block

    :param content: What to transform, so
    :type content: dict
    :param values: Yaes engine to use instead of the default
    :type values: dict
    :param base: base directory to transform files
    :type base: yaes.Engine
    :param skip: list of files to skip for processing
    :type skip: list
    :param inject: keyword to inject text at (text:)
    :param engine: Yaes engine to use instead of the default

    **Usage**


    To process a single content block::

        import os
        import yaml
        import jamurai

        with open("/tmp/from.txt", "w") as from_file:
            from_file.write("{{ foo }}")

        content = {
            "source": "from.txt",
            "destination": "to.txt"
        }

        values = {
            "foo": "bar"
        }

        jamurai.build(content, values, "/tmp")

        with open("/tmp/to.txt", "r") as to_file:
            data = to_file.read()

        data
        # "bar"

.. class:: Machine(base='', skip=None, inject='jamurai', engine=None)

    Class for Jinja wrapper for file and directory transformation and injection

    :param base: base directory to transform files
    :type base: yaes.Engine
    :param skip: list of files to skip for processing
    :type skip: list
    :param inject: keyword to inject text at (text:)
    :param engine: Yaes engine to use instead of the default

    .. attribute:: base
        :type: str

        base directory to transform files

    .. attribute:: engine
        :type: yaes.Engine

        Yaes engine to use

    .. attribute:: inject
        :type: str

        keyword to inject text at (text:)

    .. attribute:: skip
        :type: list

        list of files to skip for processing

    .. method:: build(content, values)

        Builds a content block

        :param content: What to transform, so
        :type content: dict
        :param values: Yaes engine to use instead of the default
        :type values: dict

        **Usage**


        For multiple content::

            import os
            import yaml
            import jamurai


            machine = jamurai.Machine("/tmp")

            with open("/tmp/this.txt", "w") as from_file:
                from_file.write("{{ this }}")

            with open("/tmp/that.txt", "w") as from_file:
                from_file.write("{{ that }}")

            contents = [
                {
                    "source": "this.txt",
                    "destination": "these.txt"
                },
                {
                    "source": "that.txt",
                    "destination": "those.txt"
                }
            ]

            values = {
                "this": "yin",
                "that": "yang"
            }

            for content in contents:
                machine.build(content, values)

            with open("/tmp/these.txt", "r") as to_file:
                data = to_file.read()

            data
            # "yin"

            with open("/tmp/those.txt", "r") as to_file:
                data = to_file.read()

            data
            # "yang"

    .. method:: copy(content)

        Copies the content of source to desintation unchanged

        :param content:

    .. method:: craft(content, values)

        Craft changes, the actual work of creating desitnations from sources

        :param content:
        :param values:

    .. method:: destination(content, data=None, path=False)

        Retrieve or store the content of a destination file

        :param content:
        :param data:
        :param path:

    .. method:: directory(content, values)

        Craft a directory

        :param content:
        :param values:

    .. classmethod:: exclude(content)

        Exclude content from being copied from source to destination based on pattern

        :param content:

    .. method:: file(content, values)

        Craft a file

        :param content:
        :param values:

    .. staticmethod:: json(source, destination, location, remove)

        Inserts destination into source at location if not present

        :param source:
        :param destination:
        :param location:
        :param remove:

    .. method:: mode(content)

        Have the desination mode match the source mode

        :param content:

    .. classmethod:: place(content)

        Get either source of destination

        :param content:

    .. method:: places(content, values)

        Expands a place to sources or desintations

        :param content:
        :param values:

    .. staticmethod:: placing(content)

        Get either source of destination

        :param content:

    .. staticmethod:: preserve(content)

        Preserve content as is without transformation based on pattern

        :param content:

    .. method:: relative(path)

        Gets the relative path based on base and whether source or destnation

        :param path:

    .. method:: remove(content)

        Removes the content of desintation

        :param content:

    .. method:: source(content, path=False)

        Retrieves the content of a source file

        :param content:
        :param path:

    .. method:: text(source, destination, location, remove)

        Inserts destination into source at location if not present

        :param source:
        :param destination:
        :param location:
        :param remove:

    .. staticmethod:: yaml(source, destination, location, remove)

        Inserts destination into source at location if not present

        :param source:
        :param destination:
        :param location:
        :param remove:
