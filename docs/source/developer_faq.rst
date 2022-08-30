Developer FAQ
==============================================

**Q:** Why are elements and versions stored as strings even though
they are integers?

**A:** Because JSON is used as the backend, and JSON only supports
using strings as keys in objects. Z numbers and versions are
used as keys.  It was decided to keep them as strings throughout. This is for
consistency, since JSON is also an output format.
