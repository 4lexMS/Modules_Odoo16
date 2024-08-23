from odoo import models, fields, api
import xlsxwriter
import base64
from io import BytesIO

class ProductListSale(models.Model):
    _inherit = 'product.pricelist'

    def action_button_list_sale(self):
        product_ids = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.id)]).mapped('product_tmpl_id').ids
        ctx = dict(self.env.context or {}, active_ids=product_ids)
        view = self.env.ref('product_report_prices.view_product_price_report_wizard', False)

        return {
            'name': 'Listar precios Ventas',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'product.price.report.wizard',
            'target': 'new',
            'context': ctx,
        }

class ProductListTrans(models.Model):
    _inherit = 'stock.picking'

    def action_button_list_trans(self):
        product_ids = self.env['stock.move'].search([('picking_id', '=', self.id)]).mapped('product_tmpl_id').ids
        ctx = dict(self.env.context or {}, active_ids=product_ids)
        view = self.env.ref('product_report_prices.view_product_price_report_wizard', False)
        return {
            'name': 'Listar precios Transferencia',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'product.price.report.wizard',
            'target': 'new',
            'context': ctx,
        }

class ProductPriceReportWizard(models.TransientModel):
    _name = 'product.price.report.wizard'
    _description = 'Reporte de Precios de Productos'

    report_type = fields.Selection([
        ('type1', 'Etiqueta precios'),
        ('type2', 'Reporte Lista Precios'),
        ('type3', 'Recepción Transferencia'),
    ], string='Tipo de reporte', required=True)

    def generate_report(self):
        products = self.env['product.template'].browse(self.env.context.get('active_ids', []))
        if self.report_type == "type1":
            return self.action_generate_xlsx_report1(products)
        elif self.report_type == "type2":
            return self.action_generate_xlsx_report2(products)
        else:
            return self.action_generate_xlsx_report3(products)

    def action_generate_xlsx_report1(self, products):
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
            worksheet.write(row, 1, product.barcode if product.barcode else "", text_products)
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
    def action_generate_xlsx_report2(self, products):
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
            worksheet.write(row, 1, product.barcode if product.barcode else "", text_products)
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
    def action_generate_xlsx_report3(self, products):
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
            worksheet.write(row, 1, product.barcode if product.barcode else "", text_products)
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
