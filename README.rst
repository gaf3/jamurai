jamurai
=======

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
