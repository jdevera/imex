import imex
from imex.metadata import Tag, ImageMetadata

class MetadataEditor(object):

    def __init__(self, rules, keep_timestamps = True, **kwargs):
        """
            Supported keyword arguments:
             * debug
             * dry_run
        """
        self._keep_timestamps = keep_timestamps
        self._debug = kwargs.pop('debug', False)
        self._dry_run = kwargs.pop('dry_run', False)
        self._rules = rules


    def apply_rule(self, image_metadata, rule):
        log = imex.log
        changed = False
        for new_tag_name in rule:
            new_tag_value = rule[new_tag_name]

            if not new_tag_name in image_metadata:
                changed = True
                image_metadata[new_tag_name] = Tag(new_tag_name)

            new_tag = image_metadata[new_tag_name] # Just a convenience alias.

            if new_tag.repeatable:
                # Separate the values to be added from the values to be deleted
                add_list, del_list = self._rules.parse_repeatable_tag_values(new_tag_value)

                # # -------------------------------------------------------------------------
                # # Deferred deletion of value new_tag_value for new_tag_name:
                # # If the new tag is the same as the matching tag and its matching value was
                # # set for deletion, add this value to the list of values to delete.
                # # -------------------------------------------------------------------------
                # if new_tag_name == search_tag_name and rules.must_remove(search_tag_name, search_tag_value):
                #     del_list.append(search_tag_value)
                #     log.qdebug('    Deferred removal of value \'{0}\' for tag {1}'.format(search_tag_value, search_tag_name))


                if add_list:
                    log.qdebug('    Adding values \'{0}\' to tag {1}'.format(', '.join(add_list), new_tag_name))
                if del_list:
                    log.qdebug('    Deleting values \'{0}\' from tag {1}'.format(', '.join(del_list), new_tag_name))

                # Add and delete (in this order) the new values from the current rule
                if new_tag.combine_raw_values(add_list, del_list):
                    changed = True
                    log.dump()
                else:
                    log.clear()
            else:
                # For non-repeatable tags, simply set the new value (this will take care of
                # deferred removal, too).
                new_adjusted_tag_value = [new_tag_value] if new_tag.is_iptc() else new_tag_value
                if new_tag.raw_value != new_adjusted_tag_value:
                    log.dump()
                    log.debug('    Setting new value \'{0}\' for tag {1}'.format(new_tag_value, new_tag_name))
                    new_tag.raw_value = new_adjusted_tag_value
                    changed = True

            log.clear()
        return changed

    def process_image(self, image_filename, rules):
        """
        Find all matching tags in an image's metadata and apply changes according
        to the given set of rules.

        This is the structure of a rule:
            search_tag_name : search_tag_value : (new_tag_name : new_tag_value)

        And it is read as: if the *search_tag_name* tag is found on the image with
        a value of *search_tag_value*, then set the value of each *new_tag_name* to
        its corresponding *new_tag_value*

        A search_tag_value can be set for removal once it has been found.
        """

        log = imex.log
        log.info('Processing {0}'.format(image_filename))
        imd = ImageMetadata(image_filename)
        imd.read()

        log.qdebug(' Applying default assignment')
        need_write = self.apply_rule(imd, rules.default_rule)

        # Tags that are present in the current image and have an associated rule
        matching_tags = rules.get_matching_tags(imd)

        for search_tag_name in matching_tags:

            for search_tag_value in rules.get_search_tag_values(search_tag_name):

                # --------------------------------------------------------------------------------
                # Skip this search_tag_value if it is not one of the values of the search_tag_name
                # tag in the current image
                # --------------------------------------------------------------------------------
                if not imd[search_tag_name].has_raw_value(search_tag_value):
                    continue

                log.debug(' Found match: value \'{0}\' for tag {1}'.format(search_tag_value, search_tag_name))
                # --------------------------------------------------------------------------------
                # The current search_tag_value can be marked for removal in the rules.
                #
                # We will normally delete the value right away, but if the same search_tag_name is
                # going to be modified as part of this rule, defer this deletion.
                #
                # In the case of a non-repeatable tag, the value will simply be replaced with the
                # new one. If it is a repeatable tag, we'll simply add search_tag_value to the
                # list of values to delete
                # --------------------------------------------------------------------------------
                if rules.must_remove(search_tag_name, search_tag_value):

                    # Remove now if we are not touching this search_tag_name in
                    # the current rule
                    if search_tag_name not in rules.get_new_tag_names(search_tag_name, search_tag_value):

                        if imd[search_tag_name].repeatable:
                            # If the list is empty, the tag will be deleted when
                            # the metadata is written
                            imd[search_tag_name].combine_raw_values([], [search_tag_value])
                        else:
                            del imd[search_tag_name]
                        log.debug('  Removed value \'{0}\' for tag {1}'.format(search_tag_value, search_tag_name))


                # ------------------------------------------------------------------------------
                # The current image has a search_tag_name tag and its value is search_tag_value,
                # now set all new_tag_names to their corresponding new_tag_values
                # ------------------------------------------------------------------------------
                for new_tag_name in rules.get_new_tag_names(search_tag_name, search_tag_value):

                    # Track any changes, only then we will need to run the rules again
                    changed = False

                    new_tag_value = rules.get_new_tag_value(search_tag_name, search_tag_value, new_tag_name)

                    # Add the new tag if it is not already present in the image. We will set it's
                    # value later.
                    if not new_tag_name in imd:
                        changed = True
                        imd[new_tag_name] = Tag(new_tag_name)

                    new_tag = imd[new_tag_name] # Just a convenience alias.

                    if new_tag.repeatable:
                        # Separate the values to be added from the values to be deleted
                        add_list, del_list = rules.parse_repeatable_tag_values(new_tag_value)

                        # -------------------------------------------------------------------------
                        # Deferred deletion of value new_tag_value for new_tag_name:
                        # If the new tag is the same as the matching tag and its matching value was
                        # set for deletion, add this value to the list of values to delete.
                        # -------------------------------------------------------------------------
                        if new_tag_name == search_tag_name and rules.must_remove(search_tag_name, search_tag_value):
                            del_list.append(search_tag_value)
                            log.qdebug('    Deferred removal of value \'{0}\' for tag {1}'.format(search_tag_value,
                                                                                                  search_tag_name))


                        if add_list:
                            log.qdebug('    Adding values \'{0}\' to tag {1}'.format(', '.join(add_list),
                                                                                     new_tag_name))
                        if del_list:
                            log.qdebug('    Deleting values \'{0}\' from tag {1}'.format(', '.join(del_list),
                                                                                         new_tag_name))

                        # Add and delete (in this order) the new values from the current rule
                        if new_tag.combine_raw_values(add_list, del_list):
                            changed = True
                            log.dump()
                        else:
                            log.clear()
                    else:
                        # For non-repeatable tags, simply set the new value (this will take care of
                        # deferred removal, too).
                        if new_tag.raw_value != new_tag_value:
                            log.debug('    Setting new value \'{0}\' for tag {1}'.format(new_tag_value, new_tag_name))
                            new_tag.raw_value = [new_tag_value] if new_tag.is_iptc() else new_tag_value
                            changed = True

                    if changed:
                        need_write = True

                        # ------------------------------------------------------------------------
                        # The current tag has changed, if there are any rules that have the
                        # current new_tag_name as their search_tag_name, then we need to apply the
                        # rules for that tag again, since some of their search_tag_value could
                        # match the new values.
                        # ------------------------------------------------------------------------
                        if new_tag_name in rules:
                            matching_tags.append(new_tag_name) # Extend the outermost for loop
                            log.debug(' **A matching tag has been modified. Revisiting all rules**')

                # for new_tag_name
            # for search_tag_value
        # for search_tag_name

        if need_write:
            if self._dry_run:
                log.debug(' Changes detected. File not saved (dry-run)')
            else:
                imd.write(self._keep_timestamps)
                log.debug(' Changes saved')
        else:
            log.debug(' No changes detected')


        log.debug('')
