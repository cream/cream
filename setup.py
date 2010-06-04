from cream.dist import setup

setup(
    name = 'Melange Widgets',
    version = '0.0.8',
    data_files = [
        ('share/cream/modules/melange/widgets', ['src/*'])
        ]
    )
