from odoo import models, fields, api
from odoo.exceptions import UserError
import xlsxwriter
import base64
from io import BytesIO

class ProductPriceReportWizard(models.TransientModel):
    _name = 'product.price.report.wizard'
    _description = 'Product Price Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection([
        ('type1', 'Etiqueta precios'),
        ('type2', 'Reporte Lista Precios'),
        ('type3', 'Recepción Transferencia'),
    ], string='Report Type', required=True)

    product_ids = fields.Char(string='Product IDs', readonly=True)

    def default_get(self, fields):
        res = super(ProductPriceReportWizard, self).default_get(fields)
        res['product_ids'] = ','.join(map(str, self.env.context.get('active_ids', [])))
        return res

    def generate_report(self):
        self.ensure_one()  # Asegurarse de que solo hay un registro en el wizard
        if self.report_type == "type1":
            return self.action_generate_xlsx_report1()
        elif self.report_type == "type2":
            return self.action_generate_xlsx_report2()
        else:
            return self.action_generate_xlsx_report3()

    def action_generate_xlsx_report1(self):
        # Crear un archivo XLSX en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')

        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 14,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True
            })

        worksheet.set_row(0, 20.5)
        worksheet.set_row(9, 20.5)
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 16)

        worksheet.set_column('F:N', 2)
        worksheet.set_column('C:D', 2.4)
        worksheet.set_column('E:E', 37)

        for row_buc in range(1, 9):
            worksheet.set_row(row_buc, 12)

        worksheet.merge_range('B1:O1', 'Listado de Precio', title_format)

        # Definir los encabezados
        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })
        title_price = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })

        headers = ['Código', 'Descripción', 'Nivel 2']
        worksheet.write('B10', headers[0], title_header)
        worksheet.write('E10', headers[1], title_header)
        worksheet.write('O10', headers[2], title_price)
        # Obtener datos de productos

        products = self.env['product.template'].browse(map(int, self.product_ids.split(',')))

        row = 10

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        for product in products:
            worksheet.set_row(row, 20)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 1, product.default_code, text_products)
            worksheet.write(row, 4, product.name, text_products)
            worksheet.write(row, 14, product.list_price, text_products)
            row += 1

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'FORMATO PARA ETIQUETA PRECIOS.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
    def action_generate_xlsx_report2(self):
        # Crear un archivo XLSX en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')

        worksheet.set_row(0, 16.9)
        worksheet.set_row(1, 16.9)
        worksheet.set_row(2, 21.5)
        worksheet.set_row(9, 20.8)
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 14)

        worksheet.set_column('F:N', 1.8)
        worksheet.set_column('C:C', 4.8)
        worksheet.set_column('D:D', 3)
        worksheet.set_column('E:E', 38)

        for row_buc in range(3, 8):
            worksheet.set_row(row_buc, 12)

        # Definir los encabezados
        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 8,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })
        title_price = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 8,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })

        worksheet.write('C10', "", title_header)
        worksheet.write('D10', "", title_header)
        worksheet.write('F10', "", title_header)
        worksheet.write('I10', "", title_header)
        worksheet.write('J10', "", title_header)
        worksheet.write('K10', "", title_header)
        worksheet.write('L10', "", title_header)

        headers = ['Código', 'Descripción', 'Nivel 2']
        worksheet.write('B10', headers[0], title_header)
        worksheet.write('E10', headers[1], title_header)
        worksheet.write('O10', headers[2], title_price)

        # Obtener datos de productos
        products = self.env['product.template'].browse(map(int, self.product_ids.split(',')))
        row = 10

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })
        text_price = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        for product in products:
            worksheet.set_row(row, 20)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 1, product.default_code, text_products)
            worksheet.write(row, 4, product.name, text_products)
            worksheet.write(row, 14, product.list_price, text_price)
            row += 1

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'FORMATO PARA ETIQUETA PRECIOS DESDE REPORTE LISTA DE PRECIOS.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
    def action_generate_xlsx_report3(self):
        # Crear un archivo XLSX en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')

        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 14,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True
            })

        worksheet.set_row(0, 20.5)
        worksheet.set_row(9, 20.5)
        worksheet.set_column('A:A', 4.5)
        worksheet.set_column('B:B', 16.9)

        worksheet.set_column('F:N', 1.8)
        worksheet.set_column('C:D', 2.7)
        worksheet.set_column('E:E', 37)

        for row_buc in range(1, 9):
            worksheet.set_row(row_buc, 12)

        worksheet.merge_range('B1:O1', 'Listado de Precio', title_format)

        # Definir los encabezados
        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })
        title_price = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1
            })

        headers = ['Código', 'Descripción', 'Nivel 2']
        worksheet.write('B10', headers[0], title_header)
        worksheet.write('E10', headers[1], title_header)
        worksheet.write('O10', headers[2], title_price)
        # Obtener datos de productos
        products = self.env['product.template'].browse(map(int, self.product_ids.split(',')))
        row = 10

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        for product in products:
            worksheet.set_row(row, 20)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 1, product.default_code, text_products)
            worksheet.write(row, 4, product.name, text_products)
            worksheet.write(row, 14, product.list_price, text_products)
            row += 1

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'FORMATO PARA ETIQUETA PRECIOS DESDE RECEPCION DE TRANSFERENCIAS.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
