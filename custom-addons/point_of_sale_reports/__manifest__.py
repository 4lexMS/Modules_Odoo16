# my_custom_module/__manifest__.py
{
    'name': 'Informe de punto de venta',
    'version': '1.0',
    'summary': 'Reportes de Puntos de ventas',
    'description': 'Este módulo imprime reportes de arqueo de caja y egreso o ingreso de caja.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale', 'stock', ],
    'data': [
        'wizard/arqueo_cajas.xml',
        'wizard/egreso_caja.xml',
        'views/action_report.xml',
        'report/reporte_arqueo.xml',
        'report/reporte_egreso.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
