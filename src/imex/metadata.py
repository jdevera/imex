import pyexiv2


class Tag(object):
    """
    A wrapper for the different types of tag available in pyexiv2
    """

    def __init__(self, tag, value=None):
        if isinstance(tag, str):
            self._tag = self._create_tag(tag, value)
        else:
            self._tag = tag

    def _create_tag(self, key, value):
        """
        Create  pyexiv2 tag object based on the tag family of the key
        """
        family = key.split('.')[0].lower()
        return getattr(self, '_create_{0}_tag'.format(family))(key, value)

    @staticmethod
    def _create_exif_tag(key, value):
        """
        Helper method to create an Exif tag
        """
        return pyexiv2.ExifTag(key, value)

    @staticmethod
    def _create_iptc_tag(key, value):
        """
        Helper method to create an Iptc tag
        """
        return pyexiv2.IptcTag(key, value)

    @staticmethod
    def _create_xmp_tag(key, value):
        """
        Helper method to create an Xmp tag
        """
        return pyexiv2.XmpTag(key, value)

    def __repr__(self):
        return "{0}: {1!s}".format(self._tag.key, self._tag.raw_value)

    def is_exif(self):
        """
        True if the wrapped tag is in the Exif family
        """
        return isinstance(self._tag, pyexiv2.exif.ExifTag)

    def is_iptc(self):
        """
        True if the wrapped tag is in the Iptc family
        """
        return isinstance(self._tag, pyexiv2.iptc.IptcTag)

    def is_xmp(self):
        """
        True if the wrapped tag is in the Xmp family
        """
        return isinstance(self._tag, pyexiv2.xmp.XmpTag)

    @property
    def tag(self):
        """
        The wrapped pyexiv2 tag object
        """
        return self._tag

    @property
    def key(self):
        """
        The current tag's key 'Family.Section.Name'
        """
        return self._tag.key

    @property
    def name(self):
        """
        The name of the tag (this is also the third part of the key).
        """
        return self._tag.name

    @property
    def section(self):
        """
        The name of the tag's record (Second part of the key)
        """
        if self.is_exif():
            return self._tag.section_name
        elif self.is_iptc():
            return self._tag.record_name
        else:
            return self.key.split('.')[1]


    @property
    def value(self):
        """
        The value of the tag as a (list of) python object(s)
        """
        return self._tag.value

    @value.setter
    def value(self, new_value):
        self._tag.value = new_value

    @property
    def raw_value(self):
        """
        The value of the tag as a (list of) string(s)
        """
        return self._tag.raw_value

    @raw_value.setter
    def raw_value(self, new_raw_value):
        self._tag.raw_value = new_raw_value

    @property
    def repeatable(self):
        """
        Whether the tag is repeatable (accepts several values)
        """
        return self.is_iptc() and self._tag.repeatable

    def has_value(self, value):
        """
        Check whether a given value is among the tag's values

        When the tag is not repeatable, simply compare with the tag's value
        """
        if isinstance(self.value, list):
            return value in self.value
        else:
            return self.value == value

    def has_raw_value(self, raw_value):
        """
        Check whether a given value is among the tag's raw values (as strings)

        When the tag is not repeatable, simply compare with the tag's value
        """
        if isinstance(self.raw_value, list):
            return raw_value in self.raw_value
        else:
            return self.raw_value == raw_value

    def combine_raw_values(self, add_list, del_list):
        """
        For a repeatable tag, add the values in add_list to the tag raw values and then remove the
        values in del_list from the tag's raw values.

        Return true if there have been any changes.
        """
        if not self.repeatable:
            # Well, technically it has the attribute, but it's of no use if the tag is not
            # repeatable.
            msg = "Non-repeatable tag '{0}' has no 'combine_raw_values' attribute"
            raise AttributeError(msg.format(self.key))
        add_set = set(add_list)
        del_set = set(del_list)
        original_set = set(self.raw_value) if self.raw_value != None else set()
        new_values = (original_set | add_set) - del_set
        if original_set != new_values:
            self.raw_value = list(new_values)
            return True
        return False




class ImageMetadata(pyexiv2.metadata.ImageMetadata):
    """
    A specialisation of pyexiv2's ImageMetadata that works with the imex.Tag wrapper
    """

    def __getitem__(self, key):
        try:
            tag = pyexiv2.metadata.ImageMetadata.__getitem__(self, key)
            return Tag(tag)
        except KeyError:
            msg = "Tag '{0}' not set"
            raise KeyError(msg.format(key))

    def __setitem__(self, key, value):
        if isinstance(value, Tag):
            tag = value.tag
        else:
            tag = value
        pyexiv2.metadata.ImageMetadata.__setitem__(self, key, tag)


