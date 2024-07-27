# my_custom_module/__manifest__.py
{
    'name': 'Informe de punto de venta',
    'version': '1.0',
    'summary': 'Reportes de Puntos de ventas',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale',],
    'data': [
        'views/consolidacion_cajas.xml',
        'views/egreso_caja.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
