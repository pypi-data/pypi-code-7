class Counter:
  counter = 0

  @classmethod
  def get(self):
    self.counter += 1
    return str(self.counter)

  @classmethod
  def reset(self):
    self.counter = 0
