from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Campos que ya tenías para Logística
    x_moneda_costo = fields.Selection([('mxn', 'MXN'), ('usd', 'USD')], string='Moneda de Costo', default='usd')
    x_extra_costo = fields.Float(string='Costo Real', default=0.0)
    
    # Nuevo Selector para elegir la fórmula
    x_marca_producto = fields.Selection([
        ('logistica', 'Logística (Normal)'),
        ('abisai', 'Abisai (Fórmula Especial)')
    ], string='Lógica de Costo', default='logistica')