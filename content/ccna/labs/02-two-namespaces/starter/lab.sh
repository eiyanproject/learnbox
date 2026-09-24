#!/bin/bash
# Two namespaces joined by a veth pair.
#
# 1. create the pair
# 2. start a second namespace, held open by a background process
# 3. move veth1 into it
# 4. address and bring up both ends
#
# Leave the peer's pid in a variable called `peer` - the test uses it.

