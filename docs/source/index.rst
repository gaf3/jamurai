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

.. function:: build(content, values, base='', skip=None, inject='jamurai', engine=None)

    Bulids from a content

    :param content:
    :param values:
    :param base:
    :param skip:
    :param inject:
    :param engine:

.. class:: Machine(base='', skip=None, inject='jamurai', engine=None)

    Class that processes the transformation

    Store the daemon

    :param base:
    :param skip:
    :param inject:
    :param engine:

    .. method:: build(content, values)

        Bulids from a content

        :param content:
        :param values:

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
