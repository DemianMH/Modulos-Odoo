{
    'name': 'Reporte de Gastos Dealer',
    'version': '1.0',
    'summary': 'Visualización e Impresión en PDF de Gastos Dealer',
    'description': 'Módulo para mostrar los gastos reales en listas y permitir la descarga del PDF ejecutivo (Top 15 y Distribución por Pestaña).',
    'category': 'Human Resources/Expenses',
    'depends': ['hr_expense'],
    'data': [
        'views/expenses_report_views.xml',
        'views/expenses_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}