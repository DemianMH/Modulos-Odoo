from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Campos base
    x_moneda_costo = fields.Selection([
        ('mxn', 'Pesos (MXN)'),
        ('usd', 'Dólares (USD)')
    ], string='Moneda de Costo', default='mxn')
    
    x_extra_costo = fields.Float(string='Costo Extra (Placas, Etiquetas, etc.)', digits=(16, 2))
    
    # Campo que da el error
    x_tipo_articulo = fields.Selection([
        ('llanta', 'Llanta / Rueda Industrial'),
        ('bolsa', 'Bolsa'),
        ('cartera', 'Cartera'),
        ('mochila', 'Mochila'),
        ('messenger', 'Messenger'),
        ('otros', 'Otros')
    ], string='Tipo de Artículo', default='otros')