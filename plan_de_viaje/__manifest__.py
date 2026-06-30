{
    'name': 'Plan de Viaje Corporativo',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Gestión, control y auditoría de planes de viaje corporativos',
    'description': """
        Módulo robusto para gestionar planes de viaje de los ejecutivos.
        Permite trazar rutas, auditar cambios, solicitar aprobaciones de dirección
        y gestionar estrategias o activaciones en un entorno multiempresa.
    """,
    'author': 'Tu Empresa',
    'depends': ['base', 'mail', 'contacts', 'loyalty'], # Agregamos loyalty aquí
    'data': [
        'security/plan_viaje_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/plan_viaje_views.xml',
        'views/menu_views.xml',
        'views/plan_viaje_report.xml',
        'views/report_plan_viaje_template.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}