#!/usr/bin/env python

# Copyright (c) 2010 Jacobo de Vera 

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Expand image metadata according to rules
"""

import sys
import imex

def main():

    opts, args = imex.ConfigManager().parse_cmd_line()

    # Set up logging
    imex.log = imex.SimpleScreenLogger()
    if opts.debug:
        imex.log.set_level(imex.log.LEVEL_DEBUG)

    # Get the rules
    with open(opts.rules_file) as fin:
        rules = imex.RuleManager(fin)

    if opts.check_rules:
        rules.validate()

    # Process all image files
    for image_file in args:
        mde = imex.MetadataEditor(rules, opts.keep_times, debug=opts.debug, dry_run=opts.dry_run)
        mde.process_image(image_file, rules)

    return 0


if __name__ == '__main__':
    sys.exit(main())

