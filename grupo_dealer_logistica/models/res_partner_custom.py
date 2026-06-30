from odoo import models, fields

class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'

    x_paqueteria_id = fields.Char(string='Paquetería Preferida')
    x_pago_paqueteria = fields.Selection([
        ('cliente', 'Cliente Paga'),
        ('nosotros', 'Nosotros Pagamos'),
        ('no_aplica', 'No Aplica')
    ], string='¿Quién paga la paquetería?', default='cliente')
    
    x_condicion_entrega = fields.Selection([
        ('domicilio', 'Entrega a Domicilio'),
        ('ocurre', 'Ocurre (En sucursal)'),
        ('recolectan', 'Recolectan en nuestras oficinas')
    ], string='Condición de Entrega')
    
    x_etiquetado_especial = fields.Char(string='Instrucciones de Etiquetado')
    x_plazo_pago_dias = fields.Integer(string='Plazo de Pago Autorizado (Días)')

    
    