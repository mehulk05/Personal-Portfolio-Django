from split_settings.tools import include


settings = []

base_settings = [
    'components/common.py',
    'components/database_development.py',
]
settings.extend(base_settings)
include(*settings)
