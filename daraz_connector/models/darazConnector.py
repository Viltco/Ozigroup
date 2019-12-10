from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import datetime ,timezone
import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC

class DarazConnector(models.Model):
    _name = "daraz.connector"
    _description = "Daraz Connector"

    name=fields.Char("Store Name", index=True, required=True)
    api_url=fields.Char("Api Url",required=True)
    userId=fields.Char("User ID",required=True)
    api_key=fields.Char("Api Key",required=True)
    state=fields.Selection([("draft",'Draft'),("connected",'Connected')],default='draft')

    def doConnection(self,action=None,req=None):
        url = self.api_url
        key = self.api_key
        action =action if action else "GetBrands"
        format = "json"
        userId = self.userId
        method=req if req  else 'GET'
        self.state='connected'
        super(DarazConnector, self).write({"state":"connected"})
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
        print(parameters)

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept': "*/*",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        try:
            response = requests.request(method, url, headers=headers, params=parameters)
        except Exception as e:
            self.state = 'draft'
            super(DarazConnector, self).write({"state": "draft"})
            raise Warning(_(response.text))

        if response.status_code==200:
            self.state = 'connected'
            super(DarazConnector, self).write({"state": "connected"})
            raise  Warning(
                _("Successfully Connected"))
            #raise Warning(_("Successfully Connected"))
        return response.text