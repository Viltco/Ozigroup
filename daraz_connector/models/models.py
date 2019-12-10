# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import datetime ,timezone
import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC
import json


class darazCategory(models.Model):
    _inherit = "product.category"

    leaf=fields.Boolean("Leaf",default=False)
    darazCategoryId=fields.Integer("Daraz Category ID")
    darazStoreId=fields.One2many('daraz.connector','id',string="Daraz Store")


class syncDarazCategories(models.TransientModel):
    _name = "sync.darazcategories"
    _description = "Sync Daraz Store Categories"

    darazStoreId = fields.Many2one('daraz.connector', 'Daraz Store')

    def doConnection(self,action=None,req=None):
        darazStore = self.env['daraz.connector'].browse(self.darazStoreId.id)
        url = darazStore.api_url
        key = darazStore.api_key
        action =action if action else "GetCategoryTree"
        format = "json"
        userId = darazStore.userId
        method=req if req  else 'GET'

        now = datetime.now().timestamp()
        test = datetime.fromtimestamp(now, tz=timezone.utc).replace(microsecond=0).isoformat()
        parameters = {
            'UserID': userId,
            'Version': "1.0",
            'Action':action,
            'Format': format,
            'Timestamp': test}

        concatenated = urllib.parse.urlencode(sorted(parameters.items()))
        data = concatenated.encode('utf-8')
        parameters['Signature'] = HMAC(key.encode('utf-8'), data,
                                       sha256).hexdigest()


        headers = {
            'Content-Type': "application/json",
            'Accept': "*/*",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        try:
            response = requests.request(method, url, headers=headers, params=parameters)
        except Exception as e:


            raise Warning(_(response.text))



        return json.loads(response.text)

    def createCategory(self,record,recModel,parent=None):
        print(recModel,parent,record)
        name=record.get("name")
        categoryId=record.get("categoryId")
        leaf=record.get("leaf")
        if parent is not None:
            category = recModel.create({"name": name, "darazCategoryId": categoryId, "leaf": leaf,"parent_id":parent})
        else:
            category = recModel.create({"name": name, "darazCategoryId": categoryId, "leaf": leaf})
        return category.id

    def rec(self,data, parent=None):
        productCategory = self.env['product.category']
        for record in data:
            if record.get('leaf') == False:
                parent_id = self.createCategory(record,productCategory,parent)

                self.rec(record.get('children'), parent_id)
            else:
                self.createCategory(record,productCategory)
        return True
    def getCategories(self):
        # productCategory = self.env['product.category']
        # category = productCategory.create({"name": "name"})
        # print(category.id)
        res=self.doConnection('GetCategoryTree','GET')
        result=self.rec(res.get('SuccessResponse').get('Body'))
        if result==True:
            print("Successfully Imported Categories")
        # for record in res.get('SuccessResponse').get('Body'):
        #     categoryId=record.get('categoryId')
        #     leaf=record.get('leaf')
        #     name=record.get('name')
        #     category=productCategory.create({"name":name,"darazCategoryId":categoryId,"leaf":leaf})
        #     print(category.id)
        #     for child in record.get("children"):
        #         pass


