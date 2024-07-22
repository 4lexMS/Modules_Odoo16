# my_custom_module/__manifest__.py
{
    'name': 'Etiquetas del producto',
    'version': '1.0',
    'summary': 'Personalizar etiquetas de productos',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base',  'stock',],
    'data': [
        'report/reporte1.xml',
        'views/action_reporte1.xml',
    ],
    'installable': True,
    'application': True,
}
