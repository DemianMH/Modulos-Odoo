{
    'name': 'Grupo Dealer - Sistema de Cotización Inteligente',
    'version': '18.0.2.0.0',
    'category': 'Sales/CRM',
    'summary': 'Mueve el cotizador dinámico a las líneas de venta en Odoo 18',
    'description': """
        Módulo avanzado para Grupo Dealer.
        - Clientes: Datos de paquetería y condiciones de crédito.
        - Productos: Conserva únicamente los costos base y atributos en USD.
        - Ventas: Incorpora la calculadora matemática en vivo por línea de cotización.
    """,
    'author': 'Grupo Dealer',
    'depends': ['base', 'sale', 'contacts', 'product'], 
    'data': [
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}