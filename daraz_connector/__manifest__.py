# -*- coding: utf-8 -*-
{
    'name': "Daraz Connector",

    'summary': """
        Daraz Api connector that integrate the inventory and sale orders
        Module can sync date between odoo and Daraz Store""",

    'description': """
        Daraz Connector
    """,

    'author': "Hunain",
    'website': "http://www.telenoc.org",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
