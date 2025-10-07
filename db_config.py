class DatabaseConfig:
    # 数据库配置
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',  # 请修改为你的数据库密码
        'database': 'student_management_system'
    }

    @staticmethod
    def get_config():
        """获取数据库配置"""
        return DatabaseConfig.config

    @staticmethod
    def update_config(host=None, user=None, password=None, database=None):
        """更新数据库配置"""
        if host:
            DatabaseConfig.config['host'] = host
        if user:
            DatabaseConfig.config['user'] = user
        if password:
            DatabaseConfig.config['password'] = password
        if database:
            DatabaseConfig.config['database'] = database 