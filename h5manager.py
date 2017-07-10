"""
Backend to manage HDF5 files.
"""

from enum import Enum
import fnmatch
from posixpath import normpath
import os.path
import calendar
import time
import sys

import h5py as h5

from util import split_path, abspath

class H5Item:
    """
    Represent one HDF5 item. Which members are meaningful depends on the items kind:
    - dataset: name, kind, shape, dtype
    - group: name, kind, children
    - hardLink, softLink: name, kind, target path (string)
    - externalLink: name, kind, target (tuple of filename and path (string) inside that file)
    """

    class Kind(Enum):
        """Kinds of possible items."""
        dataset      = 0
        group        = 1
        hardLink     = 2
        softLink     = 3
        externalLink = 4

    def __init__(self, name, kind, children=None, target=None, shape=None, dtype=None):
        self.name = name
        self.kind = kind
        self.children = children
        self.target = target  # string for softLink,
                              # (filename, path_inside_file) for externalLink
        self.shape = shape
        self.dtype = dtype

class H5Manager:
    """
    Provides basic operations on HDF5 files.
    """

    def __init__(self, fname):
        self._fname = None
        self._cache = {}
        self._openTime = 0 # time the file was last opened (secs since epoch)

        self.read_file(fname)

    def _clear_cache(self):
        """Empty out the cache"""
        self._cache = {}

    def refresh(self):
        """Re-read file if it has changed since it was last read."""

        try:
            if os.path.getmtime(self._fname) > self._openTime:
                self.read_file(self._fname)
        except FileNotFoundError:
            print("Error: file '{}' was removed.".format(self._fname))
            sys.exit(1)

    def read_file(self, fname):
        """Read the HDF5 file. Preserves cache if file does not exist."""

        with h5.File(fname, "r") as f:
            self._clear_cache()
            self._fname = fname
            self._load_to_cache(f, self._cache)
            self._openTime = calendar.timegm(time.gmtime())

    def _load_to_cache(self, group, cache):
        """Load an HDF5 group and its children into cache."""
        for k in group:
            item = group[k]
            if isinstance(item, h5.Group):
                cch = {}
                self._load_to_cache(item, cch)
                cache[k] = H5Item(k, H5Item.Kind.group, children=cch)
            else:
                # get link class
                lnk = group.get(k, getlink=True)

                if isinstance(lnk, h5.SoftLink):
                    cache[k] = H5Item(k, H5Item.Kind.softLink, target=lnk.path)
                elif isinstance(lnk, h5.ExternalLink):
                    cache[k] = H5Item(k, H5Item.Kind.externalLink,
                                      target=(lnk.filename, lnk.path))

                # TODO check for hard links
                else:
                    cache[k] = H5Item(k, H5Item.Kind.dataset,
                                      shape=item.shape, dtype=item.dtype)

    def get_items(self, wd, *spaths):
        """
        Get all items at given paths.
        Arguments:
            wd (:obj:`list`): Working directory.
            spaths (:obj:`list`): Relative (to wd) paths to items given as strings!
        Returns:
            List of tuples (p, d), where d is a dict mapping names to items
            and p is the path to those items.
        """

        self.refresh()

        result = []
        for spath in spaths:
            p = abspath(wd, [e for e in split_path(normpath(spath)) if e])
            self._get_items(p, self._cache, result, [])

        return result

    def get_item(self, path):
        """
        Retrieve one item from the file.
        The root item cannot be retrieved, instead `None` is returned.
        Arguments:
            path (:obj:`list`): Path to item.
        Returns:
            Item that was found or None if it does not exist or is root.
        """

        if not path:
            # cannot retrieve root object (does not exist)
            return None

        self.refresh()

        result = []
        # get parent of requested item
        self._get_items(path[:-1], self._cache, result, [])
        if not result:
            # parent does not exist
            return None

        items = result[0][1]  # all children of parent item
        if not items or not path[-1] in items:
            # there are no children or the one we want is not in there
            return None

        # found it
        return items[path[-1]]

    def _get_items(self, path, cache, result, fullpath):
        """
        Recursively collect items.
        Arguments:
            path (:obj:`list`): Path to explore.
            cache (:obj:`dict`): 'Directory' for current working directory.
            result (:obj:`list`): List of tuples (p, d), where d is a dict mapping names
                                  to items and p is the path to those items.
            fullpath (:obj:`list`): Path to items in current iteration (for internal use;
                                    init with empty list).
        """

        if not path:
            # path empty => store everything in cache
            result.append((fullpath, cache))
        else:
            items = {}
            for name in fnmatch.filter(cache.keys(), path[0]):
                item = cache[name]
                if item.kind == item.Kind.group:
                    # group: explore children and remember group name
                    self._get_items(path[1:], item.children, result, fullpath+[name])
                else:
                    # anything else: remember item
                    items[name] = item
            if items:
                # store all (non-group) items in current path
                result.append((fullpath, items))

    def get_file_name(self):
        """Return the name of the opened file."""
        return self._fname
