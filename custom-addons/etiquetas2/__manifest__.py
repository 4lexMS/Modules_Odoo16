# my_custom_module/__manifest__.py
{
    'name': 'etiquetas2',
    'version': '1.0',
    'summary': 'Personalizar etiquetas de productos',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'product',],
    'data': [
        'views1/reportePrueba.xml',
        'views1/product_form_views.xml',
        'security1/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
