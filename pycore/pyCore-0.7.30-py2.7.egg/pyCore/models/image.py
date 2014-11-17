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

class Image(BaseModel):
    def __str__(self):
        return self.name


    def delete(self):
        request(self.oc_address, '/api/image/delete/', {'token': self.token,
                                                     'image_id': self.id})


    def upload_url(self, url):
        request(self.oc_address, '/api/image/upload_url/', {'token': self.token,
                                                         'image_id': self.id,
                                                         'url': url})


    def upload_data(self, offset, data):
        request(self.oc_address, '/api/image/upload_data/', {'token': self.token,
                                                          'image_id': self.id,
                                                          'offset': offset,
                                                          'data': data})


    def attach(self, vm):
        request(self.oc_address, '/api/image/attach/', {'token': self.token,
                                                     'image_id': self.id,
                                                     'vm_id': vm.id})


    def detach(self, vm):
        request(self.oc_address, '/api/image/detach/', {'token': self.token,
                                                     'image_id': self.id,
                                                     'vm_id': vm.id})


    def edit(self, **kwargs):
        d = {'token': self.token, 'image_id': self.id}
        for k in kwargs.keys():
            d[k] = kwargs[k]
        request(self.oc_address, '/api/image/edit/', d)
