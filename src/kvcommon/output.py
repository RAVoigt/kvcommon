import pprint


def pp(
    *args,
    pprint_indent: int = 4,
    pprint_width: int = 100,
    pprint_depth: int | None = None,
    pprint_compact: bool = True,
    pprint_sort_dicts: bool = True,
    pprint_stream=None,
    **kwargs,
) -> pprint.PrettyPrinter:
    """
    PrettyPrinter is nice, but involves way too much boilerplate in setting one up quickly.

    This function acts as a one-liner that instantiates a pprint.PrettyPrinter with my preferred defaults and invokes it.

    The PrettyPrinter object is returned for later re-use.

    Params changed from defaults:
        pprint_compact: False -> True
        pprint_indent: 1 -> 4
        pprint_width: 80 -> 100
    """
    pp = pprint.PrettyPrinter(
        indent=pprint_indent,
        width=pprint_width,
        depth=pprint_depth,
        sort_dicts=pprint_sort_dicts,
        compact=pprint_compact,
        stream=pprint_stream,
    )
    pp.pprint(*args, **kwargs)
    return pp
