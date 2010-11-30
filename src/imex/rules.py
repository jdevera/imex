import yaml

from imex.metadata import Tag

class RuleManager(object):
    """
    Encapsulate a set of rules and provide validation and organised access to them.
    """

    REMOVE_KEY = '_rm'
    """
    Special key that indicates that the value where it appears is to be removed.
    """

    SELF_REF = '_self'

    def __init__(self, fin):
        """
        Get rules entry from the yaml rules file
        """
        all_rules = yaml.load(fin.read())
        self._ruleset = all_rules['rules']
        self.default_rule = all_rules['always_apply']
        self._special_names = [self.REMOVE_KEY]
        self._expand_self_refs()

    def __iter__(self):
        return self._ruleset.__iter__()


    def get_search_tag_names(self):
        """
        Get a list of all the search tag names
        """
        return self._ruleset.keys()

    def get_search_tag_values(self, tag_name):
        """
        Get a list of all the search tag values for a given search tag name
        """
        return self._ruleset[tag_name].keys()

    def get_new_tag_names(self, tag_name, tag_value):
        """
        Get a list of the new tag names under a given search tag value for a given search tag
        name, excluding those with a special meaning.
        """
        return [key for key in self._ruleset[tag_name][tag_value] \
                    if not key in self._special_names]

    def get_new_tag_value(self, tag_name, tag_value, new_tag_name):
        """
        Get the new value that is to be assigned to a given new tag name when search tag name has
        a value of search tag value.
        """
        return self._ruleset[tag_name][tag_value][new_tag_name]

    def must_remove(self, tag_name, tag_value):
        """
        Check whether a given value for a given tag must be removed if found in a image
        """
        return self._ruleset[tag_name][tag_value].get(self.REMOVE_KEY, False)

    @staticmethod
    def parse_repeatable_tag_values(values):
        """
        Separate repeatable values in values to add and values to delete.

        Repeatable tag values come in the rules as a list of values. These values support a + and
        a - as prefixes that indicate whether the following value is to be added or removed,
        respectively. Values with no prefix are added.

        In order to delete a value that starts with +, the - prefix must be used, e.g. -+value
        In order to add a value that starts with -, the + prefix must be used, e.g. +-value
        """
        add_list = []
        del_list = []
        for value in values:
            if value.startswith("-"):
                del_list.append(value[1:])
            elif value.startswith("+"):
                add_list.append(value[1:])
            else: # Asume this is an addition
                add_list.append(value)
        return add_list, del_list

    def get_matching_tags(self, existing_tags):
        """
        Return a list of the given tag names that also appear in the rule set as search tags
        """
        return list(set(existing_tags).intersection(self._ruleset))

    def _expand_self_refs(self):
        for search_tag_name in self.get_search_tag_names():
            for search_tag_value in self.get_search_tag_values(search_tag_name):
                for new_tag_name in self.get_new_tag_names(search_tag_name, search_tag_value):
                    if new_tag_name == self.SELF_REF:
                        new_tag_value = self.get_new_tag_value(search_tag_name, search_tag_value, new_tag_name)
                        self._ruleset[search_tag_name][search_tag_value][search_tag_name] = new_tag_value
                        del self._ruleset[search_tag_name][search_tag_value][self.SELF_REF]

    def validate(self):
        """
        Validate the structure of the rule set
        """
        for search_tag_name in self.get_search_tag_names():
            search_tag_obj = Tag(search_tag_name)
            for search_tag_value in self.get_search_tag_values(search_tag_name):
                for new_tag_name in self.get_new_tag_names(search_tag_name, search_tag_value):
                    new_tag_obj = Tag(new_tag_name)
                    new_tag_value = self.get_new_tag_value(search_tag_name, search_tag_value, new_tag_name)
                    if new_tag_obj.repeatable:
                        if not isinstance(new_tag_value, list):
                            raise KeyError('%s needs a list'%(new_tag_name))
                    else:
                        if isinstance(new_tag_value, list):
                            raise KeyError('%s needs a scalar value'%(new_tag_name))
