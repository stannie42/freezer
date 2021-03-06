"""
Copyright 2014 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com). This product includes software written by Tim
Hudson (tjh@cryptsoft.com).
========================================================================
"""

import falcon
from freezer_api.common import exceptions


class BackupsCollectionResource(object):
    """
    Handler for endpoint: /v1/backups
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    def on_get(self, req, resp):
        # GET /v1/backups(?limit,marker)     Lists backups
        user_id = req.get_header('X-User-ID')
        obj_list = self.db.get_backup_list(user_id=user_id)
        req.context['result'] = {'backups': obj_list}

    def on_post(self, req, resp):
        # POST /v1/backups    Creates backup entry
        try:
            doc = req.context['doc']
        except KeyError:
            raise exceptions.BadDataFormat(
                message='Missing request body',
                resp_body={'error': 'missing request body'})
        user_name = req.get_header('X-User-Name')
        user_id = req.get_header('X-User-ID')
        backup_id = self.db.add_backup(
            user_id=user_id, user_name=user_name, data=doc)
        resp.status = falcon.HTTP_201
        req.context['result'] = {'backup_id': backup_id}


class BackupsResource(object):
    """
    Handler for endpoint: /v1/backups/{backup_id}
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    def on_get(self, req, resp, backup_id):
        # GET /v1/backups/{backup_id}     Get backup details
        user_id = req.get_header('X-User-ID')
        obj = self.db.get_backup(user_id=user_id, backup_id=backup_id)
        req.context['result'] = obj

    def on_delete(self, req, resp, backup_id):
        # DELETE /v1/backups/{backup_id}     Deletes the specified backup
        user_id = req.get_header('X-User-ID')
        self.db.delete_backup(
            user_id=user_id, backup_id=backup_id)
        req.context['result'] = {'backup_id': backup_id}
        resp.status = falcon.HTTP_204
