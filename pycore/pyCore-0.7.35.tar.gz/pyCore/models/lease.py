"""
Copyright (c) 2014 Maciej Nabozny

This file is part of OverCluster project.

OverCluster is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pyCore.utils import request
from pyCore.models.base_model import BaseModel

class Lease(BaseModel):
    def __str__(self):
        return self.id


    def attach(self, vm):
        """
        Attach lease to given vm
        :param vm: VM object
        """
        request(self.oc_address, '/api/network/attach/', {'token': self.token,
                                                          'lease_id': self.id,
                                                          'vm_id': vm.id})

    def detach(self):
        """
        Detach lease from vm (if attached)
        """
        request(self.oc_address, '/api/network/attach/', {'token': self.token,
                                                          'lease_id': self.id})