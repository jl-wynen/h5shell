from enum import Enum

import h5py as h5

class H5Item:
    class Kind(Enum):
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
    def __init__(self, fname):
        self._fname = fname
        self._cache = {}

        self.read_file()

    def clear_cache(self):
        self._cache = {}

    def refresh(self):
        # TODO check modification time
        self.clear_cache()
        self.read_file()

    def dump_cache(self, cache = None):
        if not hasattr(self, "indent") or self.indent < 0:
            self.indent = 0
            
        if not cache:
            cache = self._cache
            
        for k in cache:
            print(" "*self.indent+"{:<40}".format(k),end="")
            
            if cache[k].kind == H5Item.Kind.dataset:
                print("dset")
            elif cache[k].kind == H5Item.Kind.group:
                print("group")
                if cache[k].children:
                    self.indent += 4
                    self.dump_cache(cache[k].children)
            elif cache[k].kind == H5Item.Kind.hardLink:
                print("hardLink to " + str(cache[k].target))
            elif cache[k].kind == H5Item.Kind.softLink:
                print("softLink to " + str(cache[k].target))
            elif cache[k].kind == H5Item.Kind.externalLink:
                print("extLink to " + cache[k].target[0] + "//" + cache[k].target[1])
            else:
                print("???")

        self.indent -= 4
                
    def read_file(self):
        with h5.File(self._fname, "r") as f:
            self._load_to_cache(f, self._cache)
            
    def _get_group(self, path, cache):
        if len(path) == 0:
            return cache
        else:
            # raise KeyError if path does not exist
            if cache[path[0]].kind == H5Item.Kind.group:
                return self._get_group(path[1:], cache[path[0]].children)
            else:
                return {path[0]: cache[path[0]]}
    
    def list_contents(self, path):
        self.refresh()
        group = self._get_group(path, self._cache)
        return group

    def _load_to_cache(self, group, cache):
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
