class Tuple:
  def __init__(self, tup):
    self.values = tup["tuple"]
    self.meta = tup["meta"]
    self.column_aliases = tup.get("column_aliases", [])
    self.alias_hash = None

  def __getitem__(self, k):
    self.maybe_build_alias_hash()
    concrete_name_to_get = self.alias_hash.get(k, None)
    concrete_name_to_get = concrete_name_to_get if concrete_name_to_get else k
    if concrete_name_to_get in self.meta:
      return self.meta[concrete_name_to_get]
    elif concrete_name_to_get in self.values:
      return self.values[concrete_name_to_get]
    else:
      return None

  def maybe_build_alias_hash(self):
    if not self.alias_hash:
      self.alias_hash = {}
      for col in self.column_aliases:
#        rel_name = col["relation_name"]
        concrete_name = col["concrete_name"]

        # Note that this won't work with multiple tables since concrete_name will be repeated amongst them
        self.alias_hash[col["alias"]] = concrete_name
    return
