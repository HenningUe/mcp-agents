- replace "from typing" imports to "import typing as tp" and replace all
  imported items accordingly, e.g. Any to "tp.Any"
- replace Dict, Set, List from typing by native types, e.g. dict
- replace Optional keyword of typing by proper usage of pipe symbol "|" and None
- replace Union keyword of typing by proper usage of pipe symbol "|"

- use typing module as alias import, i.e. "import typing as tp". That means
  "Any" from typing is used as follows: "tp.Any"
- native types such as dict, set, list shall be used directly for type
  declarations. These types shall not be used from typing
- maximum line length shall be 100. Pythonic linebreaks shall be applied
- strings without context referencing via curled brackets should not have the
  f-prefix.
- Instead of typing.Optional use the pipe symbol "|" + None to indicate that
  None is a valid data type option
- Instead of typing.Union use the pipe symbol "|" to concatenate optional data
  types
- Errors inside functions shall not be indicated by returning boolean values.
  I.e. False means function failed. Instead a proper custom error shall be
  thrown in the function. The caller can then deal with this function properly
