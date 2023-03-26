from typing import Dict
from collections import defaultdict


class completion_heandler:

  def __init__(self, system_message: str, message_count: int):
    self.data = defaultdict(list)
    self.system_messages = defaultdict(str)
    self.default_system_message = system_message
    self.message_max_count = message_count

  def _initinalize(self, user_id: str):
    self.data[user_id] = [{
      "role":
      "system",
      "content":
      self.system_messages.get(user_id) or self.default_system_message
    }]

  def _append(self, user_id: str, role: str, content: str):
    if self.data[user_id] == []:
      self._initinalize(user_id)
    self.data[user_id].append({"role": role, "content": content})

  def _clear(self, user_id: str):
    self.data[user_id] = []

  def _change_system(self, user_id: str, data: str):
    self.system_messages[user_id] = data
    self._clear(user_id)

  def _output_messages(self, user_id: str) -> Dict:
    if (len(self.data[user_id]) > self.message_max_count):
      self.data[user_id].pop(1)
      self.data[user_id].pop(1)
    return self.data[user_id]
